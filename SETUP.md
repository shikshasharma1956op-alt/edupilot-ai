# EduPilot AI Setup & Installation Guide

This guide explains how to install dependencies, run the applications locally, execute tests, and configure cloud deployments.

---

## 1. Prerequisites

- **Python 3.10+** (Required by Google ADK)
- **Node.js 18+** & **npm**
- **Docker** & **Docker Compose** (Optional, for containerized run)

---

## 2. Local Installation (Development Mode)

### A. Python Backend Setup
1. Open a terminal in the project directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Linux/macOS:
   source venv/bin/activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

### B. Next.js Frontend Setup
1. Open a new terminal in the project directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Next.js development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to: `http://localhost:3000`

---

## 3. Environment Variables Configuration

To use real Google Gemini models instead of the default simulated local agent responses, configure the following variables in a `.env` file inside the `backend/` directory:

```env
# Google Vertex AI or Gemini API Credential (Required for live ADK agents)
GEMINI_API_KEY=your_gemini_api_key_here

# Enable/Disable Mock Fallbacks
MOCK_MODE=false

# Google ADK Target Model
GEMINI_MODEL=gemini-2.5-flash

# Optional: MCP Server Tokens for live Search/Github tools
GITHUB_TOKEN=your_github_token
YOUTUBE_API_KEY=your_youtube_api_key
KAGGLE_USERNAME=your_kaggle_username
KAGGLE_KEY=your_kaggle_key
```

---

## 4. Execution & Testing

### Running Unit Tests
In the virtual environment, execute pytest from the workspace directory:
```bash
python -m pytest backend/tests/
```

### Running the Local CLI Simulation
Verify the orchestrator routing and database storage commits using the demo script:
```bash
python demo_script.py
```

---

## 5. Cloud Deployments

### Option A: Railway
1. Install the Railway CLI or connect your GitHub repository to Railway.
2. Railway will automatically detect the `docker-compose.yml` or standard buildpacks.
3. Configure `GEMINI_API_KEY` and `MOCK_MODE` in the Railway dashboard variables.
4. Set the frontend environment variable `NEXT_PUBLIC_API_URL` to point to your Railway backend URL.

### Option B: Google Cloud Run (Containerized)
Build and push the backend docker container to Google Artifact Registry:
```bash
# Build backend image
docker build -t gcr.io/your-project-id/edupilot-backend ./backend

# Push and deploy
docker push gcr.io/your-project-id/edupilot-backend
gcloud run deploy edupilot-backend --image gcr.io/your-project-id/edupilot-backend --platform managed --allow-unauthenticated
```
