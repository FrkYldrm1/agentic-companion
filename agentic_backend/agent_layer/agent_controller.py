from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from orchestration_layer.orchestrator import orchestrate_response
from memory_layer.models import FlaggedResponse
from sqlalchemy.orm import Session
from memory_layer.db import get_db
import traceback

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    conversation_id: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        reply = await orchestrate_response(request.message, request.conversation_id)
        print(f"🛫 [RETURNING TO CLIENT] {reply} (type: {type(reply)})")

        # Ensure it's a plain string — if not, convert it
        if not isinstance(reply, str):
            print("⚠️ Reply is not a string, converting...")
            reply = str(reply)

        return ChatResponse(reply=reply)

    except Exception as e:
        print("❌ Exception in /agent/chat:")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/final-response/{conversation_id}")
def get_final_response(conversation_id: str, db: Session = Depends(get_db)):
    flag = (
        db.query(FlaggedResponse)
        .filter(FlaggedResponse.conversation_id == conversation_id)
        .filter(FlaggedResponse.status.in_(["approved", "edited"]))
        .order_by(FlaggedResponse.timestamp.desc())
        .first()
    )

    if flag:
        print(f"✅ Final response found: status={flag.status}")
        return {"reply": flag.replacement_text or flag.response_text}

    print("⏳ Still under review.")
    return {"reply": "Still under review."}
