class ConfidenceEstimator:
    def from_logprobs(self, logprobs: list[float]) -> float:
        """
        Estimate confidence using average token log-probabilities.

        Args:
            logprobs: A list of token-level log probabilities from the language model.

        Returns:
            A normalized confidence score between 0 and 1.
        """
        if not logprobs:
            return 0.0
        avg_logprob = sum(logprobs) / len(logprobs)
        # Normalize: typical logprobs range from -0.1 (very confident) to -5.0 (very uncertain)
        normalized = max(0.0, min(1.0, 1 + (avg_logprob / 5)))
        return round(normalized, 3)

    def from_classifier(self, classifier_score: float) -> float:
        """
        Directly use a classifier's trust or helpfulness score.

        Args:
            classifier_score: Float from 0.0 (untrustworthy) to 1.0 (trustworthy).

        Returns:
            The same score, validated within [0, 1].
        """
        return max(0.0, min(1.0, classifier_score))

    def from_heuristics(self, response: str) -> float:
        """
        Estimate confidence from linguistic and structural patterns.

        Args:
            response: The agent's textual output.

        Returns:
            Heuristic confidence score.
        """
        response_lower = response.lower()
        low_confidence_keywords = [
            "i think",
            "maybe",
            "not sure",
            "guess",
            "probably",
            "possibly",
        ]
        high_confidence_keywords = [
            "certainly",
            "definitely",
            "clearly",
            "without a doubt",
        ]

        if any(kw in response_lower for kw in low_confidence_keywords):
            return 0.4
        elif any(kw in response_lower for kw in high_confidence_keywords):
            return 0.85
        elif len(response.split()) < 5:
            return 0.5
        elif len(response.split()) > 30:
            return 0.9
        else:
            return 0.7
