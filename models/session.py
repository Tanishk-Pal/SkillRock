from datetime import datetime
from models import db

class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    connection_id = db.Column(db.Integer, db.ForeignKey("connections.id", ondelete="SET NULL"), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    learner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    
    title = db.Column(db.String(150), default="Learning Session")
    notes = db.Column(db.Text, default="")
    scheduled_date = db.Column(db.String(50), nullable=False)
    scheduled_time = db.Column(db.String(50), nullable=False)
    duration_minutes = db.Column(db.Integer, default=60)
    meeting_link = db.Column(db.String(255), default="Campus / Online")
    status = db.Column(db.String(20), default="scheduled", index=True)  # scheduled, completed, cancelled
    xp_awarded = db.Column(db.Boolean, default=False)  # backend protection against duplicate XP awards
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    connection = db.relationship("Connection", backref=db.backref("sessions", lazy="dynamic"))
    teacher = db.relationship("User", foreign_keys=[teacher_id], backref=db.backref("teaching_sessions", lazy="dynamic"))
    learner = db.relationship("User", foreign_keys=[learner_id], backref=db.backref("learning_sessions", lazy="dynamic"))
    skill = db.relationship("Skill")
    ratings = db.relationship("Rating", back_populates="session", cascade="all, delete-orphan")

    def has_rated(self, user_id):
        return any(r.reviewer_id == user_id for r in self.ratings)

    def __repr__(self):
        return f"<Session {self.id}: {self.title} ({self.status})>"


class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = db.Column(db.Integer, nullable=False)  # 1 to 5
    feedback = db.Column(db.Text, default="")
    xp_awarded = db.Column(db.Boolean, default=False)  # backend protection against duplicate 5-star XP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    session = db.relationship("Session", back_populates="ratings")
    reviewer = db.relationship("User", foreign_keys=[reviewer_id], backref=db.backref("given_ratings", lazy="dynamic"))
    reviewee = db.relationship("User", foreign_keys=[reviewee_id], backref=db.backref("received_ratings", lazy="dynamic"))

    __table_args__ = (
        db.UniqueConstraint("session_id", "reviewer_id", name="uq_session_reviewer"),
    )

    def __repr__(self):
        return f"<Rating {self.id}: {self.score} stars from {self.reviewer_id} to {self.reviewee_id}>"
