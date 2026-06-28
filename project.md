# EduPilot AI - Project Specifications & Workflows

EduPilot AI is a state-of-the-art, multi-agent student mentoring and career roadmap acceleration platform. Built on the **Google Agent Development Kit (ADK)** framework, the system coordinates multiple AI specialist agents under a single Orchestrator to guide students, manage roadmap syllabi, supply external learning resources via Model Context Protocol (MCP) clients, and grade student portfolios.

---

## System Architecture Overview

```mermaid
graph TD
    User([Student Client]) <--> |HTTP / JSON| API[FastAPI Server]
    
    subgraph Backend [FastAPI Application Tier]
        API <--> ORC[Orchestrator Agent]
        ORC <--> MEM[SQLite Memory DB]
        ORC <--> SEC[Security Guard Manager]
        
        subgraph SubAgents [Google ADK Agent Layer]
            ORC --> |1. Analyze & Classify| CA[Career Advisor - Blue]
            ORC --> |2. Sequence Roadmaps| LP[Learning Planner - Cyan]
            ORC --> |3. Query Materials| RD[Resource Discovery - Purple]
            ORC --> |4. Grade Projects| PE[Progress Evaluation - Green]
            ORC --> |5. Fuel Stamina| MC[Motivation Coach - Orange]
        end
        
        subgraph MCP [Model Context Protocol Clients]
            RD --> GH[GitHub MCP Client]
            RD --> YT[YouTube MCP Client]
            RD --> KG[Kaggle MCP Client]
            RD --> SE[Google Search MCP Client]
        end
    end
```

---

## 1. Onboarding & Multi-Agent Routing Flow

The Orchestrator intercepts student prompts and coordinates dynamic routing to specialized sub-agents. It uses a **Single Director, Multiple Specialists** paradigm to execute workflows sequentially or conditionally depending on the user's intent.

```mermaid
sequenceDiagram
    autonumber
    actor User as Student Client
    participant ORC as Orchestrator
    participant SEC as Security Guard
    participant DB as SQLite DB
    participant AG as Specialized Agent(s)
    
    User->>ORC: Send Message / Prompt
    ORC->>SEC: Sanitize & Scan (Check Injection)
    alt Safe Prompt
        SEC-->>ORC: Access Granted
        ORC->>DB: Fetch Session History & Profile
        DB-->>ORC: Return Session State
        ORC->>ORC: Determine Routing (Career, Planner, Resource, etc.)
        loop Each Triggered Agent
            ORC->>AG: Dispatch Task
            AG-->>ORC: Return Agent Output
        end
        ORC->>DB: Save Messages & State Changes
        ORC-->>User: Aggregate Markdown Response
    else Injection Detected / Unsafe
        SEC-->>ORC: Access Denied (Flag Threat)
        ORC-->>User: Return Security Warning / Safe Default
    end
```

---

## 2. Project Evaluation & Portfolio Grading Pipeline

When a student submits a coding task or milestone project for review, the Orchestrator invokes the **Progress Evaluator** to grade the code and the **Motivation Coach** to update their learning streak metrics.

```mermaid
sequenceDiagram
    autonumber
    actor User as Student Client
    participant ORC as Orchestrator
    participant PE as Progress Evaluator
    participant DB as SQLite DB
    participant MC as Motivation Coach
    
    User->>ORC: Submit Project (Title, Description, Code)
    ORC->>PE: Route to Progress Evaluator
    PE->>PE: Analyze Code & Score (out of 100)
    PE->>PE: Generate Feedback
    PE->>DB: Save Grade & Feedback in `completed_projects`
    PE->>DB: Mark matching Milestone as Completed
    PE-->>ORC: Evaluation Complete
    ORC->>MC: Route to Motivation Coach
    MC->>DB: Check Streak & Activity Logs
    DB-->>MC: Return Streak Data
    MC->>MC: Increment Streak & Generate Encouragement
    MC-->>ORC: Coach Message
    ORC-->>User: Return Grade + Feedback + Encouragement Quote
```

---

## 3. Resource Discovery & MCP Integration Flow

The **Resource Discovery** agent connects to external resources using Model Context Protocol (MCP) clients to fetch real-world data like repositories, playlists, datasets, or search terms matching the student's study plan.

```mermaid
graph LR
    User([Student]) -->|Query Skill| ORC(Orchestrator)
    ORC -->|Route| RD(Resource Discovery Agent)
    
    subgraph MCP [Model Context Protocol Clients]
        RD -->|Search Code| GH[GitHub API]
        RD -->|Find Videos| YT[YouTube API]
        RD -->|Find Datasets| KG[Kaggle API]
        RD -->|General Search| SE[Google Search API]
    end
    
    GH -->|Repo Links| RD
    YT -->|Video Tutorials| RD
    KG -->|Dataset Links| RD
    SE -->|Web References| RD
    
    RD -->|Compiled Materials| ORC
    ORC -->|Structured Roadmap Resource List| User
```

---

## Agent Roles & Visual Branding Guidelines

To represent routing live on the dashboard UI, each agent is mapped to a distinct color code and UI badge:

| Agent | Brand Color | Hex Code | Primary Mandate |
| :--- | :--- | :--- | :--- |
| **Career Advisor** | Electric Blue | `#3B82F6` | Analyzes student interests and suggests target roles. |
| **Learning Planner** | Cyan Glow | `#06B6D4` | Generates 3-step checklist milestones and custom syllabi. |
| **Resource Discovery** | Royal Purple | `#A855F7` | Integrates with external MCP servers for code & tutorials. |
| **Progress Evaluator** | Forest Green | `#22C55E` | Grades project code submissions and provides technical reviews. |
| **Motivation Coach** | Solar Orange | `#F97316` | Manages learning streaks, activity counts, and motivational quotes. |
