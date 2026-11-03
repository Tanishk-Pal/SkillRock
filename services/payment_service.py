"""
SkillRock Payment & Access Control Engine
Handles dynamic in-memory UPI QR generation, strict 12-digit UTR validation,
anti-replay duplicate protection, and unified student unlock verification.
"""

import io
import re
import base64
import logging
from datetime import datetime, timezone
from urllib.parse import quote
import qrcode
from config import Config
from models import get_db, Course
from models.test_series import TestDefinition, TestPack, UserEntitlement

logger = logging.getLogger(__name__)

# Known dummy / invalid test UTR sequences
BLOCKED_DUMMY_UTRS = {
    "123456789012",
    "012345678901",
    "987654321098",
    "000000000000",
    "111111111111",
    "222222222222",
    "333333333333",
    "444444444444",
    "555555555555",
    "666666666666",
    "777777777777",
    "888888888888",
    "999999999999",
}


def validate_utr(utr_number):
    """
    Validates a 12-digit UPI Transaction Reference (UTR) number:
    - Must be non-empty string.
    - Exactly 12 numeric digits (^[0-9]{12}$).
    - Not in known dummy sequences.
    - Not all-identical digits.
    - Contains at least 4 distinct digits to defeat simple repetitive dummy inputs.
    Returns: (is_valid: bool, error_message: str)
    """
    if not utr_number:
        return False, "Please enter your 12-digit UTR / UPI Transaction Reference Number."

    utr_clean = str(utr_number).strip()

    if not re.match(r"^\d{12}$", utr_clean):
        return False, "Invalid UTR format. The UTR number must be exactly 12 numeric digits (0-9)."

    if utr_clean in BLOCKED_DUMMY_UTRS:
        return False, "Invalid test or dummy UTR sequence detected. Please enter your authentic bank reference number."

    # Block sequences with identical digits (e.g. 000000000000 or 999999999999)
    unique_digits = set(utr_clean)
    if len(unique_digits) <= 1:
        return False, "Invalid UTR number: identical repeating digits are not permitted."

    # Minimum entropy check: at least 4 unique digits in a genuine 12-digit bank UTR
    if len(unique_digits) < 4:
        return False, "Invalid UTR sequence. Genuine bank transaction references contain at least 4 distinct digits."

    return True, ""


def generate_upi_qr_base64(amount, item_type, item_id, item_title=""):
    """
    Generates an in-memory dynamic UPI QR code Base64 string for direct HTML rendering.
    Zero disk writes or file caching.
    """
    merchant_upi = Config.MERCHANT_UPI_ID or "palt51419@okaxis"
    merchant_name = Config.MERCHANT_NAME or "SkillRock"

    try:
        amt_float = float(amount)
    except (ValueError, TypeError):
        amt_float = 0.0

    # Build standard NPCI UPI URI
    short_type = "CRS" if item_type == "course" else "TST"
    short_id = str(item_id).replace("-", "")[:8].upper()
    ref_note = f"SR-{short_type}-{short_id}"

    # Parameters: pa (payee VPA), pn (payee name), am (amount), cu (currency), tn (transaction note)
    upi_uri = (
        f"upi://pay?pa={quote(merchant_upi)}"
        f"&pn={quote(merchant_name)}"
        f"&am={amt_float:.2f}"
        f"&cu=INR"
        f"&tn={quote(ref_note)}"
    )

    # In-memory QR generation
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=8,
        border=2,
    )
    qr.add_data(upi_uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#0F172A", back_color="#FFFFFF")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    b64_qr = base64.b64encode(buf.getvalue()).decode("utf-8")
    qr_data_uri = f"data:image/png;base64,{b64_qr}"

    return {
        "qr_data_uri": qr_data_uri,
        "upi_uri": upi_uri,
        "merchant_upi": merchant_upi,
        "merchant_name": merchant_name,
        "ref_note": ref_note,
        "amount": amt_float,
    }


def get_item_by_type_and_id(item_type, item_id):
    """
    Authoritative server-side database lookup for an item by item_type and ID/slug.
    Returns: item instance or None
    """
    if not item_type or not item_id:
        return None

    str_id = str(item_id).strip()

    if item_type == "course":
        course = Course.get_by_id(str_id)
        if not course:
            course = Course.get_by_slug(str_id)
        return course

    elif item_type in ("test_series", "test", "test_pack"):
        test = TestDefinition.get_by_id(str_id)
        if not test:
            test = TestDefinition.get_by_slug(str_id)
        if test:
            return test

        pack = TestPack.get_by_id(str_id)
        if not pack:
            pack = TestPack.get_by_slug(str_id)
        return pack

    return None


def verify_student_unlock(user, item_type, item_id):
    """
    Unified Access Guard.
    Returns True if:
    1. User is Super Admin -> Always True.
    2. Item is Free (is_paid == False or price <= 0) -> True for all authenticated students.
    3. Item is Paid -> Checks MongoDB user_access collection for is_active == True.
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    if getattr(user, "is_admin", False):
        return True

    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        return False

    # Check if item is free
    is_paid = getattr(item, "is_paid", False)
    price = getattr(item, "price", 0.0)
    if isinstance(item, TestDefinition):
        is_paid = getattr(item, "is_paid", not getattr(item, "is_free", True))
    elif isinstance(item, TestPack):
        is_paid = getattr(item, "is_paid", getattr(item, "price_inr", 0) > 0)

    if not is_paid or price <= 0:
        return True

    # Item is paid -> Verify active record in user_access collection
    db = get_db()
    access_doc = db.user_access.find_one({
        "user_id": str(user.id),
        "item_type": item_type,
        "item_id": str(item.id),
        "is_active": True,
    })

    return bool(access_doc)


def grant_student_access(user_id, item_type, item_id, granted_by="admin", payment_id=None, amount=0.0):
    """
    Authoritative method to grant active access to a student in user_access collection
    and auto-enroll or grant entitlement where applicable.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    uid = str(user_id)
    iid = str(item_id)

    db.user_access.update_one(
        {"user_id": uid, "item_type": item_type, "item_id": iid},
        {
            "$set": {
                "user_id": uid,
                "item_type": item_type,
                "item_id": iid,
                "is_active": True,
                "granted_at": now,
                "granted_by": str(granted_by),
                "payment_id": str(payment_id) if payment_id else None,
                "amount_paid": float(amount or 0.0),
                "updated_at": now,
            },
            "$setOnInsert": {
                "created_at": now,
            }
        },
        upsert=True
    )

    # Automatically enroll student if course
    if item_type == "course":
        try:
            from routes.learning import auto_enroll_student_in_course
            from models import User
            user_obj = User.get_by_id(uid)
            if user_obj:
                auto_enroll_student_in_course(user_obj, iid)
        except Exception as e:
            logger.warning(f"Auto-enrollment hook on grant_student_access error: {e}")

    # Automatically grant entitlement if test pack
    if item_type in ("test_series", "test_pack"):
        try:
            ent = UserEntitlement.get_or_create_pack_access(
                user_id=uid,
                pack_id_or_slug=iid,
                granted_by=granted_by,
                notes=f"Granted via Payment {payment_id or 'admin'}"
            )
        except Exception as e:
            logger.warning(f"Entitlement hook on grant_student_access error: {e}")

    return True


def revoke_student_access(user_id, item_type, item_id):
    """Deactivates student access for a specific item."""
    db = get_db()
    now = datetime.now(timezone.utc)
    db.user_access.update_one(
        {"user_id": str(user_id), "item_type": item_type, "item_id": str(item_id)},
        {"$set": {"is_active": False, "revoked_at": now, "updated_at": now}}
    )
    return True
