"""
Skill Rock — Models Package
Exports MongoDB models and database connection helpers.
"""

from models.test_series import (
    Question,
    TestDefinition,
    TestPack,
    TestAttempt,
    UserEntitlement
)
from models.default_test_series import ensure_default_test_series

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
    Course,
    Assignment,
    Enrollment,
    Submission,
    Review,
    Certificate,
    extract_youtube_id,
    slugify,
    ensure_admin_user,
    ensure_default_courses
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
    "Course",
    "Assignment",
    "Enrollment",
    "Submission",
    "Review",
    "Certificate",
    "extract_youtube_id",
    "slugify",
    "ensure_admin_user",
    "ensure_default_courses",
    "Question",
    "TestDefinition",
    "TestPack",
    "TestAttempt",
    "UserEntitlement",
    "ensure_default_test_series",
]
