"""
Skill Rock — Application Factory
Connects Flask application with MongoDB database layer, Flask-Login,
and registered feature blueprints.
"""

import os
from flask import Flask, render_template, redirect, url_for, session, request, Response
from flask_login import LoginManager, current_user
from config import Config
from models import get_db, User, Skill, Session, Connection, SwapRequest, Message, PlatformSettings, ensure_admin_user
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
    admin_bp
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize MongoDB connection, collections, and seed Super Admin
    with app.app_context():
        get_db()
        ensure_admin_user()

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

    # Provide str globally in Jinja templates
    app.jinja_env.globals['str'] = str

    # Ensure user sessions are persistent across browser closes and computer restarts (60 days)
    @app.before_request
    def make_session_permanent():
        session.permanent = True

    # Context processor for global navbar badges, admin status, and platform settings
    @app.context_processor
    def inject_global_data():
        pending_requests_count = 0
        unread_messages_count = 0
        if current_user.is_authenticated and current_user.id:
            pending_requests_count = SwapRequest.count({
                "receiver_id": str(current_user.id),
                "status": "pending"
            })
            unread_messages_count = Message.count_unread(current_user.id)

        settings = PlatformSettings.get_settings()
        return {
            "pending_requests_count": pending_requests_count,
            "unread_messages_count": unread_messages_count,
            "platform_settings": settings,
            "announcement_enabled": settings.get("announcement_enabled", False),
            "announcement_text": settings.get("announcement_text", ""),
            "app_name": settings.get("platform_name", "Skill Rock"),
            "app_tagline": settings.get("tagline", "Learn. Teach. Grow Together.")
        }

    # Public Landing Page Route
    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard.dashboard"))

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
