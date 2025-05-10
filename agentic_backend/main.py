from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent_layer.agent_controller import router as agent_router
from governance_layer.api import router as governance_router
from governance_layer.websocket_routes import register_websocket_routes  # ✅ updated
from interface_layer.api import router as user_router

from memory_layer.models import Base
from memory_layer.db import engine

app = FastAPI(
    title="Agentic AI Companion API",
    description="Backend service for the elderly companion agent",
    version="0.1.0",
)

# Middleware for CORS (allow frontend or mobile app access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only – restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register RESTful API routes
app.include_router(agent_router, prefix="/agent")
app.include_router(governance_router, prefix="/governance")
app.include_router(user_router)

# Register the WebSocket route separately (not via include_router)
register_websocket_routes(app)  # ✅ properly adds /ws/{conversation_id}

# Initialize database tables
Base.metadata.create_all(bind=engine)
