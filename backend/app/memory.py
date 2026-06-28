import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from backend.app.config import DATABASE_URL

class MemoryDb:
    def __init__(self):
        # Extract DB path from file:// scheme or use standard sqlite path
        self.db_path = DATABASE_URL.replace("sqlite:///", "")
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    career_interests TEXT,
                    suggested_careers TEXT,
                    target_role TEXT,
                    skill_level TEXT,
                    current_roadmap TEXT
                )
            """)

            # Create messages table (for chat history and agent execution logs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    agent_name TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)

            # Create milestones table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    is_completed INTEGER DEFAULT 0,
                    score INTEGER,
                    feedback TEXT,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)

            # Create completed_projects table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS completed_projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT,
                    score INTEGER NOT NULL,
                    feedback TEXT,
                    code_snippet TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id)
                )
            """)
            conn.commit()

    # --- Session Operations ---
    def get_or_create_session(self, session_id: str, user_id: str = "default_user") -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            
            cursor.execute(
                "INSERT INTO sessions (session_id, user_id) VALUES (?, ?)", 
                (session_id, user_id)
            )
            conn.commit()
            return {"session_id": session_id, "user_id": user_id, "career_interests": None, "suggested_careers": None, "target_role": None, "skill_level": None, "current_roadmap": None}

    def update_session_profile(self, session_id: str, career_interests: Optional[List[str]] = None, suggested_careers: Optional[List[Dict[str, Any]]] = None, target_role: Optional[str] = None, skill_level: Optional[str] = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            updates = []
            params = []
            
            if career_interests is not None:
                updates.append("career_interests = ?")
                params.append(json.dumps(career_interests))
            if suggested_careers is not None:
                updates.append("suggested_careers = ?")
                params.append(json.dumps(suggested_careers))
            if target_role is not None:
                updates.append("target_role = ?")
                params.append(target_role)
            if skill_level is not None:
                updates.append("skill_level = ?")
                params.append(skill_level)
                
            if not updates:
                return
                
            params.append(session_id)
            cursor.execute(f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?", params)
            conn.commit()

    def update_current_roadmap(self, session_id: str, roadmap: Dict[str, Any]) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE sessions SET current_roadmap = ? WHERE session_id = ?", 
                (json.dumps(roadmap), session_id)
            )
            
            # Re-initialize milestones based on roadmap structure
            cursor.execute("DELETE FROM milestones WHERE session_id = ?", (session_id,))
            
            # Check if roadmap has milestones list
            milestones = roadmap.get("milestones", [])
            for m in milestones:
                cursor.execute(
                    "INSERT INTO milestones (session_id, title, description, is_completed) VALUES (?, ?, ?, 0)",
                    (session_id, m.get("title", ""), m.get("description", ""))
                )
            conn.commit()

    def get_session_profile(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
            row = cursor.fetchone()
            if not row:
                return None
            res = dict(row)
            if res.get("career_interests"):
                res["career_interests"] = json.loads(res["career_interests"])
            if res.get("suggested_careers"):
                res["suggested_careers"] = json.loads(res["suggested_careers"])
            if res.get("current_roadmap"):
                res["current_roadmap"] = json.loads(res["current_roadmap"])
            return res

    # --- Message / History Operations ---
    def add_message(self, session_id: str, role: str, content: str, agent_name: Optional[str] = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (session_id, role, content, agent_name) VALUES (?, ?, ?, ?)",
                (session_id, role, content, agent_name)
            )
            conn.commit()

    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role, content, agent_name, timestamp FROM messages WHERE session_id = ? ORDER BY timestamp ASC",
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]

    # --- Milestone Operations ---
    def get_milestones(self, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM milestones WHERE session_id = ?", (session_id,))
            return [dict(row) for row in cursor.fetchall()]

    def toggle_milestone(self, milestone_id: int, is_completed: bool, score: Optional[int] = None, feedback: Optional[str] = None) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            completed_at = datetime.now().isoformat() if is_completed else None
            cursor.execute(
                """UPDATE milestones 
                   SET is_completed = ?, score = ?, feedback = ?, completed_at = ? 
                   WHERE id = ?""",
                (1 if is_completed else 0, score, feedback, completed_at, milestone_id)
            )
            conn.commit()

    # --- Completed Projects Operations ---
    def add_completed_project(self, session_id: str, title: str, description: str, score: int, feedback: str, code_snippet: Optional[str] = None) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO completed_projects (session_id, title, description, score, feedback, code_snippet) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (session_id, title, description, score, feedback, code_snippet)
            )
            project_id = cursor.lastrowid
            conn.commit()
            return {
                "id": project_id,
                "session_id": session_id,
                "title": title,
                "description": description,
                "score": score,
                "feedback": feedback,
                "code_snippet": code_snippet
            }

    def get_completed_projects(self, session_id: str) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM completed_projects WHERE session_id = ? ORDER BY created_at DESC", (session_id,))
            return [dict(row) for row in cursor.fetchall()]
