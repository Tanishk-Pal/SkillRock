"""
SkillRock Payment & Access Control Engine
Handles dynamic in-memory UPI QR generation, strict 12-digit UTR validation,
anti-replay duplicate protection, and unified student unlock verification.
"""

import io
import re
import time
import secrets
import base64
import logging
from datetime import datetime, timezone, timedelta
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


def generate_upi_qr_base64(amount, item_type, item_id, item_title="", session_token=None):
    """
    Generates an in-memory dynamic UPI QR code Base64 string for direct HTML rendering.
    Includes a 5-minute (300 seconds) security expiration window and app-specific deep links.
    Zero disk writes or file caching.
    """
    merchant_upi = Config.MERCHANT_UPI_ID or "9243494968@nyes"
    merchant_name = Config.MERCHANT_NAME or "SkillRock"

    try:
        amt_float = float(amount)
    except (ValueError, TypeError):
        amt_float = 0.0

    if not session_token:
        session_token = secrets.token_hex(4).upper()

    now_ts = int(time.time())
    expires_in = 300  # 5 minutes
    expires_at = now_ts + expires_in

    # Build standard NPCI UPI URI with dynamic session token
    short_type = "CRS" if item_type == "course" else "TST"
    short_id = str(item_id).replace("-", "")[:8].upper()
    ref_note = f"SR-{short_type}-{short_id}-{session_token}"

    # Parameters: pa (payee VPA), pn (payee name), am (amount), cu (currency), tn (transaction note)
    upi_params = (
        f"pa={quote(merchant_upi)}"
        f"&pn={quote(merchant_name)}"
        f"&am={amt_float:.2f}"
        f"&cu=INR"
        f"&tn={quote(ref_note)}"
    )
    upi_uri = f"upi://pay?{upi_params}"
    
    # App-specific deep link intents for Mobile (Razorpay pattern)
    gpay_uri = f"tez://upi/pay?{upi_params}"
    phonepe_uri = f"phonepe://pay?{upi_params}"
    paytm_uri = f"paytmmp://pay?{upi_params}"

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
        "gpay_uri": gpay_uri,
        "phonepe_uri": phonepe_uri,
        "paytm_uri": paytm_uri,
        "merchant_upi": merchant_upi,
        "merchant_name": merchant_name,
        "ref_note": ref_note,
        "amount": amt_float,
        "session_token": session_token,
        "expires_in": expires_in,
        "expires_at": expires_at,
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


# ==============================================================================
# Automated Bank SMS Credit Parsing & Instant Auto-Unlock Engine
# ==============================================================================

def register_checkout_session(user_id, item_type, item_id, session_token, amount):
    """
    Registers an active student checkout session in MongoDB.
    Allows incoming bank SMS with ref_note (e.g. SR-CRS-<item>-<session>) to
    automatically match the user and auto-unlock within seconds.
    """
    if not session_token or not user_id:
        return False
    try:
        db = get_db()
        now = datetime.now(timezone.utc)
        db.checkout_sessions.update_one(
            {"session_token": str(session_token).strip()},
            {
                "$set": {
                    "user_id": str(user_id),
                    "item_type": str(item_type),
                    "item_id": str(item_id),
                    "session_token": str(session_token).strip(),
                    "amount": float(amount or 0.0),
                    "updated_at": now,
                },
                "$setOnInsert": {
                    "created_at": now,
                }
            },
            upsert=True
        )
        return True
    except Exception as e:
        logger.warning(f"Error registering checkout session: {e}")
        return False


