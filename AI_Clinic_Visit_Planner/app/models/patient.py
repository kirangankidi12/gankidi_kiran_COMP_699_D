from app import db
from datetime import datetime


class Patient(db.Model):
    __tablename__ = "patients"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        unique=True,   # one user = one patient
        index=True
    )

    age = db.Column(db.Integer)
    health_info = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- RELATIONSHIPS ----------------
    symptoms = db.relationship(
        "SymptomRecord",
        backref="patient",
        cascade="all, delete",
        order_by="desc(SymptomRecord.created_at)"
    )

    reminders = db.relationship(
        "Reminder",
        backref="patient",
        cascade="all, delete",
        order_by="desc(Reminder.reminder_time)"
    )

    # ---------------- METHODS ----------------
    def update_profile(self, age=None, health_info=None):
        if age:
            try:
                self.age = int(age)
            except:
                pass  # ignore invalid input safely

        if health_info is not None:
            self.health_info = health_info

    def get_recent_symptoms(self, limit=5):
        return self.symptoms[:limit]

    def get_active_reminders(self):
        return [r for r in self.reminders if r.is_active]

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<Patient UserID={self.user_id}>"