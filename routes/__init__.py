from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.profile import profile_bp
from routes.discover import discover_bp
from routes.swap import swap_bp
from routes.connections import connections_bp
from routes.sessions import sessions_bp
from routes.ai import ai_bp
from routes.chat import chat_bp
from routes.admin import admin_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "profile_bp",
    "discover_bp",
    "swap_bp",
    "connections_bp",
    "sessions_bp",
    "ai_bp",
    "chat_bp",
    "admin_bp",
]
