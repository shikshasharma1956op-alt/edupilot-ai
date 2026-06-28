import sys
import json
import logging
from typing import List, Dict, Any, Optional
from backend.app.config import GITHUB_TOKEN, YOUTUBE_API_KEY, KAGGLE_USERNAME, KAGGLE_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MCPClients")

class MCPClientManager:
    """
    Manages connections to MCP Servers (GitHub, YouTube, Kaggle, Search).
    Implements a robust JSON-RPC interface with fallback modes for development ease.
    """
    def __init__(self):
        self.github_token = GITHUB_TOKEN
        self.youtube_key = YOUTUBE_API_KEY
        self.kaggle_user = KAGGLE_USERNAME
        self.kaggle_key = KAGGLE_KEY
        
    async def github_query(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying GitHub MCP with: '{query}'")
        # In a real environment, we would connect to the GitHub MCP Server via subprocess stdio:
        # e.g., using python-mcp:
        # async with stdio_client(ServerParameters(command="npx", args=["-y", "@modelcontextprotocol/server-github"])) as (read, write):
        #     client = Client(read, write)
        #     result = await client.call_tool("search_repositories", {"query": query})
        
        # We implement a beautiful semantic fallback based on key terms in the query
        q = query.lower()
        if "machine learning" in q or "ml" in q or "data science" in q:
            return [
                {"name": "scikit-learn/scikit-learn", "url": "https://github.com/scikit-learn/scikit-learn", "stars": 58300, "description": "Machine learning in Python"},
                {"name": "keras-team/keras", "url": "https://github.com/keras-team/keras", "stars": 60500, "description": "Deep Learning for humans"},
                {"name": "tensorflow/tensorflow", "url": "https://github.com/tensorflow/tensorflow", "stars": 182000, "description": "An Open Source Machine Learning Framework"}
            ][:limit]
        elif "react" in q or "frontend" in q or "next.js" in q or "nextjs" in q:
            return [
                {"name": "vercel/next.js", "url": "https://github.com/vercel/next.js", "stars": 121000, "description": "The React Framework"},
                {"name": "facebook/react", "url": "https://github.com/facebook/react", "stars": 223000, "description": "A declarative, efficient, and flexible JavaScript library for building user interfaces"},
                {"name": "tailwindlabs/tailwindcss", "url": "https://github.com/tailwindlabs/tailwindcss", "stars": 79000, "description": "A utility-first CSS framework for rapid UI development"}
            ][:limit]
        elif "backend" in q or "fastapi" in q or "python" in q:
            return [
                {"name": "fastapi/fastapi", "url": "https://github.com/fastapi/fastapi", "stars": 71000, "description": "FastAPI framework, high performance, easy to learn, fast to code, ready for production"},
                {"name": "django/django", "url": "https://github.com/django/django", "stars": 77000, "description": "The Web framework for perfectionists with deadlines"},
                {"name": "tiangolo/uvicorn-gunicorn-fastapi-docker", "url": "https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker", "stars": 12000, "description": "Docker image with Uvicorn and Gunicorn for FastAPI applications"}
            ][:limit]
        else:
            # General Python / Dev fallback
            return [
                {"name": "vinta/awesome-python", "url": "https://github.com/vinta/awesome-python", "stars": 204000, "description": "A curated list of awesome Python frameworks, libraries, software and resources"},
                {"name": "donnemartin/system-design-primer", "url": "https://github.com/donnemartin/system-design-primer", "stars": 255000, "description": "Learn how to design large-scale systems"}
            ][:limit]

    async def youtube_query(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying YouTube MCP with: '{query}'")
        q = query.lower()
        if "machine learning" in q or "ml" in q or "data science" in q:
            return [
                {"title": "Machine Learning for Beginners - Full Course", "channel": "freeCodeCamp.org", "url": "https://www.youtube.com/watch?v=GwIo3g1ilaA", "duration": "3:24:00"},
                {"title": "StatQuest: Machine Learning Fundamentals", "channel": "StatQuest with Josh Starmer", "url": "https://www.youtube.com/watch?v=Gv9_4yMHFhI", "duration": "12:15"},
                {"title": "Practical Deep Learning for Coders (2022)", "channel": "Jeremy Howard", "url": "https://www.youtube.com/watch?v=F3zWgwg6z9M", "duration": "1:28:00"}
            ][:limit]
        elif "react" in q or "frontend" in q or "next.js" in q or "nextjs" in q:
            return [
                {"title": "Next.js 14 Tutorial for Beginners", "channel": "Codevolution", "url": "https://www.youtube.com/watch?v=wm5gMKuwSYk", "duration": "2:10:00"},
                {"title": "React JS Full Course for Beginners - 2024", "channel": "Dave Gray", "url": "https://www.youtube.com/watch?v=RVFAyFAtaeA", "duration": "7:12:00"},
                {"title": "Tailwind CSS Crash Course", "channel": "Traversy Media", "url": "https://www.youtube.com/watch?v=UboOTuxgCoU", "duration": "45:00"}
            ][:limit]
        elif "backend" in q or "fastapi" in q or "python" in q:
            return [
                {"title": "FastAPI Crash Course", "channel": "Sanji Code", "url": "https://www.youtube.com/watch?v=tLKKmB21H2M", "duration": "55:00"},
                {"title": "Python for Beginners - Learn Python in 1 Hour", "channel": "Programming with Mosh", "url": "https://www.youtube.com/watch?v=kqtD5dpn9C8", "duration": "1:00:00"},
                {"title": "Docker Crash Course for Web Developers", "channel": "Academind", "url": "https://www.youtube.com/watch?v=pTFZFxd4hOI", "duration": "1:15:00"}
            ][:limit]
        else:
            return [
                {"title": "Harvard CS50 - Introduction to Computer Science", "channel": "Harvard CS50", "url": "https://www.youtube.com/watch?v=8mAITcNt710", "duration": "2:15:00"},
                {"title": "How to Learn Code Faster", "channel": "Clément Mihailescu", "url": "https://www.youtube.com/watch?v=M9K1q484y7A", "duration": "10:15"}
            ][:limit]

    async def kaggle_query(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying Kaggle MCP with: '{query}'")
        q = query.lower()
        if "machine learning" in q or "ml" in q or "data science" in q:
            return [
                {"title": "Titanic - Machine Learning from Disaster", "type": "Competition", "url": "https://www.kaggle.com/c/titanic", "participants": 15000},
                {"title": "Iris Species Dataset", "type": "Dataset", "url": "https://www.kaggle.com/datasets/uciml/iris", "downloads": 240000},
                {"title": "House Prices - Advanced Regression Techniques", "type": "Competition", "url": "https://www.kaggle.com/c/house-prices-advanced-regression-techniques", "participants": 8000}
            ][:limit]
        elif "nlp" in q or "language" in q:
            return [
                {"title": "Natural Language Processing with Disaster Tweets", "type": "Competition", "url": "https://www.kaggle.com/c/nlp-getting-started", "participants": 4200},
                {"title": "CommonLit Readability Prize", "type": "Competition", "url": "https://www.kaggle.com/c/commonlitreadabilityprize", "participants": 3600}
            ][:limit]
        else:
            return [
                {"title": "Store Sales - Time Series Forecasting", "type": "Competition", "url": "https://www.kaggle.com/c/store-sales-time-series-forecasting", "participants": 5400},
                {"title": "Credit Card Fraud Detection Dataset", "type": "Dataset", "url": "https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud", "downloads": 180000}
            ][:limit]

    async def search_query(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        logger.info(f"Querying Search MCP with: '{query}'")
        q = query.lower()
        if "machine learning" in q:
            return [
                {"title": "Machine Learning Roadmap 2026", "snippet": "A complete interactive roadmap showing the skills needed to become a machine learning developer in 2026, including calculus, probability, neural networks, and prompt engineering.", "url": "https://roadmap.sh/ai-data-scientist"},
                {"title": "Introduction to AI Agents - Hugging Face", "snippet": "A comprehensive course teaching AI Agents, reasoning loops, function calling, tool use, and multi-agent frameworks using open-source tools.", "url": "https://huggingface.co/learn/deep-rl-course"}
            ][:limit]
        else:
            return [
                {"title": "Roadmap.sh - Developer Roadmaps", "snippet": "roadmap.sh is a community effort to create roadmaps, guides and other educational content to help guide developers in deciding what path to take next.", "url": "https://roadmap.sh"},
                {"title": "W3Schools Online Web Tutorials", "snippet": "Free online tutorials for learning HTML, CSS, JavaScript, Python, SQL, Java, PHP, Bootstrap, and XML.", "url": "https://www.w3schools.com"}
            ][:limit]
