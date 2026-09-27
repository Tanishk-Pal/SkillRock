from datetime import datetime
from models import db

class SwapRequest(db.Model):
    __tablename__ = "swap_requests"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    teach_skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    learn_skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)
    message = db.Column(db.Text, default="")
    status = db.Column(db.String(20), default="pending", index=True)  # pending, accepted, rejected, cancelled
    xp_awarded = db.Column(db.Boolean, default=False)  # backend protection against duplicate XP awards
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sender = db.relationship("User", foreign_keys=[sender_id], backref=db.backref("sent_requests", lazy="dynamic"))
    receiver = db.relationship("User", foreign_keys=[receiver_id], backref=db.backref("received_requests", lazy="dynamic"))
    teach_skill = db.relationship("Skill", foreign_keys=[teach_skill_id])
    learn_skill = db.relationship("Skill", foreign_keys=[learn_skill_id])

    @property
    def status_label(self):
        if self.status == "pending":
            return "Waiting"
        elif self.status == "accepted":
            return "Accepted"
        elif self.status == "rejected":
            return "Declined"
        elif self.status == "cancelled":
            return "Cancelled"
        return self.status.capitalize()

    def __repr__(self):
        return f"<SwapRequest {self.id}: {self.sender_id} -> {self.receiver_id} ({self.status})>"


class Connection(db.Model):
    __tablename__ = "connections"

    id = db.Column(db.Integer, primary_key=True)
    user1_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user2_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    swap_request_id = db.Column(db.Integer, db.ForeignKey("swap_requests.id", ondelete="SET NULL"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user1 = db.relationship("User", foreign_keys=[user1_id], backref=db.backref("connections_as_u1", lazy="dynamic"))
    user2 = db.relationship("User", foreign_keys=[user2_id], backref=db.backref("connections_as_u2", lazy="dynamic"))
    swap_request = db.relationship("SwapRequest")

    def get_other_user(self, current_user_id):
        if self.user1_id == current_user_id:
            return self.user2
        return self.user1

    def __repr__(self):
        return f"<Connection {self.id}: {self.user1_id} <-> {self.user2_id}>"
