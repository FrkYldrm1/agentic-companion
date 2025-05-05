from fastapi import WebSocket, WebSocketDisconnect, APIRouter

router = APIRouter()
active_connections = {}


@router.websocket("/ws/{conversation_id}")
async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
    await websocket.accept()
    active_connections[conversation_id] = websocket
    print("✅ WebSocket connection open:", conversation_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        print("❌ WebSocket disconnected:", conversation_id)
        active_connections.pop(conversation_id, None)


def get_connection(conversation_id: str):
    return active_connections.get(conversation_id)
