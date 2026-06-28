import logging
import random
from typing import Dict, Any, List
from backend.app.config import MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.security import SecurityManager

logger = logging.getLogger("MotivationCoach")

try:
    from google.adk import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    InMemoryRunner = None

SYSTEM_INSTRUCTION = """
You are the Motivation Coach Agent (assigned color: Orange) in the EduPilot AI multi-agent mentoring system.
Your mission is to support the student's mental stamina, celebrate milestone achievements, and keep them focused on their career target.

Reference their active goals and streak statistics to make your encouragement highly contextual.

You must only use tools that are allowed for you. Enforce data isolation.
"""

if ADK_AVAILABLE and not MOCK_MODE:
    try:
        motivation_agent = Agent(
            name="Motivation Coach",
            model=GEMINI_MODEL,
            instruction=SYSTEM_INSTRUCTION
        )
    except Exception as e:
        logger.warning(f"Failed to initialize ADK Agent: {e}. Falling back to simulated agent.")
        motivation_agent = None
else:
    motivation_agent = None

QUOTES = [
    "The secret of getting ahead is getting started. — Mark Twain",
    "Continuous learning is the minimum requirement for success in any field. — Brian Tracy",
    "Do what you can, with what you have, where you are. — Theodore Roosevelt",
    "It always seems impossible until it is done. — Nelson Mandela",
    "Action is the foundational key to all success. — Pablo Picasso"
]


async def run_motivation_coach(session_id: str, prompt: str, memory_db: MemoryDb) -> str:
    """
    Executes the Motivation Coach agent.
    Analyses progress milestones and provides contextual mental support.
    """
    logger.info(f"Motivation Coach running for session {session_id} with prompt: '{prompt}'")
    
    is_safe, reason = SecurityManager.is_clean_input(prompt)
    if not is_safe:
        return f"[Security Warning] Motivation Coach rejected execution: {reason}"
        
    profile = memory_db.get_session_profile(session_id)
    milestones = memory_db.get_milestones(session_id)
    
    target_role = (profile.get("target_role") if profile else None) or "Software Engineer"
    
    # Analyze completion stats
    total = len(milestones)
    completed = len([m for m in milestones if m.get("is_completed")])
    
    # 1. ADK LLM Run
    if motivation_agent and not MOCK_MODE:
        try:
            runner = InMemoryRunner(agent=motivation_agent)
            context = f"Student Target: {target_role}. Milestones: {completed}/{total} completed. Student prompt: {prompt}"
            response_text = ""
            async for event in runner.run_async(
                user_id="default_user",
                session_id=session_id,
                new_message=context
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_text += part.text
            return response_text
        except Exception as e:
            logger.error(f"Error in ADK execution: {e}. Falling back to simulation.")

    # 2. Mental Support Generator (Mock Mode Fallback)
    quote = random.choice(QUOTES)
    
    if total > 0 and completed == 0:
        boost = f"I see you have generated a fresh path for **{target_role}**! Starting a new roadmap can feel intimidating, but taking the first step is where the magic happens. Let's tackle Milestone 1 together!"
    elif completed > 0 and completed < total:
        boost = f"Excellent job on completing {completed}/{total} of your milestones! You are making steady progress towards becoming a **{target_role}**. Keep up the momentum!"
    elif total > 0 and completed == total:
        boost = f"Incredible achievement! You have checked off all milestones for **{target_role}**! Take a moment to celebrate. You're ready to show off your portfolio project to the world!"
    else:
        boost = f"Keep pushing forward! Every line of code you write and concept you learn brings you closer to your career objectives."
        
    response = (
        f"### ⚡ Motivation Coach: Daily Spark (Color: Orange)\n\n"
        f"*{quote}*\n\n"
        f"**Mental Boost:**\n"
        f"{boost}\n\n"
        f"🔥 **Current Streak:** `4 Days` | **Completion Ratio:** `{completed}/{total} Milestones` ({int((completed/total)*100) if total > 0 else 0}%)\n\n"
        f"🚀 *Action step: Review the next milestone in your dashboard, take a deep breath, and write one line of code!*"
    )
    
    return response
