import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List

from backend.app.config import APP_NAME, MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.mcp_clients import MCPClientManager
from backend.app.agents.orchestrator import Orchestrator
from backend.app.schemas import (
    ChatRequest, 
    ChatResponse, 
    SessionProfileResponse,
    MilestoneToggleRequest,
    SettingsUpdateRequest
)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("MainBackend")

app = FastAPI(
    title=APP_NAME,
    description="Backend API for EduPilot AI multi-agent coaching system",
    version="1.0.0"
)

# CORS Configuration for local Next.js frontend dev server (port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev simplicity, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Core Services
memory_db = MemoryDb()
mcp_manager = MCPClientManager()
orchestrator = Orchestrator(memory_db, mcp_manager)


@app.get("/")
def read_root():
    import os
    from fastapi.responses import FileResponse
    # Look for frontend client relative to main.py
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_path = os.path.join(base_dir, "..", "frontend", "index.html")
    normalized_path = os.path.normpath(frontend_path)
    if os.path.exists(normalized_path):
        return FileResponse(normalized_path)
    
    return {
        "app": APP_NAME,
        "status": "online",
        "mock_mode": MOCK_MODE,
        "active_model": GEMINI_MODEL
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(payload: ChatRequest):
    """
    Process a chat message through the multi-agent Orchestrator.
    Routes to specific specialized agents and returns aggregated text and routing log.
    """
    logger.info(f"Received chat request for session: {payload.session_id}")
    try:
        response, logs = await orchestrator.execute(payload.session_id, payload.message)
        return ChatResponse(response=response, execution_logs=logs)
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal agent execution error: {str(e)}"
        )


@app.get("/api/sessions/{session_id}", response_model=SessionProfileResponse)
def get_session_profile(session_id: str):
    """
    Retrieves the target career role, milestones, interests, and profile settings for a session.
    """
    profile = memory_db.get_session_profile(session_id)
    if not profile:
        # Create a blank session if none exists
        profile = memory_db.get_or_create_session(session_id)
    
    return SessionProfileResponse(
        session_id=profile["session_id"],
        user_id=profile["user_id"],
        career_interests=profile.get("career_interests"),
        suggested_careers=profile.get("suggested_careers"),
        target_role=profile.get("target_role"),
        skill_level=profile.get("skill_level"),
        current_roadmap=profile.get("current_roadmap")
    )


@app.get("/api/sessions/{session_id}/history")
def get_chat_history(session_id: str):
    """
    Returns message logs of a session for message restoration.
    """
    messages = memory_db.get_messages(session_id)
    return {"messages": messages}


@app.get("/api/sessions/{session_id}/milestones")
def get_milestones(session_id: str):
    """
    Returns lists of registered roadmap milestones and status.
    """
    milestones = memory_db.get_milestones(session_id)
    return {"milestones": milestones}


@app.post("/api/milestones/{milestone_id}/toggle")
def toggle_milestone(milestone_id: int, payload: MilestoneToggleRequest):
    """
    Toggles completion checkbox status of a specific roadmap milestone.
    """
    try:
        memory_db.toggle_milestone(
            milestone_id=milestone_id, 
            is_completed=payload.is_completed,
            score=payload.score,
            feedback=payload.feedback
        )
        return {"status": "success", "milestone_id": milestone_id, "is_completed": payload.is_completed}
    except Exception as e:
        logger.error(f"Error toggling milestone: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database update failed: {str(e)}"
        )


@app.get("/api/sessions/{session_id}/projects")
def get_projects(session_id: str):
    """
    Returns projects submitted and scores for the portfolio.
    """
    projects = memory_db.get_completed_projects(session_id)
    return {"projects": projects}


@app.get("/api/settings")
def get_settings():
    return {
        "mock_mode": MOCK_MODE,
        "gemini_model": GEMINI_MODEL
    }


@app.post("/api/settings")
def update_settings(payload: SettingsUpdateRequest):
    global MOCK_MODE, GEMINI_MODEL
    import os
    
    MOCK_MODE = payload.mock_mode
    GEMINI_MODEL = payload.gemini_model
    
    os.environ["MOCK_MODE"] = "true" if MOCK_MODE else "false"
    os.environ["GEMINI_MODEL"] = GEMINI_MODEL
    
    return {"status": "updated", "mock_mode": MOCK_MODE, "gemini_model": GEMINI_MODEL}
