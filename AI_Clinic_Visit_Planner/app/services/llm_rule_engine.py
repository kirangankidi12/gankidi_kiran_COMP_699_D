import re

class LLMRuleEngine:
    """
    Lightweight LLM-style reasoning engine.
    Uses pattern matching, context understanding, and semantic grouping.
    """

    def __init__(self):

        # 🔹 Semantic symptom groups
        self.semantic_groups = {
            "cardiac": ["chest", "heart", "left side", "pressure"],
            "respiratory": ["breathing", "breath", "lungs", "shortness"],
            "pain": ["pain", "ache", "discomfort"],
            "general": ["fatigue", "weakness", "tired", "dizziness"]
        }

        # 🔴 Critical patterns (LLM-like reasoning)
        self.critical_patterns = [
            ["pain", "chest"],
            ["pain", "heart"],
            ["breathing", "difficulty"],
            ["shortness", "breath"]
        ]

    # ---------------- NORMALIZE ----------------
    def normalize(self, text):
        if not text:
            return ""
        return text.lower().strip()

    # ---------------- TOKENIZE ----------------
    def tokenize(self, text):
        return re.findall(r'\b\w+\b', text)

    # ---------------- CONTEXT DETECTION ----------------
    def detect_context(self, text):
        words = self.tokenize(text)
        context_hits = {}

        for category, keywords in self.semantic_groups.items():
            for word in words:
                if word in keywords:
                    context_hits[category] = context_hits.get(category, 0) + 1

        return context_hits

    # ---------------- CRITICAL REASONING ----------------
    def is_critical(self, text):
        words = self.tokenize(text)

        for pattern in self.critical_patterns:
            if all(p in words for p in pattern):
                return True

        return False

    # ---------------- FINAL ANALYSIS ----------------
    def analyze(self, symptom_text):
        text = self.normalize(symptom_text)

        context = self.detect_context(text)

        # 🔴 Critical override
        if self.is_critical(text):
            return "High", "Possible serious condition detected based on symptom combination."

        # Context-based reasoning
        if "cardiac" in context and "pain" in context:
            return "High", "Symptoms indicate possible cardiac involvement."

        if "respiratory" in context:
            return "High", "Breathing-related symptoms detected."

        if "pain" in context and context["pain"] > 1:
            return "Medium", "Multiple pain-related symptoms observed."

        if "general" in context:
            return "Low", "General mild symptoms detected."

        return "Low", "No strong indicators of severe condition."