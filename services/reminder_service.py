"""
SkillRock Automated Student Learning & Certificate Reminder Service
Monitors student course progress and sends periodic, non-spammy email reminders
every 2 to 3 days when a student has:
1) A lecture pending completion (watch_percent < 80%)
2) A certificate waiting to be claimed (watch_percent >= 80%, project or quiz pending)
"""

import os
import logging
from datetime import datetime, timezone, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import threading

logger = logging.getLogger(__name__)

# Minimum interval between reminders to the same student (2.5 days = 60 hours)
MIN_REMINDER_INTERVAL_HOURS = 48  # 2 days minimum
MAX_INACTIVITY_DAYS = 21  # Stop emailing after 3 weeks of zero activity to avoid fatigue


def _dispatch_smtp_email(subject, html_body, text_body, recipient_email):
    """
    Sends an email using configured Gmail SMTP credentials.
    Runs synchronously within caller's worker thread.
    """
    gmail_user = (os.getenv("GMAIL_USER") or os.getenv("MAIL_USERNAME") or "skillrockk@gmail.com").strip()
    gmail_pass = (os.getenv("GMAIL_APP_PASSWORD") or os.getenv("MAIL_PASSWORD") or "TanishkDeepakPal062007").strip()
    smtp_server = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    sender_name = "SkillRock Student Academy"

    if not gmail_user or not gmail_pass:
        logger.warning(f"[REMINDER] Missing SMTP credentials. Simulated dispatch to {recipient_email}")
        return False, "Missing SMTP credentials"

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{sender_name} <{gmail_user}>"
        msg["To"] = recipient_email

        part_text = MIMEText(text_body, "plain", "utf-8")
        part_html = MIMEText(html_body, "html", "utf-8")
        msg.attach(part_text)
        msg.attach(part_html)

        # Attempt TLS on port 587 first
        try:
            with smtplib.SMTP(smtp_server, smtp_port, timeout=14) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(gmail_user, gmail_pass)
                server.sendmail(gmail_user, recipient_email, msg.as_string())
            logger.info(f"[REMINDER SUCCESS] Sent to {recipient_email} via TLS 587")
            return True, "Delivered"
        except (smtplib.SMTPServerDisconnected, smtplib.SMTPConnectError, TimeoutError):
            # Fallback to SSL on port 465
            with smtplib.SMTP_SSL(smtp_server, 465, timeout=14) as server:
                server.login(gmail_user, gmail_pass)
                server.sendmail(gmail_user, recipient_email, msg.as_string())
            logger.info(f"[REMINDER SUCCESS] Sent to {recipient_email} via SSL 465")
            return True, "Delivered"

    except smtplib.SMTPAuthenticationError as auth_err:
        err_msg = (
            f"Gmail SMTP authentication requires an App Password. "
            f"Generate one at https://myaccount.google.com/apppasswords and set GMAIL_APP_PASSWORD. Detail: {auth_err}"
        )
        logger.warning(f"[REMINDER AUTH WARNING] {err_msg}")
        return False, err_msg
    except Exception as e:
        logger.error(f"[REMINDER ERROR] Failed sending to {recipient_email}: {e}")
        return False, str(e)


