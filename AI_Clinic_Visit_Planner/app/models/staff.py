from app import db
from datetime import datetime


class ClinicStaff(db.Model):
    __tablename__ = "clinic_staff"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,   # one user = one staff profile
        index=True
    )

    role = db.Column(db.String(50))  # nurse, receptionist, etc.
    is_approved = db.Column(db.Boolean, default=False)

    # Availability
    services = db.Column(db.Text)
    operating_hours = db.Column(db.String(100))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- METHODS ----------------
    def approve(self):
        self.is_approved = True

    def revoke(self):
        self.is_approved = False

    def update_availability(self, services=None, hours=None):
        if services is not None:
            self.services = services

        if hours is not None:
            self.operating_hours = hours

    def has_availability(self):
        return bool(self.services and self.operating_hours)

    def is_active(self):
        return self.is_approved

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<ClinicStaff UserID={self.user_id} Approved={self.is_approved}>"