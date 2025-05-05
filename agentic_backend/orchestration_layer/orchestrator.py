# orchestrator.py

from agent_layer.responder import generate_agent_reply
from governance_layer.rule_engine import RuleEngine
from governance_layer.audit_logger import AuditLogger
from governance_layer.intervention import InterventionHandler
from sqlalchemy.orm import Session
from memory_layer.db import get_db
from memory_layer.models import FlaggedResponse

engine = RuleEngine()
logger = AuditLogger()
intervention = InterventionHandler()


async def orchestrate_response(message: str, conversation_id: str) -> str:
    # Check user input
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

    # Generate agent reply
    reply = await generate_agent_reply(message)

    # Check agent output
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

        # Save to DB
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
            print(f"❌ Failed to save flagged response: {e}")
            return "Internal error saving flagged message."

        return "Thank you! A supervisor is reviewing this reply."

    return reply
