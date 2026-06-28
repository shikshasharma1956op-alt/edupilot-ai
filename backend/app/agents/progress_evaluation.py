import logging
import json
from typing import Dict, Any, List, Optional
from backend.app.config import MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.security import SecurityManager

logger = logging.getLogger("ProgressEvaluation")

try:
    from google.adk import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    InMemoryRunner = None

SYSTEM_INSTRUCTION = """
You are the Progress Evaluation Agent (assigned color: Green) in the EduPilot AI multi-agent mentoring system.
Your responsibility is to grade student project submissions, evaluate code snippets, offer targeted feedback, and generate quick quiz questions.

When evaluating a project:
1. Provide a score between 0 and 100.
2. Structure your feedback into 'Strengths', 'Areas of Improvement', and 'Next Steps'.

You must only use tools that are allowed for you. Sanitise input inputs.
"""

if ADK_AVAILABLE and not MOCK_MODE:
    try:
        evaluation_agent = Agent(
            name="Progress Evaluation",
            model=GEMINI_MODEL,
            instruction=SYSTEM_INSTRUCTION
        )
    except Exception as e:
        logger.warning(f"Failed to initialize ADK Agent: {e}. Falling back to simulated agent.")
        evaluation_agent = None
else:
    evaluation_agent = None


async def run_progress_evaluation(session_id: str, prompt: str, memory_db: MemoryDb, code_snippet: Optional[str] = None) -> str:
    """
    Executes the Progress Evaluation agent.
    Grades user coding submissions or generates conceptual quizzes.
    """
    logger.info(f"Progress Evaluation running for session {session_id} with prompt: '{prompt}'")
    
    is_safe, reason = SecurityManager.is_clean_input(prompt)
    if not is_safe:
        return f"[Security Warning] Progress Evaluation rejected: {reason}"
        
    p_lower = prompt.lower()
    
    # 1. Project Grade Flow
    if "evaluate" in p_lower or "grade" in p_lower or code_snippet:
        project_title = "Capstone Project Submission" if not code_snippet else "Coding Assignment"
        
        # Analyze parameters safely
        clean_prompt = SecurityManager.sanitize_tool_parameters("evaluate_project", {"prompt": prompt})["prompt"]
        
        # ADK Run
        if evaluation_agent and not MOCK_MODE:
            try:
                runner = InMemoryRunner(agent=evaluation_agent)
                context = f"Project description: {clean_prompt}. Code snippet: {code_snippet if code_snippet else 'None'}"
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
                
                # Register completed project with mock score in database
                memory_db.add_completed_project(
                    session_id=session_id,
                    title=project_title,
                    description=clean_prompt,
                    score=85,
                    feedback=response_text[:500],
                    code_snippet=code_snippet
                )
                
                # Check off milestone 3 (capstone)
                milestones = memory_db.get_milestones(session_id)
                if milestones:
                    memory_db.toggle_milestone(milestones[-1]["id"], True, 85, "Project graded and completed successfully.")
                
                return response_text
            except Exception as e:
                logger.error(f"Error in ADK evaluation execution: {e}. Falling back to simulation.")

        # Simulator Fallback
        score = 88
        feedback = (
            "**Strengths:** Good architectural design, correct library integration, and clean logic division.\n"
            "**Areas of Improvement:** Needs error handling middleware and environment configuration checks.\n"
            "**Next Steps:** Implement unit tests and package into a Docker image."
        )
        
        # Store in sqlite db
        memory_db.add_completed_project(
            session_id=session_id,
            title=project_title,
            description=clean_prompt,
            score=score,
            feedback=feedback,
            code_snippet=code_snippet
        )
        
        # Complete latest milestone (usually Capstone)
        milestones = memory_db.get_milestones(session_id)
        if milestones:
            # Let's toggle the last milestone (Capstone project) to completed
            last_id = milestones[-1]["id"]
            memory_db.toggle_milestone(last_id, True, score, "Successfully evaluated and graded.")
            
        return (
            f"### 📈 Progress Evaluator (Color: Green)\n\n"
            f"**Project Title:** {project_title}\n"
            f"**Evaluation Score:** `{score}/100` ⭐\n\n"
            f"#### 🔍 Feedback Report:\n"
            f"{feedback}\n\n"
            f"✅ *Milestone status updated! Milestone 3 has been marked as **Completed**.*"
        )
        
    # 2. Quiz Flow
    else:
        # ADK Run
        if evaluation_agent and not MOCK_MODE:
            try:
                runner = InMemoryRunner(agent=evaluation_agent)
                response_text = ""
                async for event in runner.run_async(
                    user_id="default_user",
                    session_id=session_id,
                    new_message=f"Generate a 3-question conceptual quiz on the topic: {prompt}"
                ):
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                response_text += part.text
                return response_text
            except Exception as e:
                logger.error(f"Error in ADK quiz execution: {e}. Falling back to simulation.")
                
        # Simulator Fallback
        return (
            f"### 📝 Progress Evaluator: Quick Quiz (Color: Green)\n\n"
            f"Here is a conceptual quick check on **{prompt if prompt else 'Software Engineering'}**:\n\n"
            f"1️⃣ **Question 1:** What is the difference between synchronous and asynchronous processes in Node.js/Python?\n"
            f"   - *A) Sync blocks execution; Async handles tasks concurrently.*\n"
            f"   - *B) Sync is faster; Async is secure.*\n\n"
            f"2️⃣ **Question 2:** Why is database indexing helpful in relational schemas?\n"
            f"   - *A) It encrypts credentials.*\n"
            f"   - *B) It speeds up read queries at the cost of write speed.*\n\n"
            f"3️⃣ **Question 3:** What does Docker use to isolate container resources?\n"
            f"   - *A) Virtual Machines.*\n"
            f"   - *B) Linux Cgroups and Namespaces.*\n\n"
            f"💬 *Reply with your answers (e.g., '1-A, 2-B, 3-B') to check your scores!*"
        )
