"""
SkillRock Payment & Access Control Blueprint
Handles student checkout, in-memory dynamic UPI QR code rendering,
safe UTR submission with anti-replay guarantees, payment status tracking,
and strict free enrollment gating (blocking paid items with HTTP 403).
"""

import os
import logging
from datetime import datetime, timezone
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    abort,
    jsonify,
    current_app,
)
from flask_login import login_required, current_user
from pymongo.errors import DuplicateKeyError
from models import get_db, Course
from models.test_series import TestDefinition, TestPack
from services.payment_service import (
    validate_utr,
    generate_upi_qr_base64,
    get_item_by_type_and_id,
    verify_student_unlock,
    grant_student_access,
)

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payment", __name__)


# ==============================================================================
# 1. Checkout Page (Dynamic In-Memory UPI QR Code)
# ==============================================================================

@payment_bp.route("/payment/checkout/<item_type>/<item_id>")
@login_required
def checkout(item_type, item_id):
    """
    Renders the official dynamic UPI checkout screen for paid courses & test series.
    - Never trusts client-side prices: always pulls authoritative price from MongoDB.
    - If item is free, redirects immediately to /enroll-free/<item_type>/<item_id>.
    - If user already unlocked item, redirects to the course/test player.
    """
    if item_type not in ("course", "test_series"):
        flash("Invalid item category selected.", "danger")
        return redirect(url_for("learning.courses_list"))

    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        flash("The requested learning item was not found.", "warning")
        return redirect(url_for("learning.courses_list"))

    # Authoritative server-side price check
    is_paid = getattr(item, "is_paid", False)
    price = getattr(item, "price", 0.0)

    # Free items bypass checkout completely
    if not is_paid or price <= 0:
        return redirect(url_for("payment.enroll_free", item_type=item_type, item_id=str(item.id)))

    # If student already owns access, send directly to content
    if verify_student_unlock(current_user, item_type, str(item.id)):
        flash(f"You already have active access to '{item.title}'!", "success")
        if item_type == "course":
            return redirect(url_for("learning.course_detail", slug=item.slug, player=1, _anchor="skillrockPlayerFrame"))
        else:
            return redirect(url_for("test_series.test_detail", test_slug=item.slug))

    db = get_db()
    # Check if this student already submitted a pending UTR for this item
    pending_payment = db.payments.find_one({
        "user_id": str(current_user.id),
        "item_type": item_type,
        "item_id": str(item.id),
        "status": "pending",
    })

    # Generate in-memory dynamic QR code locked to exact server-side price
    qr_data = generate_upi_qr_base64(
        amount=price,
        item_type=item_type,
        item_id=str(item.id),
        item_title=item.title,
    )

    return render_template(
        "payment/checkout.html",
        item=item,
        item_type=item_type,
        item_id=str(item.id),
        price=price,
        qr_data=qr_data,
        pending_payment=pending_payment,
    )


@payment_bp.route("/payment/refresh-qr/<item_type>/<item_id>")
@login_required
def refresh_qr(item_type, item_id):
    """
    Regenerates a fresh dynamic UPI QR code with a renewed 5-minute countdown window.
    Called asynchronously from client via AJAX when the previous 5-minute timer expires.
    """
    if item_type not in ("course", "test_series"):
        return jsonify({"success": False, "error": "Invalid item type"}), 400

    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        return jsonify({"success": False, "error": "Item not found"}), 404

    is_paid = getattr(item, "is_paid", False)
    price = getattr(item, "price", 0.0)

    if not is_paid or price <= 0:
        return jsonify({"success": False, "error": "Item is free"}), 400

    qr_data = generate_upi_qr_base64(
        amount=price,
        item_type=item_type,
        item_id=str(item.id),
        item_title=item.title,
    )

    return jsonify({
        "success": True,
        "qr_data_uri": qr_data["qr_data_uri"],
        "upi_uri": qr_data["upi_uri"],
        "gpay_uri": qr_data["gpay_uri"],
        "phonepe_uri": qr_data["phonepe_uri"],
        "paytm_uri": qr_data["paytm_uri"],
        "merchant_upi": qr_data["merchant_upi"],
        "merchant_name": qr_data["merchant_name"],
        "ref_note": qr_data["ref_note"],
        "amount": qr_data["amount"],
        "session_token": qr_data["session_token"],
        "expires_in": qr_data["expires_in"],
        "expires_at": qr_data["expires_at"],
    })


# ==============================================================================
# 2. UTR Submission & Anti-Replay Guard
# ==============================================================================

