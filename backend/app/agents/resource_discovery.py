import logging
from typing import Dict, Any, List
from backend.app.config import MOCK_MODE, GEMINI_MODEL
from backend.app.memory import MemoryDb
from backend.app.mcp_clients import MCPClientManager
from backend.app.security import SecurityManager

logger = logging.getLogger("ResourceDiscovery")

try:
    from google.adk import Agent
    from google.adk.runners import InMemoryRunner
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    Agent = None
    InMemoryRunner = None

SYSTEM_INSTRUCTION = """
You are the Resource Discovery Agent (assigned color: Purple) in the EduPilot AI multi-agent mentoring system.
Your mission is to query GitHub, YouTube, Kaggle, and Web Search tools (via MCP servers) to fetch educational content, templates, datasets, and guides.

Format findings in clean markdown blocks. Always include direct links to resources.

You must only use tools that are allowed for you. Validate that query inputs are clean.
"""

if ADK_AVAILABLE and not MOCK_MODE:
    try:
        resource_agent = Agent(
            name="Resource Discovery",
            model=GEMINI_MODEL,
            instruction=SYSTEM_INSTRUCTION
        )
    except Exception as e:
        logger.warning(f"Failed to initialize ADK Agent: {e}. Falling back to simulated agent.")
        resource_agent = None
else:
    resource_agent = None


async def run_resource_discovery(session_id: str, prompt: str, memory_db: MemoryDb, mcp_manager: MCPClientManager) -> str:
    """
    Executes the Resource Discovery agent.
    Calls MCP Clients for Github, Youtube, Kaggle, and Search to locate learning materials.
    """
    logger.info(f"Resource Discovery running for session {session_id} with prompt: '{prompt}'")
    
    is_safe, reason = SecurityManager.is_clean_input(prompt)
    if not is_safe:
        return f"[Security Warning] Resource Discovery rejected execution: {reason}"
        
    # Get active profile targets to refine search terms
    profile = memory_db.get_session_profile(session_id)
    target_role = (profile.get("target_role") if profile else None) or "Software Engineer"
    
    # Define tool query based on active role + user prompt
    search_term = prompt if prompt else target_role
    
    # 1. Trigger MCP Server Calls
    github_repos = await mcp_manager.github_query(search_term, limit=2)
    youtube_vids = await mcp_manager.youtube_query(search_term, limit=2)
    kaggle_data = await mcp_manager.kaggle_query(search_term, limit=2)
    web_links = await mcp_manager.search_query(search_term, limit=2)
    
    # 2. ADK LLM Run
    if resource_agent and not MOCK_MODE:
        try:
            # We pass the MCP results to the agent inside the prompt so it can reason over them
            context = f"""
            The MCP servers returned the following resource listings:
            GitHub Repos: {json.dumps(github_repos)}
            YouTube Videos: {json.dumps(youtube_vids)}
            Kaggle Datasets: {json.dumps(kaggle_data)}
            Web Search: {json.dumps(web_links)}
            
            Synthesize these findings for the student studying {target_role} and explain how to use them.
            """
            
            runner = InMemoryRunner(agent=resource_agent)
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

    # 3. Resource Compiler (Mock Mode Fallback)
    response = (
        f"### 🔍 Resource Hunter (Color: Purple)\n\n"
        f"I've searched our connected **MCP Servers (GitHub, YouTube, Kaggle, and Google Search)** for **{search_term}** resources. "
        "Here are the recommended assets for your studies:\n\n"
    )
    
    if github_repos:
        response += "#### 🐙 GitHub MCP Repositories\n"
        for repo in github_repos:
            response += f"- [{repo['name']}]({repo['url']}) (★ {repo['stars']:,}) - *{repo['description']}*\n"
        response += "\n"
        
    if youtube_vids:
        response += "#### 🎥 YouTube MCP Tutorials\n"
        for vid in youtube_vids:
            response += f"- [{vid['title']}]({vid['url']}) - Channel: *{vid['channel']}* [{vid['duration']}]\n"
        response += "\n"
        
    if kaggle_data:
        response += "#### 🏆 Kaggle MCP Datasets & Competitions\n"
        for kag in kaggle_data:
            response += f"- [{kag['title']}]({kag['url']}) ({kag['type']})\n"
        response += "\n"
        
    if web_links:
        response += "#### 🌐 Web Search Reference Links\n"
        for link in web_links:
            response += f"- [{link['title']}]({link['url']}) - *{link['snippet']}*\n"
        response += "\n"
        
    response += "📝 *Tips: Fork the GitHub templates, review the YouTube video, and download datasets for your capstone project!*"
    
    return response
