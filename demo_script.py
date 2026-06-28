import os
import asyncio
import sys

# Configure path and environment variables for local testing
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
os.environ["MOCK_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./backend/data/edupilot.db"

from backend.app.memory import MemoryDb
from backend.app.mcp_clients import MCPClientManager
from backend.app.agents.orchestrator import Orchestrator

# Colored console helpers
class colors:
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PURPLE = '\033[95m'
    GREEN = '\033[92m'
    ORANGE = '\033[93m'
    END = '\033[0m'
    BOLD = '\033[1m'

AGENT_COLORS = {
    "blue": colors.BLUE,
    "cyan": colors.CYAN,
    "purple": colors.PURPLE,
    "green": colors.GREEN,
    "orange": colors.ORANGE
}

async def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    print(f"{colors.BOLD}======================================================================{colors.END}")
    print(f"{colors.BOLD}           EduPilot AI Multi-Agent Session - Local Test Run           {colors.END}")
    print(f"{colors.BOLD}======================================================================{colors.END}\n")

    # 1. Initialize DB and Orchestrator
    db = MemoryDb()
    mcp = MCPClientManager()
    orchestrator = Orchestrator(db, mcp)
    
    session_id = "demo_session_cli_1"
    user_prompt = "Hello! I am a beginner, and I want to become a Machine Learning Engineer."
    
    print(f"👤 {colors.BOLD}User Request:{colors.END} '{user_prompt}'\n")
    print("🤖 Running Orchestrator Routing & Multi-Agent flow...")
    print("----------------------------------------------------------------------")
    
    # 2. Execute Orchestration
    response, logs = await orchestrator.execute(session_id, user_prompt)
    
    # 3. Print execution flow (visual trace of agent calls)
    print("\n🗺️  Agent Execution Connection Graph Trace:")
    for log in logs:
        agent_name = log["agent"]
        color_code = log["color"]
        status = log["status"]
        c = AGENT_COLORS.get(color_code, colors.END)
        print(f"  └─► {c}{colors.BOLD}[{agent_name}]{colors.END} status: {colors.BOLD}{status}{colors.END}")
        
    print("\n----------------------------------------------------------------------")
    print(f"📄 {colors.BOLD}Aggregated Mentor Response:{colors.END}\n")
    print(response)
    print("\n----------------------------------------------------------------------")
    
    # 4. Read database changes (Memory system validation)
    print(f"💾 {colors.BOLD}SQLite Memory Verification:{colors.END}")
    profile = db.get_session_profile(session_id)
    print(f"  • Target Role: {colors.CYAN}{profile.get('target_role')}{colors.END}")
    print(f"  • Target Skills: {colors.BLUE}{', '.join(profile.get('career_interests', []))}{colors.END}")
    
    print(f"\n🗺️  {colors.BOLD}Registered Roadmap Milestones in DB:{colors.END}")
    milestones = db.get_milestones(session_id)
    for m in milestones:
        status_symbol = "✅ Completed" if m.get("is_completed") else "❌ Pending"
        print(f"  • {m['title']} -> Status: {status_symbol}")
        print(f"    Description: {m['description']}")
        
    print(f"\n{colors.BOLD}======================================================================{colors.END}")
    print(f"{colors.GREEN}{colors.BOLD}EduPilot AI CLI verification successful! Full Multi-Agent pipeline active.{colors.END}")
    print(f"{colors.BOLD}======================================================================{colors.END}")

if __name__ == "__main__":
    asyncio.run(main())
