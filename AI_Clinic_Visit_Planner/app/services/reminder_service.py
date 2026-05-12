from datetime import datetime
from app import db
from app.models.reminder import Reminder


class ReminderService:

    # ---------------- VALIDATION ----------------
    def _is_valid_future_time(self, reminder_time):
        try:
            return reminder_time and reminder_time > datetime.utcnow()
        except:
            return False

    # ---------------- CREATE ----------------
    def create_reminder(self, patient_id, reminder_time):
        """
        Create a new reminder (only future times allowed)
        """

        if not patient_id:
            return None

        if not self._is_valid_future_time(reminder_time):
            return None

        try:
            reminder = Reminder(
                patient_id=patient_id,
                reminder_time=reminder_time,
                is_active=True
            )

            db.session.add(reminder)
            db.session.commit()

            return reminder

        except Exception:
            db.session.rollback()
            return None

    # ---------------- CANCEL ----------------
    def cancel_reminder(self, reminder_id, patient_id=None):
        """
        Cancel reminder safely (with optional ownership check)
        """

        reminder = Reminder.query.get(reminder_id)

        if not reminder:
            return None

        # 🔐 Ownership protection (important)
        if patient_id and reminder.patient_id != patient_id:
            return None

        try:
            reminder.is_active = False
            db.session.commit()
            return reminder

        except Exception:
            db.session.rollback()
            return None

    # ---------------- GET ACTIVE ----------------
    def get_active_reminders(self, patient_id):
        return Reminder.query.filter_by(
            patient_id=patient_id,
            is_active=True
        ).order_by(Reminder.reminder_time.asc()).all()

    # ---------------- GET ALL ----------------
    def get_all_reminders(self, patient_id):
        return Reminder.query.filter_by(
            patient_id=patient_id
        ).order_by(Reminder.reminder_time.desc()).all()

    # ---------------- GET UPCOMING ----------------
    def get_upcoming_reminders(self, patient_id, limit=5):
        now = datetime.utcnow()

        return Reminder.query.filter(
            Reminder.patient_id == patient_id,
            Reminder.reminder_time > now,
            Reminder.is_active == True
        ).order_by(Reminder.reminder_time.asc()).limit(limit).all()

    # ---------------- TRIGGER CHECK ----------------
    def check_due_reminders(self):
        """
        Simulate reminder triggering (cron-like behavior)
        """

        now = datetime.utcnow()

        due_reminders = Reminder.query.filter(
            Reminder.reminder_time <= now,
            Reminder.is_active == True
        ).all()

        triggered = []

        for reminder in due_reminders:
            reminder.is_active = False
            triggered.append(reminder)

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        return triggered

    # ---------------- CLEANUP ----------------
    def deactivate_expired(self):
        """
        Deactivate old reminders (maintenance)
        """

        now = datetime.utcnow()

        expired = Reminder.query.filter(
            Reminder.reminder_time < now,
            Reminder.is_active == True
        ).all()

        count = 0

        for reminder in expired:
            reminder.is_active = False
            count += 1

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        return count

    # ---------------- FORMAT HELPER ----------------
    def format_reminder(self, reminder):
        """
        Convert reminder to readable dictionary (useful for APIs/UI)
        """
        return {
            "id": reminder.id,
            "time": reminder.reminder_time.strftime("%Y-%m-%d %H:%M"),
            "active": reminder.is_active
        }