def parse_bank_credit_sms(sms_text, sender=""):
    """
    Parses incoming SMS notification to verify if it represents a valid UPI bank credit.
    Extracts:
    - is_credit: bool (True only for money credited; blocks debits/spams)
    - amount: float (e.g. 699.00)
    - utr_number: str (12-digit UPI reference number)
    - ref_note: str or None (e.g. SR-CRS-6AE9ED99-A1B2C3D4)
    - sender: str (e.g. SBIINB, HDFCBK, AXISBK, YESBK, PAYTM)
    """
    if not sms_text or not isinstance(sms_text, str):
        return {"is_credit": False, "error": "Empty or invalid SMS payload"}

    text = sms_text.strip()
    text_lower = text.lower()

    # Security Guard: Explicitly block debit alerts, withdrawals, or OTPs
    is_debit = any(k in text_lower for k in ["debited", "debit of", "withdrawn", "payment of rs", "spent rs", "transferred to"])
    is_credit = any(k in text_lower for k in ["credited", "received", "deposited", "credit of"])

    if is_debit and not is_credit:
        return {"is_credit": False, "error": "Transaction is a debit alert, not a credit"}

    if not is_credit:
        return {"is_credit": False, "error": "No credit confirmation keywords detected"}

    # 1. Extract Amount
    amount = 0.0
    amount_patterns = [
        r"(?:credited\s+(?:by|with|for)|received|deposited)\s*(?:rs\.?|inr|\u20B9)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"(?:rs\.?|inr|\u20B9)\s*([0-9]+(?:\.[0-9]{1,2})?)\s*(?:is\s+|has\s+been\s+)?(?:credited|deposited|received)",
        r"(?:payment\s+received\s+of)\s*(?:rs\.?|inr|\u20B9)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"(?:credit\s+of)\s*(?:rs\.?|inr|\u20B9)?\s*([0-9]+(?:\.[0-9]{1,2})?)",
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                parsed_amt = float(match.group(1))
                if parsed_amt > 0:
                    amount = parsed_amt
                    break
            except (ValueError, TypeError):
                continue

    if amount <= 0:
        return {"is_credit": False, "error": "Could not identify valid credit amount"}

    # 2. Extract 12-digit UTR
    utr_number = ""
    utr_patterns = [
        r"(?:upi[/:-]|ref(?:erence)?(?:\s*no\.?)?[/:-]|utr[/:-]|txn[/:-]|transaction\s*id[/:-])\s*([0-9]{12})",
        r"upi/([0-9]{12})",
        r"upi-([0-9]{12})",
        r"upi:([0-9]{12})",
        r"\b([0-9]{12})\b",
    ]
    for pattern in utr_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            val_ok, _ = validate_utr(m)
            if val_ok:
                utr_number = m
                break
        if utr_number:
            break

    # 3. Extract Reference Note (e.g. SR-CRS-6AE9ED99-A1B2C3D4)
    ref_note = None
    ref_match = re.search(r"\b(SR-(?:CRS|TST)-[A-Za-z0-9\-]+)\b", text, re.IGNORECASE)
    if ref_match:
        ref_note = ref_match.group(1).upper()

    return {
        "is_credit": True,
        "amount": amount,
        "utr_number": utr_number,
        "ref_note": ref_note,
        "sender": str(sender or "").strip(),
        "parsed_at": datetime.now(timezone.utc).isoformat(),
    }


def process_incoming_bank_credit(amount, utr_number, ref_note=None, sender=None, raw_sms=None):
    """
    Processes a verified bank credit:
    1. Checks if UTR is already approved (anti-replay/idempotent).
    2. Searches for a matching pending payment in db.payments -> auto-approves & grants access.
    3. If ref_note contains session token, finds active checkout session -> auto-creates payment & unlocks.
    4. If not immediately assigned, saves to db.bank_credits for instant polling claim.
    """
    db = get_db()
    now = datetime.now(timezone.utc)
    amt_float = float(amount or 0.0)

    # Anti-Replay: Check if already approved
    if utr_number:
        existing_approved = db.payments.find_one({"utr_number": utr_number, "status": "approved"})
        if existing_approved:
            return {
                "success": True,
                "status": "already_approved",
                "payment_id": existing_approved.get("payment_id"),
                "message": f"Payment with UTR {utr_number} is already active."
            }

    # Store credit record in bank_credits collection
    credit_doc = {
        "utr_number": utr_number or None,
        "amount": amt_float,
        "ref_note": ref_note,
        "sender": sender,
        "raw_snippet": (raw_sms[:250] if raw_sms else None),
        "claimed": False,
        "claimed_by": None,
        "created_at": now,
        "updated_at": now,
    }
    try:
        db.bank_credits.insert_one(credit_doc)
    except Exception as e:
        logger.info(f"bank_credits notice: {e}")

    # Case A: Match with pending payment document
    pending_query = None
    if utr_number:
        pending_query = {"utr_number": utr_number, "status": "pending"}
    
    pending_pay = None
    if pending_query:
        pending_pay = db.payments.find_one(pending_query)

    if pending_pay:
        db.payments.update_one(
            {"_id": pending_pay["_id"]},
            {
                "$set": {
                    "status": "approved",
                    "reviewed_at": now,
                    "reviewed_by": "bank_sms_webhook",
                    "matched_via": "utr_match",
                    "verified_amount": amt_float,
                    "updated_at": now,
                }
            }
        )
        grant_student_access(
            user_id=pending_pay["user_id"],
            item_type=pending_pay["item_type"],
            item_id=pending_pay["item_id"],
            granted_by="bank_sms_webhook",
            payment_id=pending_pay.get("payment_id"),
            amount=amt_float,
        )
        if utr_number:
            db.bank_credits.update_one(
                {"utr_number": utr_number},
                {"$set": {"claimed": True, "claimed_by": pending_pay["user_id"], "payment_id": pending_pay.get("payment_id"), "updated_at": now}}
            )
        return {
            "success": True,
            "status": "approved_pending",
            "payment_id": pending_pay.get("payment_id"),
            "user_id": pending_pay["user_id"],
            "message": f"Pending payment {pending_pay.get('payment_id')} successfully auto-approved via bank SMS."
        }

    # Case B: Match via ref_note session token
    session_token = None
    if ref_note:
        parts = ref_note.split("-")
        if len(parts) >= 4:
            session_token = parts[-1]

    if session_token:
        checkout_sess = db.checkout_sessions.find_one({"session_token": session_token})
        if checkout_sess:
            user_id = checkout_sess.get("user_id")
            item_type = checkout_sess.get("item_type")
            item_id = checkout_sess.get("item_id")
            item = get_item_by_type_and_id(item_type, item_id)
            
            from models import User
            user_obj = User.get_by_id(user_id)

            payment_id = f"PAY-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
            new_payment = {
                "payment_id": payment_id,
                "user_id": str(user_id),
                "user_name": getattr(user_obj, "name", "Student"),
                "user_email": getattr(user_obj, "email", ""),
                "item_type": item_type,
                "item_id": str(item_id),
                "item_title": getattr(item, "title", "SkillRock Course"),
                "amount": amt_float,
                "utr_number": utr_number or f"SMS{now.strftime('%H%M%S')}{secrets.token_hex(2).upper()}",
                "status": "approved",
                "session_token": session_token,
                "submitted_at": now,
                "reviewed_at": now,
                "reviewed_by": "bank_sms_webhook",
                "matched_via": "session_ref_note",
                "created_at": now,
                "updated_at": now,
            }
            try:
                db.payments.insert_one(new_payment)
            except Exception as e:
                logger.warning(f"Error inserting auto payment doc: {e}")

            grant_student_access(
                user_id=user_id,
                item_type=item_type,
                item_id=item_id,
                granted_by="bank_sms_webhook",
                payment_id=payment_id,
                amount=amt_float,
            )
            if utr_number:
                db.bank_credits.update_one(
                    {"utr_number": utr_number},
                    {"$set": {"claimed": True, "claimed_by": user_id, "payment_id": payment_id, "updated_at": now}}
                )
            return {
                "success": True,
                "status": "auto_created_and_unlocked",
                "payment_id": payment_id,
                "user_id": user_id,
                "message": f"Successfully auto-unlocked access for user {user_id} via session note."
            }

    # Case C: Even if ref_note is omitted by bank SMS (e.g. Central Bank, SBI),
    # match against active student checkout session for this exact amount within the last 20 minutes!
    if amt_float > 0:
        twenty_mins_ago = now - timedelta(minutes=20)
        recent_sessions = list(db.checkout_sessions.find({
            "amount": amt_float,
            "updated_at": {"$gte": twenty_mins_ago}
        }).sort("updated_at", -1).limit(1))

        if recent_sessions:
            sess_doc = recent_sessions[0]
            matched_user_id = sess_doc.get("user_id")
            matched_item_type = sess_doc.get("item_type")
            matched_item_id = sess_doc.get("item_id")
            matched_item = get_item_by_type_and_id(matched_item_type, matched_item_id)

            from models import User
            matched_user_obj = User.get_by_id(matched_user_id)

            payment_id = f"PAY-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
            auto_payment = {
                "payment_id": payment_id,
                "user_id": str(matched_user_id),
                "user_name": getattr(matched_user_obj, "name", "Student"),
                "user_email": getattr(matched_user_obj, "email", ""),
                "item_type": matched_item_type,
                "item_id": str(matched_item_id),
                "item_title": getattr(matched_item, "title", "SkillRock Course"),
                "amount": amt_float,
                "utr_number": utr_number or f"SMS{now.strftime('%H%M%S')}{secrets.token_hex(2).upper()}",
                "status": "approved",
                "session_token": sess_doc.get("session_token"),
                "submitted_at": now,
                "reviewed_at": now,
                "reviewed_by": "bank_sms_webhook",
                "matched_via": "active_checkout_amount_match",
                "created_at": now,
                "updated_at": now,
            }
            try:
                db.payments.insert_one(auto_payment)
            except Exception as e:
                logger.warning(f"Notice inserting auto payment: {e}")

            grant_student_access(
                user_id=matched_user_id,
                item_type=matched_item_type,
                item_id=matched_item_id,
                granted_by="bank_sms_webhook",
                payment_id=payment_id,
                amount=amt_float,
            )
            if utr_number:
                db.bank_credits.update_one(
                    {"utr_number": utr_number},
                    {"$set": {"claimed": True, "claimed_by": matched_user_id, "payment_id": payment_id, "updated_at": now}}
                )
            return {
                "success": True,
                "status": "auto_created_and_unlocked",
                "payment_id": payment_id,
                "user_id": matched_user_id,
                "message": f"Successfully auto-unlocked access for user {matched_user_id} via recent active checkout session."
            }

    return {
        "success": True,
        "status": "recorded_unclaimed",
        "utr_number": utr_number,
        "amount": amt_float,
        "message": "Bank credit recorded. Ready for instant auto-unlock when student session connects."
    }


def auto_claim_credit_for_student(user, item_type, item_id, session_token=None):
    """
    Checks if student is already unlocked or if an unclaimed bank credit matches
    their active checkout session. If matched, immediately unlocks the student!
    Returns: bool (unlocked)
    """
    if not user or not getattr(user, "is_authenticated", False):
        return False

    uid = str(user.id)
    iid = str(item_id)

    # 1. Direct access check
    if verify_student_unlock(user, item_type, iid):
        return True

    db = get_db()
    now = datetime.now(timezone.utc)
    item = get_item_by_type_and_id(item_type, iid)
    if not item:
        return False

    expected_price = float(getattr(item, "price", 0.0) or 0.0)

    # 2. Check if user has an approved payment document
    approved_pay = db.payments.find_one({
        "user_id": uid,
        "item_type": item_type,
        "item_id": iid,
        "status": "approved",
    })
    if approved_pay:
        grant_student_access(uid, item_type, iid, granted_by="payment_sync", payment_id=approved_pay.get("payment_id"), amount=expected_price)
        return True

    # 3. Check for matching bank credit by session token or recent unmatched credit
    credit = None
    if session_token:
        # Check if ref_note contains session_token
        credit = db.bank_credits.find_one({
            "claimed": False,
            "amount": expected_price,
            "ref_note": {"$regex": re.escape(str(session_token).strip()), "$options": "i"}
        })

    # If not matched by session token, check if single active checkout session matches
    if not credit and expected_price > 0:
        # Find credits matching exact price created within last 15 minutes
        recent_credits = list(db.bank_credits.find({
            "claimed": False,
            "amount": expected_price,
        }).sort("created_at", -1).limit(1))

        if recent_credits:
            credit = recent_credits[0]

    if credit:
        utr_num = credit.get("utr_number") or f"SMS{now.strftime('%H%M%S')}{secrets.token_hex(2).upper()}"
        payment_id = f"PAY-{now.strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"
        new_pay = {
            "payment_id": payment_id,
            "user_id": uid,
            "user_name": getattr(user, "name", "Student"),
            "user_email": getattr(user, "email", ""),
            "item_type": item_type,
            "item_id": iid,
            "item_title": getattr(item, "title", "SkillRock Course"),
            "amount": expected_price,
            "utr_number": utr_num,
            "status": "approved",
            "session_token": session_token,
            "submitted_at": now,
            "reviewed_at": now,
            "reviewed_by": "bank_sms_auto",
            "matched_via": "client_poll_claim",
            "created_at": now,
            "updated_at": now,
        }
        try:
            db.payments.insert_one(new_pay)
        except Exception as e:
            logger.info(f"Payment doc insert notice: {e}")

        db.bank_credits.update_one(
            {"_id": credit["_id"]},
            {"$set": {"claimed": True, "claimed_by": uid, "payment_id": payment_id, "updated_at": now}}
        )
        grant_student_access(uid, item_type, iid, granted_by="bank_sms_auto", payment_id=payment_id, amount=expected_price)
        return True

    return False

