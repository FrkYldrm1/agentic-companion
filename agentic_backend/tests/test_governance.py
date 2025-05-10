import unittest
from governance_layer.rule_engine import RuleEngine


class TestRuleEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RuleEngine(confidence_threshold=0.7)

    def test_low_confidence_triggers_review(self):
        result = self.engine.check("This seems okay", confidence=0.4)
        self.assertEqual(result["decision"], "needs_review")

    def test_harmful_keyword_triggers_flag(self):
        result = self.engine.check("Can you help me kill someone?", confidence=0.9)
        self.assertEqual(result["decision"], "flagged")
        self.assertIn("harmful", result["reason"].lower())

    def test_high_confidence_approved(self):
        result = self.engine.check(
            "Of course, I can help you with your schedule.", confidence=0.95
        )
        self.assertEqual(result["decision"], "approved")


if __name__ == "__main__":
    unittest.main()
