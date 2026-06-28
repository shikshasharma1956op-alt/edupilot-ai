import logging
import json
from typing import Dict, Any, List, Tuple
from backend.app.config import MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.mcp_clients import MCPClientManager
from backend.app.security import SecurityManager

# Import sub-agents
from backend.app.agents.career_advisor import run_career_advisor
from backend.app.agents.learning_planner import run_learning_planner
from backend.app.agents.resource_discovery import run_resource_discovery
from backend.app.agents.progress_evaluation import run_progress_evaluation
from backend.app.agents.motivation_coach import run_motivation_coach

logger = logging.getLogger("Orchestrator")

try:
    from google.adk import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    InMemoryRunner = None

ORCHESTRATOR_INSTRUCTION = """
You are the Orchestrator Agent in EduPilot AI.
Your job is to parse the user's educational requests, select the specialized sub-agents that are best suited to handle them,
and compile a final report.

Sub-agents:
- Career Advisor (matches interests to paths)
- Learning Planner (generates milestone roadmaps)
- Resource Discovery (queries GitHub, YouTube, Kaggle)
- Progress Evaluation (checks code and builds quizzes)
- Motivation Coach (gives streaks and encouragement)
"""

if ADK_AVAILABLE and not MOCK_MODE:
    try:
        orchestrator_agent = Agent(
            name="Orchestrator",
            model=GEMINI_MODEL,
            instruction=ORCHESTRATOR_INSTRUCTION
        )
    except Exception as e:
        logger.warning(f"Failed to initialize Orchestrator ADK: {e}")
        orchestrator_agent = None
else:
    orchestrator_agent = None


class Orchestrator:
    def __init__(self, memory_db: MemoryDb, mcp_manager: MCPClientManager):
        self.memory_db = memory_db
        self.mcp_manager = mcp_manager

    def route_request(self, prompt: str) -> List[str]:
        """
        Decides which sub-agents need to run based on the prompt content.
        Can return multiple agents for a sequential/cascade flow.
        """
        p_lower = prompt.lower()
        agents_to_run = []

        # Check for onboarding flow (e.g. "I want to learn..." or "help me start...")
        is_onboarding = any(x in p_lower for x in ["become a", "learn to be", "help me become", "start my career", "i want to learn"])
        
        if is_onboarding:
            # Cascading multi-agent flow: career guidance -> learning plan -> initial resources
            return ["Career Advisor", "Learning Planner", "Resource Discovery"]

        # Single agent routing heuristics
        if any(x in p_lower for x in ["career", "job", "salary", "advisor", "path", "role", "outlook"]):
            agents_to_run.append("Career Advisor")
            
        if any(x in p_lower for x in ["plan", "roadmap", "milestone", "schedule", "syllabus", "steps"]):
            agents_to_run.append("Learning Planner")
            
        if any(x in p_lower for x in ["resource", "youtube", "github", "kaggle", "tutorial", "dataset", "link", "search"]):
            agents_to_run.append("Resource Discovery")
            
        if any(x in p_lower for x in ["evaluate", "code", "quiz", "grade", "score", "submit", "project", "check"]):
            agents_to_run.append("Progress Evaluation")
            
        if any(x in p_lower for x in ["motivate", "streak", "stuck", "tired", "quote", "coach", "encourage"]):
            agents_to_run.append("Motivation Coach")

        # Default to Motivation Coach + Career Advisor if ambiguous
        if not agents_to_run:
            agents_to_run = ["Career Advisor", "Motivation Coach"]

        return agents_to_run

    async def execute(self, session_id: str, prompt: str) -> Tuple[str, List[Dict[str, str]]]:
        """
        Runs the full orchestrator flow.
        1. Checks for prompt injections.
        2. Determines routing.
        3. Invokes sub-agents sequentially.
        4. Compiles final output.
        Returns:
            (final_response_text, execution_logs)
            where execution_logs lists which agents ran and their status (for the frontend visual graph).
        """
        # Save user message to database
        self.memory_db.get_or_create_session(session_id)
        self.memory_db.add_message(session_id, "user", prompt)

        # 1. Security validation
        is_clean, reason = SecurityManager.is_clean_input(prompt)
        if not is_clean:
            err_msg = f"⚠️ **Security Alert**: Request blocked. Reason: {reason}"
            self.memory_db.add_message(session_id, "assistant", err_msg, "Security Guard")
            return err_msg, [{"agent": "Security Guard", "status": "blocked", "color": "red"}]

        # 2. Dynamic routing
        target_agents = self.route_request(prompt)
        execution_logs = []
        accumulated_responses = []

        logger.info(f"Orchestrator routed prompt to: {target_agents}")

        # 3. Sequential invocation of sub-agents
        for agent_name in target_agents:
            execution_logs.append({"agent": agent_name, "status": "running", "color": self.get_agent_color(agent_name)})
            
            try:
                if agent_name == "Career Advisor":
                    response = await run_career_advisor(session_id, prompt, self.memory_db)
                elif agent_name == "Learning Planner":
                    response = await run_learning_planner(session_id, prompt, self.memory_db)
                elif agent_name == "Resource Discovery":
                    response = await run_resource_discovery(session_id, prompt, self.memory_db, self.mcp_manager)
                elif agent_name == "Progress Evaluation":
                    # Check if there is code-like blocks in the prompt
                    code_snippet = None
                    if "```" in prompt:
                        parts = prompt.split("```")
                        if len(parts) >= 3:
                            code_snippet = parts[1]
                    response = await run_progress_evaluation(session_id, prompt, self.memory_db, code_snippet)
                elif agent_name == "Motivation Coach":
                    response = await run_motivation_coach(session_id, prompt, self.memory_db)
                else:
                    response = f"Agent {agent_name} is not recognized."
                
                accumulated_responses.append(response)
                
                # Mark agent as completed in visual status logs
                for log in execution_logs:
                    if log["agent"] == agent_name:
                        log["status"] = "completed"
                        
            except Exception as e:
                logger.error(f"Error executing agent {agent_name}: {e}")
                accumulated_responses.append(f"❌ *Error in {agent_name} processing.*")
                for log in execution_logs:
                    if log["agent"] == agent_name:
                        log["status"] = "failed"

        # 4. Synthesize final response
        final_response = "\n\n---\n\n".join(accumulated_responses)
        
        # Save assistant message to database
        self.memory_db.add_message(session_id, "assistant", final_response, "Orchestrator")

        return final_response, execution_logs

    @staticmethod
    def get_agent_color(name: str) -> str:
        colors = {
            "Career Advisor": "blue",
            "Learning Planner": "cyan",
            "Resource Discovery": "purple",
            "Progress Evaluation": "green",
            "Motivation Coach": "orange",
            "Orchestrator": "indigo"
        }
        return colors.get(name, "slate")
