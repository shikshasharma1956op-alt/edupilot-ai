import re
from typing import Dict, Any, List, Optional

# List of typical prompt injection keywords or patterns
PROMPT_INJECTION_PATTERNS = [
    r"ignore\s+(?:all\s+)?previous\s+instructions",
    r"override\s+(?:all\s+)?instructions",
    r"system\s+(?:prompt|message|instructions)\s+override",
    r"you\s+are\s+now\s+a\s+different\s+agent",
    r"forget\s+what\s+you\s+were\s+told",
    r"bypass\s+restrictions",
    r"do\s+anything\s+now",
    r"dan\s+mode",
]

class SecurityManager:
    @staticmethod
    def is_clean_input(user_input: str) -> tuple[bool, str]:
        """
        Scans input for prompt injection indicators.
        Returns:
            (is_safe: bool, reason: str)
        """
        if not user_input or not isinstance(user_input, str):
            return True, ""
            
        lower_input = user_input.lower()
        for pattern in PROMPT_INJECTION_PATTERNS:
            if re.search(pattern, lower_input):
                return False, f"Potential system override pattern detected: {pattern}"
                
        # Additional checks: extreme length, command execution syntax attempts
        if len(user_input) > 8000:
            return False, "Input length exceeds the safety threshold of 8000 characters."
            
        return True, ""

    @staticmethod
    def validate_tool_permission(agent_name: str, tool_name: str) -> bool:
        """
        Defines an access control matrix showing which agents are permitted to use which tools.
        """
        # Career Advisor: only career tools
        # Learning Planner: only planning tools
        # Resource Hunter: YouTube, GitHub, Kaggle search tools
        # Progress Evaluator: quiz and code evaluation tools
        # Motivation Coach: profile and quote tools
        
        allowed_tools = {
            "Career Advisor": ["get_career_paths", "get_career_details", "update_session_profile"],
            "Learning Planner": ["generate_learning_roadmap", "generate_milestones", "update_current_roadmap"],
            "Resource Discovery": ["search_resources", "github_mcp_query", "youtube_mcp_query", "kaggle_mcp_query", "web_search_query"],
            "Progress Evaluation": ["evaluate_project", "get_evaluation_quiz", "toggle_milestone", "add_completed_project"],
            "Motivation Coach": ["get_motivation_boost", "get_session_profile"]
        }
        
        # If agent is Orchestrator, it has broad routing permissions
        if agent_name == "Orchestrator":
            return True
            
        # Get permissions list for the agent
        agent_allowed = allowed_tools.get(agent_name, [])
        return tool_name in agent_allowed

    @staticmethod
    def sanitize_tool_parameters(tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitizes tool input arguments to prevent directory traversal, local command injections,
        or SQL injections in parameters.
        """
        sanitized = {}
        for key, val in params.items():
            if isinstance(val, str):
                # Prevent directory traversal
                cleaned = val.replace("../", "").replace("..\\", "")
                # Prevent command chainers
                cleaned = re.sub(r"[;&|`$]", "", cleaned)
                sanitized[key] = cleaned
            elif isinstance(val, list):
                sanitized[key] = [
                    (item.replace("../", "").replace("..\\", "") if isinstance(item, str) else item)
                    for item in val
                ]
            else:
                sanitized[key] = val
        return sanitized
