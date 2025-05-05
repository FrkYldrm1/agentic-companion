<# 🧠 Agentic Companion — Backend Server

This is the backend of the Agentic Companion system, designed with a modular architecture for agentic AI systems with human-in-the-loop oversight. It includes memory, orchestration, governance, and integration layers. This guide helps collaborators set up, run, and understand the project.



## 🚀 Quick Start

### 1. Clone the Repository

git clone https://github.com/yourusername/agentic-companion.git
cd agentic-companion/agentic_backend


### 2. Set Up Virtual Environment


python3 -m venv venv
source venv/bin/activate
If using Windows:

cmd

venv\Scripts\activate

### 3. Install Dependencies

pip install -r requirements.txt
### 4. Create .env File
Create a file named .env inside the agentic_backend folder with the following content:
OPENAI_API_KEY=your_openai_api_key_here
### 5. Create the Database
python

from memory_layer.db import Base, engine
Base.metadata.create_all(bind=engine)
exit()

### 6. Run the Server (Backend + WebSocket + API)

uvicorn main:app --reload --host 0.0.0.0 --port 8000

POST /agent/chat — Send a message to the AI agent.

GET /final-response/{conversation_id} — Retrieve final approved message.

POST /users — Create a new user.

POST /users/login — Login as a user.

GET /flagged — View flagged responses (supervisor).

POST /flagged/{id}/resolve — Approve/edit/reject flagged messages.

### 📡 WebSocket Monitoring

Supervisors receive updates via WebSocket:

Connect to: ws://localhost:8000/ws/{conversation_id}


