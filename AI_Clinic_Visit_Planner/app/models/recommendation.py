from app import db
from datetime import datetime


class Recommendation(db.Model):
    __tablename__ = "recommendations"

    # ---------------- PRIMARY ----------------
    id = db.Column(db.Integer, primary_key=True)

    symptom_id = db.Column(
        db.Integer,
        db.ForeignKey("symptoms.id"),
        nullable=False,
        unique=True,   # one symptom = one recommendation
        index=True
    )

    risk_score = db.Column(db.Float, default=0.0)
    urgency_level = db.Column(db.String(20))  # Low, Medium, High

    care_option = db.Column(db.String(150))
    explanation = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # ---------------- VALIDATION ----------------
    def is_valid_urgency(self):
        return self.urgency_level in ["Low", "Medium", "High"]

    # ---------------- GENERATION ----------------
    def generate(self, risk_score, urgency, guidance, explanation):
        """
        Standard method to populate recommendation safely
        """
        self.risk_score = float(risk_score)

        if urgency in ["Low", "Medium", "High"]:
            self.urgency_level = urgency
        else:
            self.urgency_level = "Low"

        self.care_option = guidance
        self.explanation = explanation

    # ---------------- FORMATTING ----------------
    def urgency_color(self):
        if self.urgency_level == "High":
            return "red"
        elif self.urgency_level == "Medium":
            return "yellow"
        return "green"

    def short_explanation(self, length=80):
        if not self.explanation:
            return ""
        return (self.explanation[:length] + "...") if len(self.explanation) > length else self.explanation

    # ---------------- STRING ----------------
    def __repr__(self):
        return f"<Recommendation SymptomID={self.symptom_id} Risk={self.urgency_level}>"