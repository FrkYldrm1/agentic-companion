# governance_layer/rule_engine.py

from governance_layer.confidence_estimator import ConfidenceEstimator
import re
import logging

logger = logging.getLogger("rule_engine")
logging.basicConfig(level=logging.INFO)


class RuleEngine:
    def __init__(self, confidence_threshold=0.7):
        self.confidence_threshold = confidence_threshold
        self.estimator = ConfidenceEstimator()

        # 👇 Use regex word boundaries to avoid partial matches
        self.harmful_keywords = [
            r"\bkill\b",
            r"\bsuicide\b",
            r"\bhate\b",
            r"\bracist\b",
            r"\battack\b",
        ]

    def check(
        self,
        response: str,
        confidence: float = None,
        logprobs: list[float] = None,
        classifier_score: float = None,
    ) -> dict:
        # --- Confidence Estimation ---
        if confidence is None:
            if logprobs:
                confidence = self.estimator.from_logprobs(logprobs)
            elif classifier_score is not None:
                confidence = self.estimator.from_classifier(classifier_score)
            else:
                confidence = self.estimator.from_heuristics(response)

        # --- Debug log ---
        logger.info(f"🧠 Agent Response: {response}")
        logger.info(f"🔢 Confidence: {confidence:.2f}")

        # --- Rule 1: Confidence too low ---
        if confidence < self.confidence_threshold:
            logger.warning("⚠️ Low confidence — needs review")
            return {
                "decision": "needs_review",
                "reason": f"Low confidence score: {confidence:.2f}",
            }

        # --- Rule 2: Harmful or unsafe language ---
        response_lower = response.lower()
        for pattern in self.harmful_keywords:
            if re.search(pattern, response_lower):
                logger.warning(f"🚨 Harmful keyword match: {pattern}")
                return {
                    "decision": "flagged",
                    "reason": "Contains harmful or unsafe language",
                }

        # --- Rule 3: Passed ---
        logger.info("✅ Approved by rule engine")
        return {
            "decision": "approved",
            "reason": f"Passed all checks. Confidence: {confidence:.2f}",
        }
