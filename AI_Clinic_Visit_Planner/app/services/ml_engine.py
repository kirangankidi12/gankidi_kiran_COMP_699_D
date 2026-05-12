import pickle
import os
import numpy as np
import re


class MLEngine:
    def __init__(self):
        self.model = None
        self.model_path = os.path.join("app", "services", "rf_model.pkl")
        self.load_model()

        # Critical symptoms (must always be high risk)
        self.critical_keywords = [
            "chest pain",
            "breathing difficulty",
            "shortness of breath"
        ]

    # ---------------- LOAD MODEL ----------------
    def load_model(self):
        try:
            if os.path.exists(self.model_path):
                with open(self.model_path, "rb") as f:
                    self.model = pickle.load(f)
            else:
                self.model = None
        except Exception:
            self.model = None

    # ---------------- TEXT CLEANING ----------------
    def normalize_text(self, text):
        if not text:
            return ""
        return text.lower().strip()

    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text)

    # ---------------- CRITICAL CHECK ----------------
    def has_critical_condition(self, text):
        for keyword in self.critical_keywords:
            if keyword in text:
                return True
        return False

    # ---------------- FEATURE EXTRACTION ----------------
    def extract_features(self, symptom_text, duration, age, history_factor):

        text = self.normalize_text(symptom_text)
        words = self.tokenize(text)

        # 🔥 FIX 1: Limit keyword influence (prevent inflation)
        keyword_score = min(len(words), 5)

        # 🔥 FIX 2: Balanced duration scoring
        duration_map = {
            "1 day": 1,
            "2 days": 1,
            "3 days": 2,
            "1 week": 3,
            "2 weeks": 4,
            "chronic": 5
        }
        duration_score = duration_map.get(duration.lower(), 1) if duration else 1

        # 🔥 FIX 3: Normalize age (VERY IMPORTANT)
        try:
            age = int(age)
            age_score = age / 50   # scale down (0–2 range approx)
        except:
            age_score = 1

        # 🔥 FIX 4: Normalize history factor
        try:
            history_factor = int(history_factor)
            history_score = history_factor * 1.2
        except:
            history_score = 1

        return np.array([[keyword_score, duration_score, age_score, history_score]])

    # ---------------- PREDICTION ----------------
    def predict(self, features, symptom_text):

        text = self.normalize_text(symptom_text)

        # 🔴 HARD SAFETY RULE
        if self.has_critical_condition(text):
            return "High"

        try:
            if self.model:
                prediction = self.model.predict(features)[0]
            else:
                prediction = self.fallback_logic(features)
        except Exception:
            prediction = self.fallback_logic(features)

        # Safety check
        if prediction not in ["Low", "Medium", "High"]:
            prediction = "Low"

        return prediction

    # ---------------- FALLBACK LOGIC ----------------
    def fallback_logic(self, features):
        """
        Balanced scoring aligned with RiskCalculator
        """

        score = float(sum(features[0]))

        # 🔥 FINAL CALIBRATED THRESHOLDS
        if score < 6:
            return "Low"
        elif score < 10:
            return "Medium"
        else:
            return "High"

    # ---------------- MAIN CLASSIFIER ----------------
    def classify(self, symptom_text, duration, age, history_factor):
        features = self.extract_features(symptom_text, duration, age, history_factor)
        return self.predict(features, symptom_text)