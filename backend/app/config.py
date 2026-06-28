import os
from pathlib import Path
from dotenv import load_dotenv

# Load env file if it exists
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Application Configuration
APP_NAME = "EduPilot AI"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/edupilot.db")

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
KAGGLE_USERNAME = os.getenv("KAGGLE_USERNAME", "")
KAGGLE_KEY = os.getenv("KAGGLE_KEY", "")

# Google ADK Model Configurations
# Defaulting to gemini-2.5-flash as the latest standard model
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# Fallback simulation mode
# If GEMINI_API_KEY is not provided, the backend falls back to realistic mock mode
# to allow complete application testing/evaluation without valid Google API Keys.
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true" or not GEMINI_API_KEY

# Set Gemini API Key in the OS environment for ADK integration if it is present
if GEMINI_API_KEY and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY
if GEMINI_API_KEY and "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
