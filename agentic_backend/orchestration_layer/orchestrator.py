# orchestrator.py

from agent_layer.responder import generate_agent_reply
from governance_layer.rule_engine import RuleEngine
from governance_layer.audit_logger import AuditLogger
from governance_layer.intervention import InterventionHandler
from governance_layer.websocket_routes import get_connection
from sqlalchemy.orm import Session
from memory_layer.db import get_db
from memory_layer.models import FlaggedResponse
import asyncio

engine = RuleEngine()
logger = AuditLogger()
intervention = InterventionHandler()


async def orchestrate_response(message: str, conversation_id: str) -> str:
    # Step 1: Check user input
    user_check = engine.check(response=message)
    logger.log(
        response=message,
        decision=user_check["decision"],
        reason=user_check["reason"],
        metadata={
            "source": "mobile_user",
            "conversation_id": conversation_id,
            "from": "user",
        },
    )
    if user_check["decision"] in ("needs_review", "flagged"):
        intervention.queue_for_review(
            response=message,
            reason=user_check["reason"],
            metadata={
                "source": "mobile_user",
                "conversation_id": conversation_id,
                "from": "user",
            },
        )

        # ✅ NEW: Save flagged user input to DB
        try:
            db: Session = next(get_db())
            user_flag = FlaggedResponse(
                user_id=None,
                input_text=message,
                response_text="[input flagged — no response generated yet]",
                reason=user_check["reason"],
                confidence_score=0.5,
                conversation_id=conversation_id,
                context={"source": "mobile_user", "from": "user"},
            )
            db.add(user_flag)
            db.commit()
        except Exception as e:
            print(f"❌ Failed to save flagged user input: {e}")

    # Step 2: Generate agent reply
    reply = await generate_agent_reply(message)

    # Step 3: Check agent output
    result = engine.check(response=reply)
    logger.log(
        response=reply,
        decision=result["decision"],
        reason=result["reason"],
        metadata={
            "source": "mobile_app",
            "conversation_id": conversation_id,
            "from": "agent",
        },
    )

    if result["decision"] in ("needs_review", "flagged"):
        intervention.queue_for_review(
            response=reply,
            reason=result["reason"],
            metadata={
                "source": "mobile_app",
                "conversation_id": conversation_id,
                "from": "agent",
            },
        )

        # Save flagged agent reply to DB
        try:
            db: Session = next(get_db())
            flag = FlaggedResponse(
                user_id=None,
                input_text=message,
                response_text=reply,
                reason=result["reason"],
                confidence_score=0.5,
                conversation_id=conversation_id,
                context={"source": "mobile_app", "from": "agent"},
            )
            db.add(flag)
            db.commit()
        except Exception as e:
            print(f"❌ Failed to save flagged agent response: {e}")
            return "Internal error saving flagged message."

        return "Thank you! A supervisor is reviewing this reply."

    # Step 4: Push approved reply to WebSocket if connected
    websocket = get_connection(conversation_id)
    if websocket:
        try:
            asyncio.create_task(websocket.send_text(reply))
            print(f"📤 Sent agent reply to WebSocket: {conversation_id}")
        except Exception as e:
            print(f"❌ WebSocket send failed: {e}")

    return reply
