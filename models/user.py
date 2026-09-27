from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    college = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(50), nullable=False)
    bio = db.Column(db.Text, default="Passionate student eager to exchange skills and collaborate.")
    avatar_seed = db.Column(db.String(100), nullable=True)
    xp = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user_skills = db.relationship("UserSkill", back_populates="user", cascade="all, delete-orphan", lazy="dynamic")
    user_badges = db.relationship("UserBadge", back_populates="user", cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def level_name(self):
        if self.xp < 100:
            return "Beginner"
        elif self.xp < 250:
            return "Learner"
        elif self.xp < 500:
            return "Skill Builder"
        elif self.xp < 1000:
            return "Knowledge Sharer"
        else:
            return "Skill Mentor"

    @property
    def level_tier(self):
        if self.xp < 100:
            return 1
        elif self.xp < 250:
            return 2
        elif self.xp < 500:
            return 3
        elif self.xp < 1000:
            return 4
        else:
            return 5

    @property
    def next_level_xp(self):
        if self.xp < 100:
            return 100
        elif self.xp < 250:
            return 250
        elif self.xp < 500:
            return 500
        elif self.xp < 1000:
            return 1000
        else:
            return 1000

    @property
    def level_progress_percent(self):
        if self.xp < 100:
            return max(0, min(100, int((self.xp / 100) * 100)))
        elif self.xp < 250:
            return max(0, min(100, int(((self.xp - 100) / 150) * 100)))
        elif self.xp < 500:
            return max(0, min(100, int(((self.xp - 250) / 250) * 100)))
        elif self.xp < 1000:
            return max(0, min(100, int(((self.xp - 500) / 500) * 100)))
        else:
            return 100

    @property
    def level_progress_display(self):
        if self.xp >= 1000:
            return f"{self.xp} XP • Maximum level reached"
        return f"{self.xp} / {self.next_level_xp} XP"

    @property
    def rating_display(self):
        if not self.rating_count or self.rating_count == 0:
            return "New member • No ratings yet"
        return f"★ {self.rating:.1f} ({self.rating_count} ratings)"

    @property
    def has_ratings(self):
        return bool(self.rating_count and self.rating_count > 0)

    @property
    def teaching_skills(self):
        return [us.skill for us in self.user_skills.filter_by(skill_type="teach").all()]

    @property
    def learning_skills(self):
        return [us.skill for us in self.user_skills.filter_by(skill_type="learn").all()]

    @property
    def badges(self):
        return [ub.badge for ub in self.user_badges]

    @property
    def initials(self):
        parts = self.name.strip().split()
        if not parts:
            return "S"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    @property
    def avatar_url(self):
        seed = self.avatar_seed or self.name.replace(" ", "_")
        return f"https://api.dicebear.com/7.x/notionists/svg?seed={seed}&backgroundColor=e2e8f0,cbd5e1,f1f5f9"

    def __repr__(self):
        return f"<User {self.email} - {self.name}>"
