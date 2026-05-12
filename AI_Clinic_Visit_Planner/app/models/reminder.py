from app import db
from datetime import datetime


class Reminder(db.Model):
    __tablename__ = "reminders"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    reminder_time = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- VALIDATION ----------------
    def is_valid_time(self):
        """
        Ensure reminder is set in the future
        """
        return self.reminder_time > datetime.utcnow()

    # ---------------- STATE ----------------
    def is_due(self):
        """
        Check if reminder time has arrived
        """
        return self.is_active and self.reminder_time <= datetime.utcnow()

    def is_expired(self):
        """
        Check if reminder is past due
        """
        return self.reminder_time < datetime.utcnow()

    # ---------------- ACTIONS ----------------
    def schedule(self, datetime_value):
        try:
            if datetime_value > datetime.utcnow():
                self.reminder_time = datetime_value
                self.is_active = True
        except:
            pass  # fail silently for safety

    def cancel(self):
        self.is_active = False

    def activate(self):
        if self.is_valid_time():
            self.is_active = True

    # ---------------- DISPLAY ----------------
    def formatted_time(self):
        return self.reminder_time.strftime("%Y-%m-%d %H:%M")

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<Reminder PatientID={self.patient_id} Active={self.is_active}>"