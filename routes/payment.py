"""
SkillRock Payment & Access Control Blueprint
Handles student checkout, in-memory dynamic UPI QR code rendering,
safe UTR submission with anti-replay guarantees, payment status tracking,
and strict free enrollment gating (blocking paid items with HTTP 403).
"""

import os
import re
import json
import logging
import urllib.request
import urllib.error
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
from config import Config
from models import get_db, Course
from models.test_series import TestDefinition, TestPack
from services.payment_service import (
    validate_utr,
    generate_upi_qr_base64,
    get_item_by_type_and_id,
    verify_student_unlock,
    grant_student_access,
    register_checkout_session,
    parse_bank_credit_sms,
    process_incoming_bank_credit,
    auto_claim_credit_for_student,
)

logger = logging.getLogger(__name__)

payment_bp = Blueprint("payment", __name__)


AMBASSADOR_VALIDATION_BASE_URL = "https://skillrock-ambassador-portal-backend.onrender.com/api/sales/validate-srid"


def validate_srid_authoritative(srid):
    """
    Validates a Student Ambassador Referral ID against the authoritative external service.
    Returns tuple: (is_valid: bool, ambassador_name: str or None, is_service_available: bool)
    - Enforces format: 'SR' followed by exactly 4 numeric digits (e.g. 'SR1001').
    - Robustly accepts '1001', 'SR1001', or 'SRID:SR1001'.
    - Times out after 3.0 seconds to prevent blocking student checkout.
    - Gracefully handles Render cold-starts / 404s / 'no-server' without throwing.
    """
    if not srid:
        return False, None, True

    clean_srid = str(srid).strip().upper()
    clean_srid = re.sub(r"^SRID:?", "", clean_srid)
    if re.match(r"^\d{4}$", clean_srid):
        clean_srid = f"SR{clean_srid}"

    if not re.match(r"^SR\d{4}$", clean_srid):
        return False, None, True

    url = f"{AMBASSADOR_VALIDATION_BASE_URL}/{clean_srid}"
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "SkillRock-Backend-Validator/1.0",
                "Accept": "application/json",
            }
        )
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            name = (
                data.get("name")
                or data.get("ambassador_name")
                or (data.get("ambassador", {}).get("name") if isinstance(data.get("ambassador"), dict) else None)
            )
            is_valid = bool(data.get("valid", True) and name)
            return is_valid, name, True
    except urllib.error.HTTPError as e:
        is_render_no_server = "no-server" in str(e.headers.get("x-render-routing", "")).lower()
        if is_render_no_server or e.code >= 500:
            logger.info(f"Ambassador validation service unavailable ({e.code}, x-render-routing): {url}")
            return False, None, False
        if e.code == 404:
            return False, None, True
        return False, None, False
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        logger.info(f"Ambassador validation connection error or timeout: {e}")
        return False, None, False
    except Exception as e:
        logger.warning(f"Unexpected error validating SRID {clean_srid}: {e}")
        return False, None, False


def record_ambassador_sale(srid, item, user, amount, payment_id, utr_number, status="pending"):
    """
    Persists a referred course sale in MongoDB ambassador_sales collection,
    recording which ambassador sold which course, to whom, and when.
    Also dispatches non-blocking sync notification to Ambassador Portal API.
    """
    if not srid:
        return
    clean_srid = str(srid).strip().upper()
    clean_srid = re.sub(r"^SRID:?", "", clean_srid)
    if re.match(r"^\d{4}$", clean_srid):
        clean_srid = f"SR{clean_srid}"
    if not re.match(r"^SR\d{4}$", clean_srid):
        return

    now = datetime.now(timezone.utc)
    db = get_db()
    sale_doc = {
        "srid": clean_srid,
        "srid_display": f"SRID:{clean_srid}",
        "course_id": str(getattr(item, "id", "")),
        "course_title": getattr(item, "title", "Course"),
        "student_id": str(getattr(user, "id", "")),
        "student_name": getattr(user, "name", "Student"),
        "student_email": getattr(user, "email", ""),
        "amount": float(amount or 0.0),
        "payment_id": payment_id,
        "utr_number": utr_number,
        "status": status,
        "sold_at": now,
        "created_at": now,
        "updated_at": now,
    }
    try:
        db.ambassador_sales.update_one(
            {"payment_id": payment_id},
            {"$set": sale_doc},
            upsert=True
        )
    except Exception as e:
        logger.warning(f"Error persisting ambassador_sales record: {e}")

    # Asynchronous non-blocking dispatch to external ambassador portal
    try:
        portal_url = "https://skillrock-ambassador-portal-backend.onrender.com/api/sales/record"
        payload = json.dumps({
            "srid": clean_srid,
            "course_title": sale_doc["course_title"],
            "student_name": sale_doc["student_name"],
            "student_email": sale_doc["student_email"],
            "amount": sale_doc["amount"],
            "payment_id": payment_id,
            "utr_number": utr_number,
            "status": status,
            "sold_at": now.isoformat(),
        }).encode("utf-8")
        req = urllib.request.Request(
            portal_url,
            data=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "SkillRock-Sales-Dispatcher/1.0"
            },
            method="POST"
        )
        urllib.request.urlopen(req, timeout=1.5)
    except Exception as e:
        logger.info(f"Ambassador portal notification notice: {e}")


