"""
SkillRock Email Notification Service
Handles asynchronous email notifications via Gmail SMTP to notify administrators
when students submit practical project assignments (GitHub + Live URL) for manual review.
"""

import os
import smtplib
import threading
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def _send_email_thread(subject, html_content, text_content, recipient_email):
    """Internal daemon thread worker to dispatch SMTP email without blocking student requests."""
    gmail_user = (os.getenv("GMAIL_USER") or os.getenv("MAIL_USERNAME") or "skillrockk@gmail.com").strip()
    gmail_pass = (os.getenv("GMAIL_APP_PASSWORD") or os.getenv("MAIL_PASSWORD") or "TanishkDeepakPal062007").strip()
    smtp_server = os.getenv("MAIL_SERVER", "smtp.gmail.com").strip()
    smtp_port = int(os.getenv("MAIL_PORT", 587))
    sender_email = gmail_user or "notifications@skillrock.com"

    if not gmail_user or not gmail_pass:
        logger.info(
            f"[EMAIL NOTIFICATION] GMAIL_USER / GMAIL_APP_PASSWORD not configured. "
            f"Simulated dispatch for '{subject}' to {recipient_email}. "
            f"(Configure GMAIL_USER and GMAIL_APP_PASSWORD in Render Environment variables to enable live Gmail sending)"
        )
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"SkillRock Platform <{sender_email}>"
        msg["To"] = recipient_email

        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        with smtplib.SMTP(smtp_server, smtp_port, timeout=12) as server:
            server.starttls()
            server.login(gmail_user, gmail_pass)
            server.sendmail(sender_email, recipient_email, msg.as_string())

        logger.info(f"[EMAIL NOTIFICATION SUCCESS] Sent assignment notification to {recipient_email}")
    except Exception as e:
        logger.warning(f"[EMAIL NOTIFICATION WARNING] Could not send notification email via SMTP: {e}")


def send_admin_assignment_notification(student, course, assignment, submission):
    """
    Dispatches an asynchronous Gmail notification to the administrator
    when a student submits a practical project assignment with GitHub and Live Deployment URLs.
    """
    admin_email = os.getenv("ADMIN_NOTIFICATION_EMAIL", "palt51419@gmail.com").strip()
    student_name = getattr(student, "name", "Student")
    student_email = getattr(student, "email", "N/A")
    course_title = getattr(course, "title", "Course")
    asg_title = getattr(assignment, "title", "Project Milestone")
    step_num = getattr(submission, "step_number", 1)
    github_url = getattr(submission, "github_url", "N/A")
    deployment_url = getattr(submission, "deployment_url", "N/A")
    review_url = "https://skillrock.onrender.com/admin/submissions"

    subject = f"🚀 [SkillRock] New Project Submission: {student_name} — {course_title}"

    text_content = f"""
Hello Admin,

A student has uploaded a practical project assignment on SkillRock for manual review!

• Student: {student_name} ({student_email})
• Course: {course_title}
• Milestone: Step {step_num} - {asg_title}
• GitHub Repository: {github_url}
• Live Deployment: {deployment_url}
• Submitted At: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

Review and evaluate this submission in the Admin Console:
{review_url}

Best regards,
SkillRock Notification System
"""

    html_content = f"""<!DOCTYPE html>
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background-color: #0B0F19; color: #FFFFFF; padding: 24px; margin: 0;">
    <div style="max-width: 600px; margin: 0 auto; background: #131B2E; border: 1px solid #1E293B; border-radius: 12px; overflow: hidden; padding: 28px;">
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; border-bottom: 1px solid #1E293B; padding-bottom: 16px;">
            <h2 style="margin: 0; color: #6366F1; font-size: 1.4rem; font-weight: 800;">SkillRock</h2>
            <span style="background: rgba(99, 102, 241, 0.15); color: #818CF8; font-size: 0.75rem; padding: 4px 10px; border-radius: 6px; font-weight: 700;">Manual Review Required</span>
        </div>
        
        <p style="font-size: 1rem; color: #E2E8F0; margin-bottom: 16px;">
            Hello Admin, a student has uploaded a practical project assignment for manual evaluation and verification!
        </p>

        <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid #334155; border-radius: 8px; padding: 18px; margin-bottom: 24px;">
            <p style="margin: 6px 0; color: #94A3B8; font-size: 0.9rem;"><strong style="color: #FFFFFF;">Student:</strong> {student_name} (<a href="mailto:{student_email}" style="color: #38BDF8; text-decoration: none;">{student_email}</a>)</p>
            <p style="margin: 6px 0; color: #94A3B8; font-size: 0.9rem;"><strong style="color: #FFFFFF;">Course:</strong> {course_title}</p>
            <p style="margin: 6px 0; color: #94A3B8; font-size: 0.9rem;"><strong style="color: #FFFFFF;">Milestone:</strong> Step {step_num} — {asg_title}</p>
            <p style="margin: 6px 0; color: #94A3B8; font-size: 0.9rem;"><strong style="color: #FFFFFF;">GitHub Repo:</strong> <a href="{github_url}" target="_blank" style="color: #6366F1;">{github_url}</a></p>
            <p style="margin: 6px 0; color: #94A3B8; font-size: 0.9rem;"><strong style="color: #FFFFFF;">Live Deployment:</strong> <a href="{deployment_url}" target="_blank" style="color: #10B981;">{deployment_url}</a></p>
        </div>

        <div style="text-align: center; margin-top: 24px;">
            <a href="{review_url}" target="_blank" style="display: inline-block; background: #6366F1; color: #FFFFFF; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 700; font-size: 0.95rem;">
                Open Admin Review Queue & Evaluate
            </a>
        </div>
    </div>
</body>
</html>"""

    thread = threading.Thread(
        target=_send_email_thread,
        args=(subject, html_content, text_content, admin_email),
        daemon=True
    )
    thread.start()
