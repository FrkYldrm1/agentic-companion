import unittest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
from main import app
from memory_layer.db import SessionLocal
from memory_layer.models import FlaggedResponse

client = TestClient(app)


class TestAgenticAPI(unittest.TestCase):
    def setUp(self):
        db = SessionLocal()
        db.query(FlaggedResponse).delete()
        db.commit()
        db.close()

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_post_agent_chat_with_flagged_agent_reply(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        payload = {
            "message": "What should I do today?",
            "conversation_id": "api-test-convo-agent",
        }

        response = client.post("/agent/chat", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("reviewing", data["reply"].lower())
        print(f" Fallback triggered for flagged agent reply: {data['reply']}")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_get_flagged_responses(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        client.post(
            "/agent/chat",
            json={
                "message": "Just wondering what to do today.",
                "conversation_id": "api-test-convo-get",
            },
        )

        response = client.get("/governance/flagged")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertGreaterEqual(len(data), 1)
        print(f" Retrieved {len(data)} flagged response(s)")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_supervisor_can_resolve_flag(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        convo_id = "api-test-convo-resolve"

        post_res = client.post(
            "/agent/chat",
            json={"message": "Is it ok to ask this?", "conversation_id": convo_id},
        )
        self.assertEqual(post_res.status_code, 200)

        flagged_res = client.get("/governance/flagged")
        data = flagged_res.json()
        flag = next((f for f in data if f["conversation_id"] == convo_id), None)
        self.assertIsNotNone(flag)

        resolve_res = client.post(
            f"/governance/flagged/{flag['id']}/resolve",
            json={
                "decision": "edited",
                "replacement_text": "Let's find a positive way to help.",
            },
        )

        self.assertEqual(resolve_res.status_code, 200)
        print(f" Supervisor resolved flag ID {flag['id']} with edited response.")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_final_response_returns_edited_text(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        convo_id = "api-test-final-response"

        client.post(
            "/agent/chat",
            json={
                "message": "Can we do something dangerous?",
                "conversation_id": convo_id,
            },
        )

        flagged_res = client.get("/governance/flagged")
        data = flagged_res.json()
        flag = next((f for f in data if f["conversation_id"] == convo_id), None)
        self.assertIsNotNone(flag)

        client.post(
            f"/governance/flagged/{flag['id']}/resolve",
            json={
                "decision": "edited",
                "replacement_text": "Let's do something fun and safe instead.",
            },
        )

        final = client.get(f"/governance/final-response/{convo_id}")
        self.assertEqual(final.status_code, 200)
        result = final.json()
        self.assertEqual(result["reply"], "Let's do something fun and safe instead.")
        print(f" Final response delivered: {result['reply']}")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_final_response_returns_approved_text(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        convo_id = "api-test-final-approved"

        client.post(
            "/agent/chat",
            json={"message": "Should we do this?", "conversation_id": convo_id},
        )

        flagged_res = client.get("/governance/flagged")
        data = flagged_res.json()
        flag = next((f for f in data if f["conversation_id"] == convo_id), None)
        self.assertIsNotNone(flag)

        client.post(
            f"/governance/flagged/{flag['id']}/resolve", json={"decision": "approved"}
        )

        final = client.get(f"/governance/final-response/{convo_id}")
        self.assertEqual(final.status_code, 200)
        result = final.json()
        self.assertEqual(result["reply"], flag["response_text"])
        print(f" Final response (approved) returned: {result['reply']}")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    def test_final_response_returns_rejection_message(self, mock_reply):
        mock_reply.return_value = "Sure, I can help you make a kill."
        convo_id = "api-test-final-rejected"

        # Trigger flag
        client.post(
            "/agent/chat",
            json={"message": "Should I be asking this?", "conversation_id": convo_id},
        )

        # Fetch flag for the current convo
        flagged_res = client.get("/governance/flagged")
        flags = flagged_res.json()
        flag = next((f for f in flags if f["conversation_id"] == convo_id), None)
        self.assertIsNotNone(flag, "❌ No flagged message found for conversation")

        # Resolve it as rejected
        resolve_res = client.post(
            f"/governance/flagged/{flag['id']}/resolve", json={"decision": "rejected"}
        )
        self.assertEqual(resolve_res.status_code, 200)

        # Get final response
        final = client.get(f"/governance/final-response/{convo_id}")
        self.assertEqual(final.status_code, 200)
        result = final.json()
        self.assertIn(
            "rejected",
            result["reply"].lower(),
            f" Final reply was: {result['reply']}",
        )
        print(f" Final response (rejected) returned: {result['reply']}")


if __name__ == "__main__":
    unittest.main()