def build_reminder_email_content(student_name, course_title, course_slug, reminder_type, watch_percent, resume_time=None):
    """
    Constructs high-converting, professional HTML and plain text email content
    modeled after premier EdTech platforms (Coursera, Udemy, Physics Wallah).
    """
    course_url = f"https://skillrock.onrender.com/learning/courses/{course_slug}"
    first_name = (student_name or "Student").split()[0].title()

    if reminder_type == "certificate_waiting":
        subject = f"🎓 {first_name}, your official certificate for {course_title} is waiting!"
        headline = "You're Just One Step Away From Your Certificate!"
        badge_text = "CERTIFICATE WAITING"
        badge_color = "#10B981"
        badge_bg = "rgba(16, 185, 129, 0.15)"
        body_p1 = (
            f"Great progress! You have completed the video lectures for <strong>{course_title}</strong>. "
            f"Your official SkillRock Certificate of Achievement is ready to unlock."
        )
        body_p2 = (
            "Complete your quick final assessment (project milestone or 70%+ score on the quiz) "
            "to receive your verified certificate with tamper-proof SHA-256 hash and verifiable QR code."
        )
        cta_text = "Claim Your Certificate Now →"
    else:
        subject = f"⏳ {first_name}, continue learning {course_title} ({watch_percent}% completed)"
        headline = "Pick Up Where You Left Off!"
        badge_text = f"{watch_percent}% COMPLETED"
        badge_color = "#6366F1"
        badge_bg = "rgba(99, 102, 241, 0.15)"
        body_p1 = (
            f"Consistency is the secret to mastering technical skills. You recently started "
            f"<strong>{course_title}</strong> and made solid headway."
        )
        body_p2 = (
            f"Watch just a little more to hit the <strong>80% milestone</strong> and unlock your "
            f"verifiable capstone project and official certificate for your resume."
        )
        cta_text = f"Resume Lecture Now ({resume_time or '00:00'}) →"

    text_body = f"""Hello {first_name},

{body_p1.replace('<strong>', '').replace('</strong>', '')}

{body_p2.replace('<strong>', '').replace('</strong>', '')}

Course: {course_title}
Current Progress: {watch_percent}%
Resume link: {course_url}

Best regards,
SkillRock Student Academy
https://skillrock.onrender.com
"""

    html_body = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #0F172A; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #F8FAFC;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0F172A; padding: 32px 12px;">
    <tr>
      <td align="center">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 580px; background-color: #1E293B; border: 1px solid #334155; border-radius: 16px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.4);">
          
          <!-- Brand Header -->
          <tr>
            <td style="background: linear-gradient(135deg, #4F46E5 0%, #7C3AED 100%); padding: 26px 32px; text-align: left;">
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td>
                    <div style="font-size: 20px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.02em;">
                      SkillRock <span style="font-size: 13px; font-weight: 600; opacity: 0.85; margin-left: 6px;">STUDENT ACADEMY</span>
                    </div>
                  </td>
                  <td align="right">
                    <span style="display: inline-block; background: {badge_bg}; color: {badge_color}; border: 1px solid {badge_color}; font-size: 11px; font-weight: 700; padding: 4px 10px; border-radius: 9999px; text-transform: uppercase; letter-spacing: 0.05em;">
                      {badge_text}
                    </span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Main Body -->
          <tr>
            <td style="padding: 32px;">
              <h1 style="margin: 0 0 14px 0; font-size: 22px; font-weight: 800; color: #FFFFFF; line-height: 1.3;">
                {headline}
              </h1>

              <p style="margin: 0 0 16px 0; font-size: 15px; line-height: 1.6; color: #CBD5E1;">
                Hi <strong>{first_name}</strong>,
              </p>

              <p style="margin: 0 0 18px 0; font-size: 15px; line-height: 1.6; color: #CBD5E1;">
                {body_p1}
              </p>

              <!-- Course Progress Highlight Box -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #0F172A; border: 1px solid #334155; border-radius: 12px; margin: 20px 0; padding: 18px;">
                <tr>
                  <td>
                    <div style="font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: #94A3B8; font-weight: 700; margin-bottom: 6px;">
                      Active Course
                    </div>
                    <div style="font-size: 16px; font-weight: 800; color: #FFFFFF; margin-bottom: 12px;">
                      {course_title}
                    </div>

                    <!-- Visual Progress Bar -->
                    <div style="background-color: #334155; height: 8px; border-radius: 9999px; overflow: hidden; margin-bottom: 8px;">
                      <div style="background: linear-gradient(90deg, #6366F1, #10B981); height: 100%; width: {max(5, watch_percent)}%; border-radius: 9999px;"></div>
                    </div>

                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                      <tr>
                        <td style="font-size: 12px; color: #94A3B8;">
                          Watched: <strong style="color: #F8FAFC;">{watch_percent}%</strong> (80% unlocks certificate)
                        </td>
                        <td align="right" style="font-size: 12px; color: #10B981; font-weight: 700;">
                          {'✅ Ready to Verify' if watch_percent >= 80 else 'In Progress'}
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>
              </table>

              <p style="margin: 0 0 26px 0; font-size: 14px; line-height: 1.6; color: #94A3B8;">
                {body_p2}
              </p>

              <!-- CTA Button -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                <tr>
                  <td align="center">
                    <a href="{course_url}" target="_blank" style="display: inline-block; background: linear-gradient(135deg, #4F46E5 0%, #6366F1 100%); color: #FFFFFF; font-size: 15px; font-weight: 800; text-decoration: none; padding: 14px 32px; border-radius: 9999px; box-shadow: 0 4px 16px rgba(79, 70, 229, 0.4);">
                      {cta_text}
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Value Points -->
              <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="margin-top: 32px; border-top: 1px solid #334155; padding-top: 20px;">
                <tr>
                  <td style="font-size: 12px; color: #94A3B8; line-height: 1.6;">
                    🔒 <strong>Tamper-Proof Credential:</strong> Verified with cryptographic SHA-256 hash.<br>
                    📱 <strong>Instant QR Verification:</strong> Scannable by employers and recruiters.<br>
                    💼 <strong>Shareable:</strong> Add directly to LinkedIn, Resume, and GitHub.
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #0F172A; padding: 20px 32px; text-align: center; border-top: 1px solid #334155;">
              <p style="margin: 0 0 6px 0; font-size: 12px; color: #64748B;">
                SkillRock Student Academy • Free Technical Learning & Placement Prep
              </p>
              <p style="margin: 0; font-size: 11px; color: #475569;">
                You received this email because you enrolled in this course on SkillRock.
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    return subject, html_body, text_body


