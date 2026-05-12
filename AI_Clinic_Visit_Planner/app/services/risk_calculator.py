import re


class RiskCalculator:

    def __init__(self):
        # Symptom weights (balanced)
        self.symptom_weights = {
            "fever": 2,
            "cough": 1.2,
            "pain": 2.5,
            "chest": 4,
            "breathing": 4,
            "shortness": 3.5,
            "headache": 1,
            "vomiting": 2.5,
            "dizziness": 2,
            "fatigue": 1.2,
            "tiredness": 1.0,
            "weakness": 1.0,
            "infection": 3
        }

        # Intensity modifiers
        self.intensity_modifiers = {
            "mild": 0.5,
            "slight": 0.5,
            "moderate": 1.0,
            "severe": 1.6,
            "extreme": 2.0
        }

        # Critical keywords
        self.critical_keywords = [
            "chest pain",
            "breathing difficulty",
            "shortness of breath"
        ]

    # ---------------- NORMALIZATION ----------------
    def normalize_text(self, text):
        if not text:
            return ""
        return text.lower().strip()

    # ---------------- TOKENIZATION ----------------
    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text)

    # ---------------- INTENSITY FACTOR ----------------
    def get_intensity_factor(self, words):
        factor = 1.0
        for word in words:
            if word in self.intensity_modifiers:
                # pick lowest modifier if multiple (mild + slight etc.)
                factor = min(factor, self.intensity_modifiers[word])
        return factor

    # ---------------- CRITICAL DETECTION ----------------
    def has_critical_condition(self, text):
        for keyword in self.critical_keywords:
            if keyword in text:
                return True
        return False

    # ---------------- SEVERITY ----------------
    def extract_severity(self, symptom_text):

        text = self.normalize_text(symptom_text)
        words = self.tokenize(text)

        base_severity = 0
        symptom_count = 0

        for word in words:
            if word in self.symptom_weights:
                base_severity += self.symptom_weights[word]
                symptom_count += 1

        # If no known symptoms
        if base_severity == 0:
            base_severity = 0.8

        intensity_factor = self.get_intensity_factor(words)

        # 🔥 KEY FIX: reduce severity when multiple mild symptoms
        if intensity_factor <= 0.6 and symptom_count <= 2:
            base_severity *= 0.6

        severity = base_severity * intensity_factor

        # Cap severity
        severity = min(severity, 7)

        return round(severity, 2)

    # ---------------- RISK SCORE ----------------
    def calculate(self, symptom_text, history_factor):

        text = self.normalize_text(symptom_text)

        try:
            history_factor = int(history_factor)
        except:
            history_factor = 1

        severity = self.extract_severity(symptom_text)

        # Balanced formula
        risk_score = (severity * 1.0) + (history_factor * 1.2)

        # Critical override
        if self.has_critical_condition(text):
            risk_score = max(risk_score, 14)

        # Normalize range
        risk_score = min(risk_score, 16)

        return round(risk_score, 2), severity

    # ---------------- FINAL LEVEL ----------------
    def risk_level(self, risk_score):

        if risk_score < 5:
            return "Low"
        elif risk_score < 9:
            return "Medium"
        return "High"