@payment_bp.route("/api/sales/validate-srid/<srid>", methods=["GET"])
def api_validate_srid(srid):
    """
    Backend proxy endpoint for live debounced ambassador referral validation in checkout.
    Prevents CORS issues and provides graceful messaging when ambassador service is sleeping.
    """
    clean_srid = str(srid or "").strip().upper()
    clean_srid = re.sub(r"^SRID:?", "", clean_srid)
    if re.match(r"^\d{4}$", clean_srid):
        clean_srid = f"SR{clean_srid}"

    if not re.match(r"^SR\d{4}$", clean_srid):
        return jsonify({
            "success": True,
            "valid": False,
            "available": True,
            "srid": clean_srid,
            "message": "Invalid Ambassador ID. Please check the 4-digit number."
        })

    is_valid, name, is_available = validate_srid_authoritative(clean_srid)
    if not is_available:
        return jsonify({
            "success": True,
            "valid": False,
            "available": False,
            "srid": clean_srid,
            "message": "Ambassador validation service is temporarily unavailable. Checkout will proceed normally."
        })

    if is_valid and name:
        return jsonify({
            "success": True,
            "valid": True,
            "available": True,
            "srid": clean_srid,
            "name": name,
            "message": f"Verified Ambassador: {name}"
        })
    else:
        return jsonify({
            "success": True,
            "valid": False,
            "available": True,
            "srid": clean_srid,
            "message": "Invalid Ambassador ID. Please check the 4-digit number."
        })


