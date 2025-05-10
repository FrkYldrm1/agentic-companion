import unittest
from unittest.mock import AsyncMock, patch
from sqlalchemy.orm import Session
from memory_layer.models import FlaggedResponse
from memory_layer.db import SessionLocal, Base, engine
from orchestration_layer.orchestrator import orchestrate_response

# Ensure the DB schema is set up
Base.metadata.create_all(bind=engine)


class TestOrchestrator(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.db: Session = SessionLocal()

    def tearDown(self):
        self.db.query(FlaggedResponse).delete()
        self.db.commit()

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    async def test_flagged_user_input_is_saved(self, mock_reply):
        # User input is harmful, agent reply is safe
        mock_reply.return_value = "This is a safe response."
        user_message = "Can you help me kill someone?"
        conversation_id = "test-user-flag"

        reply = await orchestrate_response(user_message, conversation_id)
        self.assertTrue(reply)

        flagged = (
            self.db.query(FlaggedResponse)
            .filter_by(conversation_id=conversation_id)
            .order_by(FlaggedResponse.id.desc())
            .first()
        )
        self.assertIsNotNone(flagged)
        self.assertIn("kill", flagged.input_text)
        print(f"✅ User input flagged and saved: {flagged.input_text}")

    @patch(
        "orchestration_layer.orchestrator.generate_agent_reply", new_callable=AsyncMock
    )
    async def test_flagged_agent_reply_triggers_supervisor_flow(self, mock_reply):
        # User input is fine, agent reply is harmful
        mock_reply.return_value = "Sure, I can help you make a kill."
        user_message = "What should I do today?"
        conversation_id = "test-agent-flag"

        reply = await orchestrate_response(user_message, conversation_id)

        # Expect fallback response
        self.assertIn("reviewing", reply.lower())

        flagged = (
            self.db.query(FlaggedResponse)
            .filter_by(conversation_id=conversation_id)
            .order_by(FlaggedResponse.id.desc())
            .first()
        )
        self.assertIsNotNone(flagged)
        self.assertIn("kill", flagged.response_text)
        print(f"✅ Agent reply flagged and saved: {flagged.response_text}")


if __name__ == "__main__":
    unittest.main()
