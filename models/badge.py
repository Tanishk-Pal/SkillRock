from datetime import datetime
from models import db

class Badge(db.Model):
    __tablename__ = "badges"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default="award")  # e.g., 'award', 'zap', 'book-open', 'users', 'crown'
    color = db.Column(db.String(30), default="#06b6d4")  # accent color

    user_badges = db.relationship("UserBadge", back_populates="badge", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Badge {self.name}>"


class UserBadge(db.Model):
    __tablename__ = "user_badges"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    badge_id = db.Column(db.Integer, db.ForeignKey("badges.id", ondelete="CASCADE"), nullable=False)
    awarded_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="user_badges")
    badge = db.relationship("Badge", back_populates="user_badges")

    __table_args__ = (
        db.UniqueConstraint("user_id", "badge_id", name="uq_user_badge"),
    )

    def __repr__(self):
        return f"<UserBadge User:{self.user_id} Badge:{self.badge_id}>"
