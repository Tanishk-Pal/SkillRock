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

from models.roadmap import (
    RoadmapPackage,
    RoadmapProgress,
    RoadmapSubmission,
    RoadmapCashback,
    ensure_default_roadmaps
)

from models.bhavishya import (
    BhavishyaPackage,
    BhavishyaSubject,
    BhavishyaProgress,
    BhavishyaMemory,
    BhavishyaSubmission,
    BhavishyaSimulatorAttempt,
    BhavishyaCashback,
    BhavishyaUsage,
    BhavishyaBatchConfig,
    BhavishyaLiveLecture
)
from models.bhavishya_recordings import (
    BhavishyaLectureRecording,
    get_recordings_db
)
from models.default_bhavishya_curriculum import ensure_default_bhavishya_subjects
from models.default_bhavishya_live import ensure_default_bhavishya_live_batch

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
    Notification,
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
    "Notification",
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
    "RoadmapPackage",
    "RoadmapProgress",
    "RoadmapSubmission",
    "RoadmapCashback",
    "ensure_default_roadmaps",
    "BhavishyaPackage",
    "BhavishyaSubject",
    "BhavishyaProgress",
    "BhavishyaMemory",
    "BhavishyaSubmission",
    "BhavishyaSimulatorAttempt",
    "BhavishyaCashback",
    "BhavishyaUsage",
    "BhavishyaBatchConfig",
    "BhavishyaLiveLecture",
    "BhavishyaLectureRecording",
    "get_recordings_db",
    "ensure_default_bhavishya_subjects",
    "ensure_default_bhavishya_live_batch",
]
