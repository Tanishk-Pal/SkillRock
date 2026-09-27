from datetime import datetime
from models import db

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, default="General")
    description = db.Column(db.String(255), nullable=True)
    icon = db.Column(db.String(50), default="code")

    user_skills = db.relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Skill {self.name} ({self.category})>"


class UserSkill(db.Model):
    __tablename__ = "user_skills"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id", ondelete="CASCADE"), nullable=False)
    skill_type = db.Column(db.String(10), nullable=False)  # 'teach' or 'learn'
    proficiency = db.Column(db.String(20), default="Intermediate")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    __table_args__ = (
        db.UniqueConstraint("user_id", "skill_id", "skill_type", name="uq_user_skill_type"),
    )

    def __repr__(self):
        return f"<UserSkill User:{self.user_id} Skill:{self.skill_id} Type:{self.skill_type}>"
