from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_layer.agent_controller import router as agent_router
from governance_layer.api import router as governance_router
from governance_layer.websocket_routes import router as websocket_router
from interface_layer.api import router as user_router

from memory_layer.models import Base
from memory_layer.db import engine

app = FastAPI(
    title="Agentic AI Companion API",
    description="Backend service for the elderly companion agent",
    version="0.1.0",
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(agent_router, prefix="/agent")
app.include_router(governance_router, prefix="/governance")
app.include_router(websocket_router)  # WebSocket route: /ws/{conversation_id}
app.include_router(user_router)  # User routes, no prefix

# Initialize DB tables
Base.metadata.create_all(bind=engine)
