import unittest
from governance_layer.intervention import InterventionHandler


class TestInterventionHandler(unittest.TestCase):
    def setUp(self):
        self.handler = InterventionHandler()

    def test_queue_and_resolve_review(self):
        # Queue a fake flagged message
        review_id = self.handler.queue_for_review(
            response="This is suspicious.",
            reason="Test reason",
            metadata={"conversation_id": "test123"},
        )

        # Ensure it's in pending reviews
        pending = self.handler.get_pending_reviews()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["review_id"], review_id)
        self.assertEqual(pending[0]["status"], "pending")

        # Resolve it
        resolved = self.handler.resolve_review(
            review_id, decision="approved", reviewer_id="admin1"
        )
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(resolved["final_decision"], "approved")
        self.assertEqual(resolved["reviewed_by"], "admin1")

        # Ensure it's no longer in pending
        self.assertEqual(len(self.handler.get_pending_reviews()), 0)

    def test_resolve_invalid_id(self):
        with self.assertRaises(ValueError):
            self.handler.resolve_review("invalid_id", decision="rejected")


if __name__ == "__main__":
    unittest.main()
