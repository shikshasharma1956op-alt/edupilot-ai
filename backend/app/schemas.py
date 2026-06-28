from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique session identifier for isolation")
    message: str = Field(..., description="The user query")
    user_id: Optional[str] = Field("default_user", description="Identifies the student")

class ChatResponse(BaseModel):
    response: str
    execution_logs: List[Dict[str, str]]

class SessionProfileResponse(BaseModel):
    session_id: str
    user_id: str
    career_interests: Optional[List[str]] = None
    suggested_careers: Optional[List[Dict[str, Any]]] = None
    target_role: Optional[str] = None
    skill_level: Optional[str] = None
    current_roadmap: Optional[Dict[str, Any]] = None

class MilestoneToggleRequest(BaseModel):
    is_completed: bool
    score: Optional[int] = None
    feedback: Optional[str] = None

class SettingsUpdateRequest(BaseModel):
    mock_mode: bool
    gemini_model: str
