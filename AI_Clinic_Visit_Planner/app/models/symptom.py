from app import db
from datetime import datetime


class SymptomRecord(db.Model):
    __tablename__ = "symptoms"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(
        db.Integer,
        db.ForeignKey("patients.id"),
        nullable=False,
        index=True
    )

    symptom_text = db.Column(db.Text, nullable=False)
    duration = db.Column(db.String(50))
    severity = db.Column(db.Integer, default=1)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- RELATIONSHIP ----------------
    recommendation = db.relationship(
        "Recommendation",
        backref="symptom",
        uselist=False,
        cascade="all, delete"
    )

    # ---------------- VALIDATION ----------------
    def is_valid(self):
        return bool(self.symptom_text and self.symptom_text.strip())

    # ---------------- NORMALIZATION ----------------
    def normalized_text(self):
        """
        Prepare text for ML processing
        """
        return self.symptom_text.lower().strip()

    # ---------------- FEATURE EXTRACTION ----------------
    def keyword_count(self):
        return len(self.normalized_text().split())

    # ---------------- SAFE UPDATE ----------------
    def update_severity(self, severity):
        try:
            self.severity = int(severity)
        except:
            self.severity = 1

    # ---------------- SUMMARY ----------------
    def short_text(self, length=30):
        if not self.symptom_text:
            return ""
        return (self.symptom_text[:length] + "...") if len(self.symptom_text) > length else self.symptom_text

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<SymptomRecord ID={self.id} Patient={self.patient_id}>"