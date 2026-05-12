class RuleEngine:

    def __init__(self):
        # 🔹 Standardized guidance mapping
        self.guidelines = {
            "Low": {
                "care": "Self-care at home",
                "explanation": (
                    "Your symptoms appear mild. It is recommended to rest, stay hydrated, "
                    "and monitor your condition. If symptoms persist or worsen, seek medical advice."
                )
            },
            "Medium": {
                "care": "Visit a clinic",
                "explanation": (
                    "Your symptoms suggest a moderate health condition. It is advisable to consult "
                    "a healthcare professional for proper evaluation and treatment."
                )
            },
            "High": {
                "care": "Go to hospital immediately",
                "explanation": (
                    "Your symptoms may indicate a serious or urgent condition. Immediate medical "
                    "attention is strongly recommended to prevent complications."
                )
            }
        }

    # ---------------- VALIDATION ----------------
    def is_valid_urgency(self, urgency):
        return urgency in self.guidelines

    # ---------------- NORMALIZATION ----------------
    def normalize(self, urgency):
        if not urgency:
            return None
        return str(urgency).strip().capitalize()

    # ---------------- MAIN GUIDANCE ----------------
    def generate_guidance(self, urgency):
        """
        Convert urgency level into human-readable recommendation
        """

        urgency = self.normalize(urgency)

        if not urgency or not self.is_valid_urgency(urgency):
            return self.default_response()

        return self.guidelines[urgency]

    # ---------------- DEFAULT RESPONSE ----------------
    def default_response(self):
        return {
            "care": "Consult a healthcare provider",
            "explanation": (
                "We could not determine a clear recommendation based on the provided input. "
                "Please consult a qualified medical professional for further guidance."
            )
        }

    # ---------------- ENRICHED RESPONSE (FOR DEMO/UI) ----------------
    def enrich_with_context(self, urgency, symptom_text=None, risk_score=None):
        """
        Adds extra explanation context (useful for UI or reports)
        """

        base = self.generate_guidance(urgency)

        # Copy to avoid modifying original
        enriched = base.copy()

        if symptom_text:
            enriched["explanation"] += f"\n\nReported symptoms: {symptom_text[:60]}..."

        if risk_score is not None:
            enriched["explanation"] += f"\nRisk Score: {risk_score}"

        return enriched