@payment_bp.route("/payment/submit", methods=["POST"])
@login_required
def submit_payment():
    """
    Receives student's 12-digit UTR submission:
    - NO CLIENT-SIDE TRUST: Completely ignores any client amount, price, or status fields.
    - Pulls authoritative item details and price directly from MongoDB.
    - Validates 12-digit UTR and blocks dummy patterns.
    - Enforces uniqueness index to prevent UTR replay / reuse.
    """
    item_type = request.form.get("item_type", "").strip()
    item_id = request.form.get("item_id", "").strip()
    utr_raw = request.form.get("utr_number", "").strip()

    if item_type not in ("course", "test_series") or not item_id:
        flash("Invalid payment target item.", "danger")
        return redirect(url_for("learning.courses_list"))

    # Server-side item retrieval
    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        flash("The course or test series you are purchasing could not be located.", "danger")
        return redirect(url_for("learning.courses_list"))

    is_paid = getattr(item, "is_paid", False)
    exact_price = float(getattr(item, "price", 0.0) or 0.0)

    if not is_paid or exact_price <= 0:
        return redirect(url_for("payment.enroll_free", item_type=item_type, item_id=str(item.id)))

    # Strict 12-digit UTR validation
    is_valid, err_msg = validate_utr(utr_raw)
    if not is_valid:
        flash(err_msg, "danger")
        return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))

    utr_clean = str(utr_raw).strip()
    db = get_db()

    # Pre-check existing payment records for anti-replay
    existing_utr = db.payments.find_one({"utr_number": utr_clean})
    if existing_utr:
        flash(
            f"The UTR reference '{utr_clean}' has already been submitted on SkillRock and cannot be reused. "
            "Please check your bank transaction or contact support if you need assistance.",
            "danger",
        )
        return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))

    # Unique Payment Reference ID
    now = datetime.now(timezone.utc)
    payment_id = f"PAY-{now.strftime('%Y%m%d')}-{os.urandom(3).hex().upper()}"

    payment_record = {
        "payment_id": payment_id,
        "user_id": str(current_user.id),
        "user_name": getattr(current_user, "name", "Student"),
        "user_email": getattr(current_user, "email", ""),
        "item_type": item_type,
        "item_id": str(item.id),
        "item_title": getattr(item, "title", "SkillRock Learning Item"),
        "amount": exact_price,  # Authoritative server price ONLY
        "utr_number": utr_clean,
        "status": "pending",
        "submitted_at": now,
        "reviewed_at": None,
        "reviewed_by": None,
        "rejection_reason": None,
        "created_at": now,
        "updated_at": now,
    }

    try:
        db.payments.insert_one(payment_record)
    except DuplicateKeyError:
        flash(
            f"The UTR number '{utr_clean}' has already been recorded in the database. "
            "Anti-replay protection has blocked this duplicate submission.",
            "danger",
        )
        return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))
    except Exception as e:
        logger.error(f"Error recording payment {payment_id}: {e}", exc_info=True)
        flash("A momentary database issue occurred while recording your payment. Please try again.", "danger")
        return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))

    flash(
        f"Payment of ₹{int(exact_price)} submitted successfully! UTR {utr_clean} is now pending verification. "
        "Our team verifies UPI transactions rapidly.",
        "success",
    )
    return redirect(url_for("payment.payment_status", payment_id=payment_id))


# ==============================================================================
# 3. Student Payment Status View
# ==============================================================================

@payment_bp.route("/payment/status/<payment_id>")
@login_required
def payment_status(payment_id):
    """Real-time payment tracker showing pending, approved, or rejected status."""
    db = get_db()
    payment = db.payments.find_one({"payment_id": str(payment_id).strip()})
    if not payment:
        flash("Payment record not found.", "warning")
        return redirect(url_for("learning.courses_list"))

    # Security check: User can only view their own payment unless admin
    if payment.get("user_id") != str(current_user.id) and not getattr(current_user, "is_admin", False):
        abort(403)

    item = get_item_by_type_and_id(payment.get("item_type"), payment.get("item_id"))

    return render_template(
        "payment/status.html",
        payment=payment,
        item=item,
    )


# ==============================================================================
# 4. Strict Free Enrollment Route (HTTP 403 Forbidden for Paid Items)
# ==============================================================================

@payment_bp.route("/enroll-free/<item_type>/<item_id>", methods=["GET", "POST"])
@login_required
def enroll_free(item_type, item_id):
    """
    CRITICAL SECURITY ENDPOINT:
    - Grants instantaneous free access ONLY IF item.is_paid == False and price == 0 in MongoDB.
    - If a user calls this on a paid course (e.g. ₹699) or test, BLOCKS with HTTP 403 Forbidden!
    """
    if item_type not in ("course", "test_series"):
        abort(400)

    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        abort(404)

    is_paid = getattr(item, "is_paid", False)
    price = getattr(item, "price", 0.0)

    # STRICT SECURITY CHECK: Block paid items unconditionally
    if is_paid is True or price > 0:
        logger.warning(
            f"SECURITY ALERT: User {current_user.id} ({current_user.email}) attempted free enrollment "
            f"on PAID item {item_type} #{item_id} (Price: ₹{price}). Access blocked with 403."
        )
        abort(403)

    # Legitimate Free Item -> Grant access & auto-enroll
    grant_student_access(
        user_id=str(current_user.id),
        item_type=item_type,
        item_id=str(item.id),
        granted_by="system_free",
        amount=0.0,
    )

    flash(f"🎉 Enrolled in '{item.title}'! Your free learning session has started.", "success")

    if item_type == "course":
        return redirect(url_for("learning.course_detail", slug=item.slug, player=1, _anchor="skillrockPlayerFrame"))
    else:
        return redirect(url_for("test_series.test_detail", test_slug=item.slug))
