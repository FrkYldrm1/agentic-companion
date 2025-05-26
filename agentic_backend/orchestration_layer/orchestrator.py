from agent_layer.responder import generate_agent_reply
from governance_layer.rule_engine import RuleEngine
from governance_layer.audit_logger import AuditLogger
from governance_layer.intervention import InterventionHandler
from memory_layer.db import SessionLocal
from memory_layer.models import FlaggedResponse
from sqlalchemy.exc import SQLAlchemyError
import traceback

engine = RuleEngine()
logger = AuditLogger()
intervention = InterventionHandler()


async def orchestrate_response(message: str, conversation_id: str) -> str:
    print(f" [START] Received user message: {message}")

    # Step 1: Governance check on user input
    user_check = engine.check(response=message)
    print(f" [CHECK] User input decision: {user_check}")

    logger.log(
        response=message,
        decision=user_check["decision"],
        reason=user_check["reason"],
        metadata={"conversation_id": conversation_id, "from": "user"},
    )

    if user_check["decision"] in ("needs_review", "flagged"):
        print(" [ACTION] User input flagged. Queuing for review...")
        intervention.queue_for_review(message, user_check["reason"], {"from": "user"})

        try:
            with SessionLocal() as db:
                user_flag = FlaggedResponse(
                    user_id=None,
                    input_text=message,
                    response_text="[input flagged — no response generated yet]",
                    reason=user_check["reason"],
                    confidence_score=0.5,
                    conversation_id=conversation_id,
                    context={"source": "mobile_user", "from": "user"},
                    status="pending",
                )
                db.add(user_flag)
                db.commit()
        except SQLAlchemyError:
            print("Failed to save flagged user input:")
            traceback.print_exc()

    # Step 2: Agent reply
    reply = await generate_agent_reply(message)
    print(f"[REPLY] Agent generated: {reply}")

    # Step 3: Governance check on agent reply
    result = engine.check(response=reply)
    print(f" [CHECK] Agent reply decision: {result}")

    logger.log(
        response=reply,
        decision=result["decision"],
        reason=result["reason"],
        metadata={"conversation_id": conversation_id, "from": "agent"},
    )

    if result["decision"] in ("needs_review", "flagged"):
        print(" [ACTION] Agent reply flagged. Queuing for review...")
        intervention.queue_for_review(reply, result["reason"], {"from": "agent"})

        try:
            with SessionLocal() as db:
                flag = FlaggedResponse(
                    user_id=None,
                    input_text=message,
                    response_text=reply,
                    reason=result["reason"],
                    confidence_score=0.5,
                    conversation_id=conversation_id,
                    context={"source": "mobile_app", "from": "agent"},
                    status="pending",
                )
                db.add(flag)
                db.commit()
        except SQLAlchemyError:
            print(" Failed to save flagged agent response:")
            traceback.print_exc()
            return "Internal error saving flagged message."

        return "This topic deserves a careful answer. I am going to share it with someone more experienced so we can give you the best support."

    #  Step 4: Return the approved reply via HTTP only (no WebSocket)
    print(f" [RETURN] Returning reply to HTTP: {reply}")
    return reply