def scan_and_send_student_reminders(app=None, force=False):
    """
    Main scheduled worker:
    1. Scans in-progress student enrollments.
    2. Identifies students inactive for 2 to 3 days (48-72 hours).
    3. Formats personalized reminder email.
    4. Dispatches asynchronously and updates last_reminder_email_at.
    """
    from models import get_db, User, Course, Enrollment, Certificate

    db = get_db()
    now = datetime.now(timezone.utc)
    cooldown_threshold = now - timedelta(hours=MIN_REMINDER_INTERVAL_HOURS)
    stale_threshold = now - timedelta(days=MAX_INACTIVITY_DAYS)

    logger.info("[STUDENT REMINDER] Starting student reminder scan...")

    # Find active in-progress enrollments
    enrollment_cursor = db[Enrollment.collection_name].find({"status": "in_progress"})
    enrollments = [Enrollment(doc) for doc in enrollment_cursor]

    # Group by user_id so each student receives AT MOST ONE reminder per scan
    user_enrollments = {}
    for enr in enrollments:
        uid = str(getattr(enr, "user_id", ""))
        if not uid:
            continue
        if uid not in user_enrollments:
            user_enrollments[uid] = []
        user_enrollments[uid].append(enr)

    scanned_count = len(user_enrollments)
    eligible_count = 0
    sent_count = 0
    errors = []

    for uid, enrs in user_enrollments.items():
        try:
            user = User.get_by_id(uid)
            if not user or not getattr(user, "email", None):
                continue

            # Anti-Spam Check 1: User-level reminder cooldown (at least 48 hours between any reminders)
            user_last_reminded = getattr(user, "last_reminder_email_at", None)
            if user_last_reminded and not force:
                if isinstance(user_last_reminded, str):
                    try:
                        user_last_reminded = datetime.fromisoformat(user_last_reminded.replace("Z", "+00:00"))
                    except Exception:
                        user_last_reminded = None
                if user_last_reminded and user_last_reminded.tzinfo is None:
                    user_last_reminded = user_last_reminded.replace(tzinfo=timezone.utc)
                if user_last_reminded and user_last_reminded > cooldown_threshold:
                    # User was reminded recently, skip
                    continue

            # Choose the highest priority enrollment for this student:
            # 1. Certificate waiting (watch_percent >= 80% but not certified yet)
            # 2. Most recently active lecture with watch_percent > 0%
            # 3. Any active course enrolled in the last 2-3+ days
            chosen_enr = None
            reminder_type = "lecture_pending"

            # Check if any course is at >= 80% (Certificate waiting)
            for e in enrs:
                c_id = getattr(e, "course_id", "")
                existing_cert = Certificate.get_by_user_course(uid, c_id)
                if not existing_cert and (getattr(e, "watch_percent", 0) >= 80 or getattr(e, "video_completed", False)):
                    chosen_enr = e
                    reminder_type = "certificate_waiting"
                    break

            # If no certificate waiting, find the best pending lecture
            if not chosen_enr:
                for e in sorted(enrs, key=lambda x: getattr(x, "watch_percent", 0), reverse=True):
                    # Check inactivity: last progress ping or created_at must be at least 48 hours ago
                    last_active = getattr(e, "last_progress_ping", None) or getattr(e, "created_at", None)
                    if last_active:
                        if isinstance(last_active, str):
                            try:
                                last_active = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
                            except Exception:
                                last_active = None
                        if last_active and last_active.tzinfo is None:
                            last_active = last_active.replace(tzinfo=timezone.utc)

                    if force or (last_active and last_active < cooldown_threshold and last_active > stale_threshold):
                        chosen_enr = e
                        reminder_type = "lecture_pending"
                        break

            if not chosen_enr:
                continue

            course = Course.get_by_id(getattr(chosen_enr, "course_id", ""))
            if not course:
                continue

            eligible_count += 1

            # Build and send email
            subject, html_body, text_body = build_reminder_email_content(
                student_name=getattr(user, "name", "Student"),
                course_title=getattr(course, "title", "Course"),
                course_slug=getattr(course, "slug", "course"),
                reminder_type=reminder_type,
                watch_percent=getattr(chosen_enr, "watch_percent", 0),
                resume_time=getattr(chosen_enr, "formatted_resume_time", "00:00")
            )

            success, msg = _dispatch_smtp_email(subject, html_body, text_body, user.email)
            if success:
                sent_count += 1
                # Update cooldown timestamp on both user and enrollment
                try:
                    db[User.collection_name].update_one(
                        {"_id": user._id},
                        {"$set": {"last_reminder_email_at": now}, "$inc": {"reminder_emails_sent": 1}}
                    )
                    db[Enrollment.collection_name].update_one(
                        {"_id": chosen_enr._id},
                        {"$set": {"last_reminder_sent_at": now}}
                    )
                except Exception as e_upd:
                    logger.warning(f"Could not update reminder timestamp: {e_upd}")
            else:
                errors.append(f"{user.email}: {msg}")

        except Exception as e_user:
            logger.error(f"Error processing reminders for student {uid}: {e_user}")
            errors.append(f"Student {uid}: {str(e_user)}")

    summary = {
        "scanned_students": scanned_count,
        "eligible_students": eligible_count,
        "sent_emails": sent_count,
        "errors": errors[:5]
    }
    logger.info(f"[STUDENT REMINDER COMPLETE] {summary}")
    return summary
