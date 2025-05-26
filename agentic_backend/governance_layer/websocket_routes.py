from fastapi import WebSocket, WebSocketDisconnect, FastAPI

# Dictionary to track active WebSocket connections
active_connections = {}


# Function to register the WebSocket endpoint directly on the FastAPI app
def register_websocket_routes(app: FastAPI):
    @app.websocket("/ws/{conversation_id}")
    async def websocket_endpoint(websocket: WebSocket, conversation_id: str):
        await websocket.accept()
        active_connections[conversation_id] = websocket
        print("WebSocket connection open:", conversation_id)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            print(" WebSocket disconnected:", conversation_id)
            active_connections.pop(conversation_id, None)


# Utility to retrieve a connection by conversation ID
def get_connection(conversation_id: str):
    return active_connections.get(conversation_id)
