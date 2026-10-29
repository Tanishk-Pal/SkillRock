"""
Skill Rock — Application Factory
Connects Flask application with MongoDB database layer, Flask-Login,
and registered feature blueprints.
"""

import os
from flask import Flask, render_template, redirect, url_for, session, request, Response
from flask_login import LoginManager, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
from config import Config
from models import (
    get_db,
    User,
    Skill,
    Session,
    Connection,
    SwapRequest,
    Message,
    PlatformSettings,
    Course,
    Assignment,
    Submission,
    Certificate,
    ensure_admin_user,
    ensure_default_courses,
    ensure_default_test_series,
    TestDefinition,
    TestPack,
    TestAttempt
)
from routes import (
    auth_bp,
    dashboard_bp,
    profile_bp,
    discover_bp,
    swap_bp,
    connections_bp,
    sessions_bp,
    ai_bp,
    chat_bp,
    admin_bp,
    learning_bp,
    test_series_bp
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure ProxyFix for reverse proxy deployments (Render, Heroku, Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Initialize MongoDB connection, collections, and seed Super Admin & Default Courses
    with app.app_context():
        try:
            get_db()
            ensure_admin_user()
            ensure_default_courses()
            ensure_default_test_series()
        except Exception as e_init:
            import logging
            logging.getLogger(__name__).warning(f"Database initialization/seed notice: {e_init}")

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.get_by_id(user_id)

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(discover_bp)
    app.register_blueprint(swap_bp)
    app.register_blueprint(connections_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(learning_bp)
    app.register_blueprint(test_series_bp)

    # Provide global utilities & model classes safely in Jinja templates
    app.jinja_env.globals.update(
        str=str,
        len=len,
        Certificate=Certificate,
        Course=Course,
        Assignment=Assignment,
        Submission=Submission
    )

    # Global Error Handlers (Prevents unhandled crashes and logs detailed tracebacks)
    @app.errorhandler(500)
    def handle_500(e):
        import logging
        logging.getLogger(__name__).error(f"Global 500 Server Error: {e}", exc_info=True)
        try:
            return render_template("errors/500.html", error=str(e)), 500
        except Exception as te:
            logging.getLogger(__name__).error(f"Error rendering 500.html: {te}")
            return """<!DOCTYPE html><html><head><meta charset="utf-8"><title>SkillRock — Service Issue</title>
            <style>body{background:#0F172A;color:#F8FAFC;font-family:-apple-system,BlinkMacSystemFont,sans-serif;text-align:center;padding:80px 20px;}
            .btn{display:inline-block;background:#5B46F6;color:#FFF;text-decoration:none;padding:12px 28px;border-radius:9999px;font-weight:700;margin-top:20px;}</style></head><body>
            <h1>SkillRock Platform Notice</h1><p style="color:#94A3B8;">A momentary server condition occurred. Please reload.</p>
            <a href="/" class="btn">Return to SkillRock Home</a></body></html>""", 500

    @app.errorhandler(404)
    def handle_404(e):
        return render_template("errors/404.html"), 404

    # HTTP Security Hardening, Response Gzip Compression & Static Asset Caching
    @app.after_request
    def set_security_headers(response):
        # OWASP Recommended Core Security Headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["X-Permitted-Cross-Domain-Policies"] = "none"

        # HTTP Strict Transport Security (HSTS) on HTTPS / Reverse-Proxy
        if request.is_secure or request.headers.get("X-Forwarded-Proto", "").lower() == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Cache static assets (CSS, JS, images, fonts) for high performance
        if request.path.startswith("/static/"):
            response.headers["Cache-Control"] = "public, max-age=86400, stale-while-revalidate=604800"
        elif request.path.startswith("/admin") or request.path.startswith("/auth") or request.path.startswith("/signin"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"

        # Transparent Gzip Compression for HTML, CSS, JS, and JSON payloads > 500 bytes
        accept_encoding = request.headers.get("Accept-Encoding", "")
        if (
            "gzip" in accept_encoding.lower()
            and response.status_code == 200
            and not response.direct_passthrough
            and response.mimetype in ["text/html", "text/css", "application/javascript", "application/json", "text/plain"]
        ):
            try:
                import gzip
                content = response.get_data()
                if len(content) > 500:
                    compressed = gzip.compress(content, compresslevel=6)
                    response.set_data(compressed)
                    response.headers["Content-Encoding"] = "gzip"
                    response.headers["Content-Length"] = len(compressed)
                    response.headers["Vary"] = "Accept-Encoding"
            except Exception:
                pass

        return response

    # Ensure user sessions are persistent and track last active timestamp for storage management
    @app.before_request
    def handle_request_preflight():
        session.permanent = True
        if current_user and current_user.is_authenticated:
            try:
                current_user.touch_activity()
            except Exception:
                pass

    # Storage Optimization: Run inactive user & orphan purger in background daemon thread on boot
    import threading
    def _startup_storage_clean():
        try:
            import time
            time.sleep(15)  # Wait for app & DB connection to stabilize
            from services.storage_cleaner import run_storage_optimization
            run_storage_optimization(days=7)
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Startup storage optimization note: {e}")

    threading.Thread(target=_startup_storage_clean, daemon=True).start()

    # Automated Student Reminders Daemon: Periodically scans for students with pending lectures or waiting certificates
    def _student_reminders_worker():
        import time
        time.sleep(90)  # Wait for app & DB connection to stabilize before running background tasks
        while True:
            try:
                from services.reminder_service import scan_and_send_student_reminders
                scan_and_send_student_reminders(app=app)
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"Student reminders background job notice: {e}")
            # Check once daily (86400 seconds)
            time.sleep(86400)

    threading.Thread(target=_student_reminders_worker, daemon=True).start()

    # SEO: 301 Permanent Redirect to normalize trailing slashes (except root and static)
    @app.before_request
    def normalize_trailing_slash():
        if request.method in ["GET", "HEAD"] and request.path != '/' and request.path.endswith('/'):
            clean_path = request.path.rstrip('/')
            if request.query_string:
                return redirect(f"{clean_path}?{request.query_string.decode('utf-8')}", code=301)
            return redirect(clean_path, code=301)

    # SEO & Discoverability Context Processor: Canonical URL, OG defaults & robots directives
    @app.context_processor
    def inject_seo_data():
        clean_path = request.path.rstrip('/') or '/'
        canonical_url = f"https://skillrock.onrender.com{clean_path}" if clean_path != '/' else "https://skillrock.onrender.com/"
        
        # Identify non-public or user-private endpoints that must not be indexed
        is_private_page = any([
            request.path.startswith("/admin"),
            request.path.startswith("/chat"),
            request.path.startswith("/messages"),
            request.path.startswith("/dashboard"),
            request.path.startswith("/profile"),
            request.path.startswith("/settings"),
            request.path.startswith("/requests"),
            request.path.startswith("/sessions"),
            request.path.startswith("/skills"),
            request.path.startswith("/learning/my-learning"),
            request.path.startswith("/learning/assignment"),
            request.path.startswith("/learning/submit"),
            request.path.startswith("/test-series/attempts"),
            request.path.startswith("/learning/progress"),
            request.path in ["/login", "/register", "/signin", "/logout"]
        ])
        
        return {
            "canonical_url": canonical_url,
            "canonical_domain": "https://skillrock.onrender.com",
            "is_private_page": is_private_page,
            "default_og_image": "https://skillrock.onrender.com/static/img/skillrock-og-banner.png"
        }

    # Context processor for global navbar badges, admin status, and platform settings
    @app.context_processor
    def inject_global_data():
        from flask import g
        if not hasattr(g, "_cached_global_data"):
            pending_requests_count = 0
            unread_messages_count = 0
            if current_user.is_authenticated and current_user.id:
                pending_requests_count = SwapRequest.count({
                    "receiver_id": str(current_user.id),
                    "status": "pending"
                })
                unread_messages_count = Message.count_unread(current_user.id)

            settings = PlatformSettings.get_settings()
            g._cached_global_data = {
                "pending_requests_count": pending_requests_count,
                "unread_messages_count": unread_messages_count,
                "platform_settings": settings,
                "announcement_enabled": settings.get("announcement_enabled", False),
                "announcement_text": settings.get("announcement_text", ""),
                "app_name": settings.get("platform_name", "Skill Rock"),
                "app_tagline": settings.get("tagline", "Learn. Teach. Grow Together.")
            }
        return g._cached_global_data

    # Public Landing Page Route (Authenticated students land directly on Learn & Build)
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("learning.courses_list"))

        # Real platform stats directly from MongoDB
        total_students = User.count()
        total_skills = Skill.count()
        completed_sessions = Session.count({"status": "completed"})
        total_swaps = Connection.count()
        popular_skills = Skill.find_all(limit=8)

        return render_template(
            "index.html",
            total_students=total_students,
            total_skills=total_skills,
            completed_sessions=completed_sessions,
            total_swaps=total_swaps,
            popular_skills=popular_skills
        )

    # Dynamic Certificate Verification Root Alias
    @app.route("/verify/<cert_id>")
    def root_verify_cert(cert_id):
        return redirect(url_for("learning.verify_certificate", cert_id=cert_id))

    # Course Catalogue Root Alias
    @app.route("/courses")
    def root_courses():
        return redirect(url_for("learning.courses_list"))

    # Lightweight Health Check Endpoint for Keep-Alive & Monitoring (Uptime pings)
    @app.route("/healthz", methods=["GET", "HEAD"])
    @app.route("/health", methods=["GET", "HEAD"])
    def health_check():
        if request.method == "HEAD":
            return Response(status=200, mimetype="application/json")
        return Response('{"status":"ok","app":"SkillRock"}', status=200, mimetype="application/json")

    # Google Search Console Verification Endpoint
    @app.route("/google26078168ee5d1f7d.html")
    def google_search_console_verification():
        return Response("google-site-verification: google26078168ee5d1f7d.html", mimetype="text/html")

    # AI & LLM Discoverability Endpoints (Standardized llms.txt & llms-full.txt)
    @app.route("/llms.txt")
    def llms_txt():
        from flask import send_from_directory
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "llms.txt",
            mimetype="text/markdown; charset=utf-8"
        )

    @app.route("/llms-full.txt")
    def llms_full_txt():
        from flask import send_from_directory
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "llms-full.txt",
            mimetype="text/markdown; charset=utf-8"
        )

    # SEO: Robots.txt for Search Engines and AI Crawlers
    @app.route("/robots.txt")
    def robots_txt():
        canonical_base = "https://skillrock.onrender.com"
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            "Allow: /learning/courses\n"
            "Allow: /learning/courses/\n"
            "Allow: /learning/verify/\n"
            "Allow: /verify/\n"
            "Allow: /static/\n"
            "Allow: /llms.txt\n"
            "Allow: /llms-full.txt\n"
            "Disallow: /admin/\n"
            "Disallow: /chat/\n"
            "Disallow: /messages/\n"
            "Disallow: /settings/\n"
            "Disallow: /api/\n"
            "Disallow: /my-learning\n"
            "Disallow: /learning/my-learning\n"
            "Disallow: /learning/progress/\n"
            "Disallow: /learning/save-progress\n"
            "Disallow: /learning/enrol/\n"
            "Disallow: /learning/submit/\n"
            "Disallow: /learning/assignment/\n"
            "Disallow: /dashboard\n"
            "Disallow: /profile\n"
            "Disallow: /requests\n"
            "Disallow: /sessions\n"
            "Disallow: /login\n"
            "Disallow: /register\n"
            "Disallow: /signin\n"
            "Disallow: /logout\n"
            "Disallow: /auth/\n"
            f"Sitemap: {canonical_base}/sitemap.xml\n"
        )
        return Response(content, mimetype="text/plain")

    # SEO: Dynamic XML Sitemap for Google, Bing & Search Engine Indexing
    @app.route("/sitemap.xml")
    def sitemap_xml():
        canonical_base = "https://skillrock.onrender.com"
        urls = [
            f"<url><loc>{canonical_base}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>",
            f"<url><loc>{canonical_base}/learning/courses</loc><changefreq>daily</changefreq><priority>0.9</priority></url>",
        ]

        # Dynamically append all published courses for rich search indexing
        try:
            published_courses = Course.get_published_courses() or []
            for c in published_courses:
                if c.slug:
                    lastmod_str = ""
                    if getattr(c, "updated_at", None):
                        try:
                            lastmod_str = f"<lastmod>{c.updated_at.strftime('%Y-%m-%d')}</lastmod>"
                        except Exception:
                            pass
                    urls.append(
                        f"<url><loc>{canonical_base}/learning/courses/{c.slug}</loc>{lastmod_str}<changefreq>weekly</changefreq><priority>0.8</priority></url>"
                    )
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"Sitemap dynamic courses fetch: {e}")

        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{"".join(urls)}\n</urlset>'
        return Response(xml_content, mimetype="application/xml")

    # PWA: Web App Manifest Endpoint
    @app.route("/manifest.json")
    def pwa_manifest():
        from flask import send_from_directory
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "manifest.json",
            mimetype="application/manifest+json"
        )

    # PWA: Root-Scoped Service Worker Endpoint
    @app.route("/sw.js")
    def pwa_service_worker():
        from flask import send_from_directory
        response = send_from_directory(
            os.path.join(app.root_path, "static"),
            "sw.js",
            mimetype="application/javascript"
        )
        response.headers["Service-Worker-Allowed"] = "/"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response

    # Native Favicon Endpoint (prevents 404 logs in browsers and search bots)
    @app.route("/favicon.ico")
    def favicon():
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>"""
        return Response(svg, mimetype="image/svg+xml")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="127.0.0.1", port=5000)
