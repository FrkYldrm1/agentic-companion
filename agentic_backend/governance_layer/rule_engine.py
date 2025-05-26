# governance_layer/rule_engine.py

from governance_layer.confidence_estimator import ConfidenceEstimator
import re
import logging

logger = logging.getLogger("rule_engine")
logging.basicConfig(level=logging.INFO)


class RuleEngine:
    def __init__(self, confidence_threshold=0.5):
        self.confidence_threshold = confidence_threshold
        self.estimator = ConfidenceEstimator()

        #  Use regex with word boundaries to catch exact harmful words
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

        # --- Logging ---
        logger.info(f" Agent Response: {response}")
        logger.info(f" Estimated Confidence: {confidence:.2f}")

        # --- Rule 1: Harmful or unsafe language ---
        response_lower = response.lower()
        for pattern in self.harmful_keywords:
            match = re.search(pattern, response_lower)
            if match:
                matched_word = match.group()
                logger.warning(f" Harmful keyword match: '{matched_word}'")
                return {
                    "decision": "flagged",
                    "reason": f"Harmful keyword detected: '{matched_word}'",
                }

        # --- Rule 2: Confidence too low ---
        if confidence < self.confidence_threshold:
            logger.warning(" Low confidence — needs review")
            return {
                "decision": "needs_review",
                "reason": f"Low confidence score: {confidence:.2f}",
            }

        # --- Rule 3: Passed ---
        logger.info(" Approved by rule engine")
        return {
            "decision": "approved",
            "reason": f"Passed all checks. Confidence: {confidence:.2f}",
        }
