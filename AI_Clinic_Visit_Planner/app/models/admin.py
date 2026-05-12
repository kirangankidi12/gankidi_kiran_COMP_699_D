from app import db
from datetime import datetime


class SystemAdmin(db.Model):
    __tablename__ = "system_admin"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,   # one user = one admin
        index=True
    )

    access_level = db.Column(db.String(50), default="SUPER")  
    # SUPER / MODERATOR (future flexibility)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- METHODS ----------------
    def is_super_admin(self):
        return self.access_level == "SUPER"

    def can_manage_users(self):
        return True  # can extend later

    def can_view_logs(self):
        return True

    def can_manage_system(self):
        return self.is_super_admin()

    def downgrade(self):
        self.access_level = "MODERATOR"

    def promote(self):
        self.access_level = "SUPER"

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<SystemAdmin UserID={self.user_id} Level={self.access_level}>"