from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict
from sqlalchemy.orm import Session
from datetime import datetime
import asyncio

from memory_layer.db import get_db
from memory_layer.models import FlaggedResponse

router = APIRouter()

# ----------------------
# WebSocket management
# ----------------------
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    active_connections[conversation_id] = websocket
    print(f"✅ WebSocket connection open: {conversation_id}")
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        del active_connections[conversation_id]
        print(f"❌ WebSocket disconnected: {conversation_id}")


# ----------------------
# Schemas
# ----------------------
class FlaggedInput(BaseModel):
    user_id: Optional[int]
    input_text: str
    response_text: str
    reason: str
    confidence_score: Optional[float] = None
    context: Optional[dict] = None
    conversation_id: Optional[str] = None


class ReviewDecisionRequest(BaseModel):
    decision: str  # approved, rejected, or edited
    replacement_text: Optional[str] = None
    reviewer_id: Optional[str] = "supervisor_1"


# ----------------------
# API Endpoints
# ----------------------
@router.post("/flagged")
def create_flagged_response(flag: FlaggedInput, db: Session = Depends(get_db)):
    new_flag = FlaggedResponse(
        user_id=flag.user_id,
        input_text=flag.input_text,
        response_text=flag.response_text,
        reason=flag.reason,
        confidence_score=flag.confidence_score,
        conversation_id=flag.conversation_id,
        context=flag.context,
        status="pending",
        timestamp=datetime.utcnow(),
    )
    db.add(new_flag)
    db.commit()
    db.refresh(new_flag)
    return {"status": "success", "flag_id": new_flag.id}


@router.get("/flagged")
def get_all_flagged_responses(
    user_id: Optional[int] = None, db: Session = Depends(get_db)
):
    query = db.query(FlaggedResponse)
    if user_id:
        query = query.filter(FlaggedResponse.user_id == user_id)
    return query.order_by(FlaggedResponse.timestamp.desc()).all()


@router.post("/flagged/{flag_id}/resolve")
def resolve_flagged_response(
    flag_id: int, review: ReviewDecisionRequest, db: Session = Depends(get_db)
):
    flag = db.query(FlaggedResponse).filter(FlaggedResponse.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")

    if review.decision not in ["approved", "rejected", "edited"]:
        raise HTTPException(status_code=400, detail="Invalid decision")

    flag.status = review.decision
    if review.decision == "edited":
        if not review.replacement_text:
            raise HTTPException(
                status_code=400, detail="Edited decision requires replacement_text"
            )
        flag.replacement_text = review.replacement_text

    db.commit()
    db.refresh(flag)

    # ✅ Push to WebSocket ONLY when resolved
    conv_id = flag.conversation_id
    if conv_id and conv_id in active_connections:
        response_text = flag.replacement_text or flag.response_text
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.run_coroutine_threadsafe(
                    active_connections[conv_id].send_text(response_text), loop
                )
            else:
                loop.run_until_complete(
                    active_connections[conv_id].send_text(response_text)
                )
            print(f"📡 WebSocket pushed to {conv_id}: {response_text}")
        except Exception as e:
            print(f"❌ WebSocket send error: {e}")

    return {"status": "resolved", "flag_id": flag.id, "new_status": flag.status}


@router.get("/final-response/{conversation_id}")
def get_final_response(conversation_id: str, db: Session = Depends(get_db)):
    flag = (
        db.query(FlaggedResponse)
        .filter_by(conversation_id=conversation_id)
        .order_by(FlaggedResponse.id.desc())
        .first()
    )

    if not flag:
        return {"reply": "Still under review."}

    if flag.status == "approved":
        return {"reply": flag.response_text}

    if flag.status == "edited" and flag.replacement_text:
        return {"reply": flag.replacement_text}

    if flag.status == "rejected":
        return {"reply": "This message has been rejected by a supervisor."}

    return {"reply": "Still under review."}