@payment_bp.route("/payment/update-referral", methods=["POST"])
@login_required
def update_referral():
    """
    Updates the student's active checkout session with the latest valid SRID in real-time.
    Called asynchronously from client when student enters a referral ID during checkout.
    """
    data = request.get_json(silent=True) or {}
    session_token = str(data.get("session_token") or "").strip()
    srid_raw = str(data.get("srid") or "").strip()

    if not session_token:
        return jsonify({"success": False, "error": "Missing session token"}), 400

    db = get_db()
    session_doc = db.checkout_sessions.find_one({"session_token": session_token})
    if not session_doc or session_doc.get("user_id") != str(current_user.id):
        return jsonify({"success": False, "error": "Session not found or unauthorized"}), 403

    now = datetime.now(timezone.utc)
    if not srid_raw:
        db.checkout_sessions.update_one(
            {"session_token": session_token},
            {"$unset": {"srid": ""}, "$set": {"updated_at": now}}
        )
        return jsonify({"success": True, "srid": None})

    clean_srid = srid_raw.upper()
    if re.match(r"^\d{4}$", clean_srid):
        clean_srid = f"SR{clean_srid}"

    if not re.match(r"^SR\d{4}$", clean_srid):
        return jsonify({"success": False, "error": "Invalid SRID format"}), 400

    db.checkout_sessions.update_one(
        {"session_token": session_token},
        {"$set": {"srid": clean_srid, "updated_at": now}}
    )
    return jsonify({"success": True, "srid": clean_srid})


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

    # Check for optional prefilled referral code (query param ?ref=1001 or ?ref=SR1001 or ?srid=1001)
    ref_param = (request.args.get("ref", "") or request.args.get("srid", "")).strip()
    clean_ref = None
    if ref_param:
        c_ref = ref_param.upper().replace(" ", "")
        if re.match(r"^SRID:SR\d{4}$", c_ref):
            clean_ref = f"SR{c_ref[-4:]}"
        elif re.match(r"^SRID:\d{4}$", c_ref):
            clean_ref = f"SR{c_ref[-4:]}"
        elif re.match(r"^\d{4}$", c_ref):
            clean_ref = f"SR{c_ref}"
        elif re.match(r"^SR\d{4}$", c_ref):
            clean_ref = c_ref

    # Generate in-memory dynamic QR code locked to exact server-side price
    qr_data = generate_upi_qr_base64(
        amount=price,
        item_type=item_type,
        item_id=str(item.id),
        item_title=item.title,
    )

    # Register active student checkout session for instant bank SMS auto-match
    register_checkout_session(
        user_id=str(current_user.id),
        item_type=item_type,
        item_id=str(item.id),
        session_token=qr_data.get("session_token"),
        amount=price,
        srid=clean_ref,
    )

    return render_template(
        "payment/checkout.html",
        item=item,
        item_type=item_type,
        item_id=str(item.id),
        price=price,
        qr_data=qr_data,
        pending_payment=pending_payment,
        prefill_srid=(clean_ref[2:] if clean_ref else ""),
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

    srid_param = (request.args.get("srid", "") or request.args.get("ref", "")).strip()
    if not srid_param:
        db = get_db()
        existing_sess = db.checkout_sessions.find_one({
            "user_id": str(current_user.id),
            "item_id": str(item.id),
        }, sort=[("updated_at", -1)])
        if existing_sess and existing_sess.get("srid"):
            srid_param = existing_sess["srid"]

    # Register refreshed checkout session
    register_checkout_session(
        user_id=str(current_user.id),
        item_type=item_type,
        item_id=str(item.id),
        session_token=qr_data.get("session_token"),
        amount=price,
        srid=srid_param,
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

    # Strip any spaces, hyphens, or formatting before validation
    import re
    utr_clean = re.sub(r"\D", "", str(utr_raw or "").strip())

    # Strict 12-digit UTR validation
    is_valid, err_msg = validate_utr(utr_clean)
    if not is_valid:
        flash(err_msg, "danger")
        return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))

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

    # Authoritative referral attribution (SRID)
    srid_raw = str(request.form.get("srid", "") or "").strip()
    clean_srid = None
    if srid_raw:
        candidate_srid = srid_raw.upper()
        if re.match(r"^\d{4}$", candidate_srid):
            clean_srid = f"SR{candidate_srid}"
        elif re.match(r"^SR\d{4}$", candidate_srid):
            clean_srid = candidate_srid

    # Fallback to active checkout session if not submitted via form
    if not clean_srid:
        sess_lookup = db.checkout_sessions.find_one({
            "user_id": str(current_user.id),
            "item_id": str(item.id),
        }, sort=[("updated_at", -1)])
        if sess_lookup and sess_lookup.get("srid"):
            candidate_srid = str(sess_lookup["srid"]).strip().upper()
            if re.match(r"^SR\d{4}$", candidate_srid):
                clean_srid = candidate_srid

    # Check if this UTR was already detected & credited via Bank SMS
    bank_credit = db.bank_credits.find_one({
        "utr_number": utr_clean,
        "claimed": False,
        "amount": {"$gte": exact_price - 0.01}
    })
    if bank_credit:
        # Instant Auto-Unlock: Bank SMS already confirmed the funds
        payment_record = {
            "payment_id": payment_id,
            "user_id": str(current_user.id),
            "user_name": getattr(current_user, "name", "Student"),
            "user_email": getattr(current_user, "email", ""),
            "item_type": item_type,
            "item_id": str(item.id),
            "item_title": getattr(item, "title", "SkillRock Learning Item"),
            "amount": exact_price,
            "utr_number": utr_clean,
            "status": "approved",
            "submitted_at": now,
            "reviewed_at": now,
            "reviewed_by": "bank_sms_instant_match",
            "matched_via": "bank_credit_sms",
            "rejection_reason": None,
            "created_at": now,
            "updated_at": now,
        }
        if clean_srid:
            payment_record["srid"] = clean_srid
            record_ambassador_sale(
                srid=clean_srid,
                item=item,
                user=current_user,
                amount=exact_price,
                payment_id=payment_id,
                utr_number=utr_clean,
                status="approved",
            )
        try:
            db.payments.insert_one(payment_record)
        except DuplicateKeyError:
            flash(f"UTR '{utr_clean}' has already been recorded.", "danger")
            return redirect(url_for("payment.checkout", item_type=item_type, item_id=str(item.id)))

        db.bank_credits.update_one(
            {"_id": bank_credit["_id"]},
            {"$set": {"claimed": True, "claimed_by": str(current_user.id), "payment_id": payment_id, "updated_at": now}}
        )
        grant_student_access(
            user_id=str(current_user.id),
            item_type=item_type,
            item_id=str(item.id),
            granted_by="bank_sms_instant_match",
            payment_id=payment_id,
            amount=exact_price,
        )
        flash(f"⚡ Instant Bank Match: Payment of ₹{int(exact_price)} verified via Bank SMS. Access unlocked!", "success")
        if item_type == "course":
            return redirect(url_for("learning.course_detail", slug=item.slug, player=1, _anchor="skillrockPlayerFrame"))
        else:
            return redirect(url_for("test_series.test_detail", test_slug=item.slug))

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
    if clean_srid:
        payment_record["srid"] = clean_srid
        record_ambassador_sale(
            srid=clean_srid,
            item=item,
            user=current_user,
            amount=exact_price,
            payment_id=payment_id,
            utr_number=utr_clean,
            status="pending",
        )

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
# 2B. Automated Bank SMS Webhook
# ==============================================================================

