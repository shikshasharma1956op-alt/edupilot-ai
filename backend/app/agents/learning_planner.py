import logging
import json
from typing import Dict, Any, List
from backend.app.config import MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.security import SecurityManager

logger = logging.getLogger("LearningPlanner")

try:
    from google.adk import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    InMemoryRunner = None

SYSTEM_INSTRUCTION = """
You are the Learning Planner Agent (assigned color: Cyan) in the EduPilot AI multi-agent mentoring system.
Your task is to build structured, milestone-based learning plans and syllabus roadmaps based on the user's target career role and skill level.

Provide details for 3 core milestones:
1. Foundation (Basic concepts and setup)
2. Core Skills (Core frameworks and practical tasks)
3. Capstone Project (Hands-on application build)

You must only use tools that are allowed for you. Enforce safety guidelines.
"""

if ADK_AVAILABLE and not MOCK_MODE:
    try:
        planner_agent = Agent(
            name="Learning Planner",
            model=GEMINI_MODEL,
            instruction=SYSTEM_INSTRUCTION
        )
    except Exception as e:
        logger.warning(f"Failed to initialize ADK Agent: {e}. Falling back to simulated agent.")
        planner_agent = None
else:
    planner_agent = None


async def run_learning_planner(session_id: str, prompt: str, memory_db: MemoryDb) -> str:
    """
    Executes the Learning Planner agent.
    Generates a structured learning plan based on the user's active target role
    and registers it to the database.
    """
    logger.info(f"Learning Planner running for session {session_id} with prompt: '{prompt}'")
    
    is_safe, reason = SecurityManager.is_clean_input(prompt)
    if not is_safe:
        return f"[Security Warning] Learning Planner rejected execution: {reason}"
        
    # Get user profile to check what career role they are working on
    profile = memory_db.get_session_profile(session_id)
    target_role = (profile.get("target_role") if profile else None) or "Software Engineer"
    
    # 1. ADK LLM Run
    if planner_agent and not MOCK_MODE:
        try:
            runner = InMemoryRunner(agent=planner_agent)
            response_text = ""
            async for event in runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=f"Generate a learning plan for target role: {target_role}. Additional constraints: {prompt}"
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
            
            # Update roadmap in database
            roadmap = {
                "role": target_role,
                "milestones": [
                    {"title": "Milestone 1: Foundations", "description": "Learn the syntax, setup, and key parameters for " + target_role},
                    {"title": "Milestone 2: Intermediate Frameworks", "description": "Build minor demo apps using typical libraries and tools"},
                    {"title": "Milestone 3: Portfolio Capstone", "description": "Create a fully functional production-quality project"}
                ]
            }
            memory_db.update_current_roadmap(session_id, roadmap)
            return response_text
        except Exception as e:
            logger.error(f"Error in ADK execution: {e}. Falling back to simulation.")

    # 2. Contextual Roadmap Generator (Mock Mode Fallback)
    if target_role == "Machine Learning Engineer":
        roadmap = {
            "role": "Machine Learning Engineer",
            "milestones": [
                {
                    "title": "Milestone 1: Python Data Science Foundations",
                    "description": "Master NumPy, Pandas, Matplotlib, and basic statistical regression concepts."
                },
                {
                    "title": "Milestone 2: Core Machine Learning Models",
                    "description": "Implement classification and regression algorithms using Scikit-Learn; evaluate metrics."
                },
                {
                    "title": "Milestone 3: Deep Learning Capstone",
                    "description": "Train and deploy a neural network model using PyTorch or TensorFlow, and write a model evaluation dashboard."
                }
            ]
        }
    elif target_role == "Frontend Developer":
        roadmap = {
            "role": "Frontend Developer",
            "milestones": [
                {
                    "title": "Milestone 1: HTML, CSS & Modern JavaScript",
                    "description": "Learn semantic layout design, CSS Grid/Flexbox, and ES6+ asynchronous features."
                },
                {
                    "title": "Milestone 2: React & State Management",
                    "description": "Master component rendering lifecycle, hooks, and routing strategies using React."
                },
                {
                    "title": "Milestone 3: Next.js Portfolio App",
                    "description": "Build a responsive Next.js application using Tailwind CSS, server-side rendering, and API route integrations."
                }
            ]
        }
    elif target_role == "Backend Developer":
        roadmap = {
            "role": "Backend Developer",
            "milestones": [
                {
                    "title": "Milestone 1: Python, SQL & Database Modeling",
                    "description": "Learn object-oriented programming, relational database schemas, and SQL CRUD queries."
                },
                {
                    "title": "Milestone 2: FastAPI, REST & Middleware",
                    "description": "Build RESTful APIs with FastAPI; write custom security validation and logging middleware."
                },
                {
                    "title": "Milestone 3: Docker & Cloud Server Deploy",
                    "description": "Containerize your backend API using Docker, write multi-stage Dockerfiles, and configure Postgres databases."
                }
            ]
        }
    else:
        roadmap = {
            "role": "Software Engineer",
            "milestones": [
                {
                    "title": "Milestone 1: Basic Programming Syntax & Logic",
                    "description": "Understand core structures, control flows, functions, and command inputs."
                },
                {
                    "title": "Milestone 2: Algorithms & Data Structures",
                    "description": "Learn sorting algorithms, lists, trees, graphs, and Big O complexity analysis."
                },
                {
                    "title": "Milestone 3: Full-Stack Web Integration",
                    "description": "Assemble a complete web page backed by a simple database and logic service."
                }
            ]
        }

    # Save to session memory (this clears old milestones and inserts new ones)
    memory_db.update_current_roadmap(session_id, roadmap)

    response = (
        f"### 🗺️ Learning Roadmap: {target_role} (Color: Cyan)\n\n"
        "I have generated a customized learning plan and uploaded the milestones to your progress tracker!\n\n"
    )
    for idx, m in enumerate(roadmap["milestones"], 1):
        response += f"#### 📍 {m['title']}\n- **Goal:** {m['description']}\n\n"
        
    response += "💡 *Next step: Use the Resource Discovery Agent to find articles, courses, and Github source code for these milestones.*"
    return response
