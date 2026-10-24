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
    ensure_default_courses
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
    learning_bp
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Configure ProxyFix for reverse proxy deployments (Render, Heroku, Nginx)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

    # Initialize MongoDB connection, collections, and seed Super Admin & Default Courses
    with app.app_context():
        get_db()
        ensure_admin_user()
        ensure_default_courses()

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
        return render_template("errors/500.html", error=str(e)), 500

    @app.errorhandler(404)
    def handle_404(e):
        return render_template("errors/404.html"), 404

    # HTTP Security Hardening, Response Gzip Compression & Static Asset Caching
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
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

    # Ensure user sessions are persistent across browser closes and computer restarts (60 days)
    @app.before_request
    def make_session_permanent():
        session.permanent = True

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

    # SEO: Robots.txt for Search Engines
    @app.route("/robots.txt")
    def robots_txt():
        base_url = request.url_root.rstrip('/')
        content = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /admin/\n"
            "Disallow: /chat/\n"
            "Disallow: /settings/\n"
            f"Sitemap: {base_url}/sitemap.xml\n"
        )
        return Response(content, mimetype="text/plain")

    # SEO: Dynamic XML Sitemap for Google & Bing Indexing
    @app.route("/sitemap.xml")
    def sitemap_xml():
        base_url = request.url_root.rstrip('/')
        urls = [
            f"<url><loc>{base_url}/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>",
            f"<url><loc>{base_url}/discover</loc><changefreq>hourly</changefreq><priority>0.9</priority></url>",
            f"<url><loc>{base_url}/ai-assistant</loc><changefreq>weekly</changefreq><priority>0.8</priority></url>",
            f"<url><loc>{base_url}/login</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
            f"<url><loc>{base_url}/register</loc><changefreq>monthly</changefreq><priority>0.6</priority></url>",
        ]
        xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{"".join(urls)}\n</urlset>'
        return Response(xml_content, mimetype="application/xml")

    # Native Favicon Endpoint (prevents 404 logs in browsers and search bots)
    @app.route("/favicon.ico")
    def favicon():
        svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m17 2 4 4-4 4"/><path d="M3 11v-1a4 4 0 0 1 4-4h14"/><path d="m7 22-4-4 4-4"/><path d="M21 13v1a4 4 0 0 1-4 4H3"/></svg>"""
        return Response(svg, mimetype="image/svg+xml")

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=Config.DEBUG, host="127.0.0.1", port=5000)