@payment_bp.route("/api/webhook/bank-sms", methods=["POST"])
def bank_sms_webhook():
    """
    Automated Bank SMS / UPI Credit Webhook Engine.
    Receives forwarded incoming bank SMS from student transfers to 9243494968@nyes.
    Parses amount, 12-digit UTR, and reference note.
    Automatically approves pending payments or unlocks active student sessions.
    Zero manual admin action required!
    """
    secret = (
        request.headers.get("X-Webhook-Secret")
        or request.args.get("secret")
        or (request.is_json and (request.get_json(silent=True) or {}).get("secret"))
        or request.form.get("secret")
    )
    expected_secret = getattr(Config, "BANK_SMS_WEBHOOK_SECRET", "skillrock_bank_hook_sec_2026")
    if not secret or secret != expected_secret:
        logger.warning(f"Unauthorized bank SMS webhook attempt with invalid secret from {request.remote_addr}")
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    payload = {}
    if request.is_json:
        payload = request.get_json(silent=True) or {}
    else:
        payload = request.form.to_dict() or {}
        # Auto-parse if MacroDroid sent raw JSON without setting Content-Type: application/json
        if not payload:
            raw_text = request.get_data(as_text=True)
            if raw_text and ("{" in raw_text):
                try:
                    import json
                    payload = json.loads(raw_text.strip())
                except Exception:
                    pass

    # Re-check secret if it was passed inside JSON body
    if not secret and isinstance(payload, dict):
        secret = payload.get("secret")
    if not secret or secret != expected_secret:
        logger.warning(f"Unauthorized bank SMS webhook attempt with invalid secret from {request.remote_addr}")
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    sms_text = (
        payload.get("message")
        or payload.get("notification")
        or payload.get("not_text")
        or payload.get("body")
        or payload.get("text")
        or payload.get("sms")
        or payload.get("content")
        or request.get_data(as_text=True)
    )
    sender = (
        payload.get("sender")
        or payload.get("not_title")
        or payload.get("title")
        or payload.get("from")
        or payload.get("address")
        or ""
    )

    if not sms_text:
        return jsonify({"success": False, "error": "Missing SMS content"}), 400

    logger.info(f"Received Bank SMS notification from sender: {sender}")
    parsed = parse_bank_credit_sms(sms_text, sender=sender)

    if not parsed.get("is_credit"):
        logger.info(f"Bank SMS ignored: {parsed.get('error')}")
        return jsonify({"success": False, "reason": parsed.get("error")}), 200

    # Process verified bank credit
    res = process_incoming_bank_credit(
        amount=parsed["amount"],
        utr_number=parsed.get("utr_number"),
        ref_note=parsed.get("ref_note"),
        sender=sender,
        raw_sms=sms_text,
    )

    return jsonify({
        "success": True,
        "parsed": {
            "amount": parsed["amount"],
            "utr_number": parsed.get("utr_number"),
            "ref_note": parsed.get("ref_note"),
        },
        "result": res,
    }), 200


# ==============================================================================
# 2C. Client Auto-Status Polling
# ==============================================================================

@payment_bp.route("/payment/check-auto-status/<item_type>/<item_id>")
@login_required
def check_auto_status(item_type, item_id):
    """
    Lightweight background status polling for checkout.html.
    Checks if user has been unlocked via Bank SMS webhook or admin verification.
    Returns unlocked: True with direct player redirect URL as soon as verified.
    """
    if item_type not in ("course", "test_series"):
        return jsonify({"unlocked": False, "error": "Invalid item type"}), 400

    item = get_item_by_type_and_id(item_type, item_id)
    if not item:
        return jsonify({"unlocked": False, "error": "Item not found"}), 404

    session_token = request.args.get("session_token", "").strip()

    # Run auto-claim & unlock verification
    is_unlocked = auto_claim_credit_for_student(
        user=current_user,
        item_type=item_type,
        item_id=str(item.id),
        session_token=session_token,
    )

    if is_unlocked:
        if item_type == "course":
            redirect_url = url_for("learning.course_detail", slug=item.slug, player=1, _anchor="skillrockPlayerFrame")
        else:
            redirect_url = url_for("test_series.test_detail", test_slug=item.slug)

        return jsonify({
            "unlocked": True,
            "status": "approved",
            "redirect_url": redirect_url,
            "message": f"Payment verified! Unlocking {item.title}..."
        })

    db = get_db()
    pending = db.payments.find_one({
        "user_id": str(current_user.id),
        "item_type": item_type,
        "item_id": str(item.id),
        "status": "pending",
    })

    if pending:
        return jsonify({
            "unlocked": False,
            "status": "pending",
            "payment_id": pending.get("payment_id"),
            "message": "Payment is under verification.",
        })

    return jsonify({
        "unlocked": False,
        "status": "listening",
        "message": "Listening for UPI transfer...",
    })



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
