"""
SkillSwap Campus — Models Package
Exports MongoDB models and database connection helpers.
"""

from models.mongo import (
    db,
    get_db,
    User,
    Skill,
    SkillItem,
    SwapRequest,
    Connection,
    Session,
    Rating,
    Badge,
    Message,
    PlatformSettings,
    ensure_admin_user
)

# Aliases for backward compatibility
UserSkill = SkillItem
UserBadge = Badge

__all__ = [
    "db",
    "get_db",
    "User",
    "Skill",
    "SkillItem",
    "UserSkill",
    "SwapRequest",
    "Connection",
    "Session",
    "Rating",
    "Badge",
    "UserBadge",
    "Message",
    "PlatformSettings",
    "ensure_admin_user",
]
