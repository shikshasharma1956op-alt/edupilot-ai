"use client";

import React, { useState, useEffect, useRef } from "react";
import { 
  Compass, 
  Map, 
  BookOpen, 
  Award, 
  Flame, 
  Settings, 
  Send, 
  Sparkles, 
  Activity, 
  CheckCircle,
  FileCode,
  AlertTriangle,
  Play,
  RotateCcw
} from "lucide-react";

// Types
interface Message {
  role: string;
  content: string;
  agent_name?: string | null;
  timestamp?: string;
}

interface Milestone {
  id: number;
  title: string;
  description: string;
  is_completed: boolean;
  score?: number | null;
  feedback?: string | null;
}

interface Project {
  id: number;
  title: string;
  description: string;
  score: number;
  feedback: string;
  code_snippet?: string | null;
  created_at: string;
}

interface AgentLog {
  agent: string;
  status: string; // "running" | "completed" | "failed" | "pending"
  color: string;
}

export default function Dashboard() {
  // Session Configuration
  const [sessionId, setSessionId] = useState("session_dashboard_demo");
  const [userId, setUserId] = useState("john_doe");
  const [activeTab, setActiveTab] = useState<"chat" | "roadmap" | "portfolio" | "settings">("chat");

  // State Management
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState("");
  const [milestones, setMilestones] = useState<Milestone[]>([]);
  const [projects, setProjects] = useState<Project[]>([]);
  const [targetRole, setTargetRole] = useState<string | null>(null);
  const [careerInterests, setCareerInterests] = useState<string[]>([]);
  const [executionLogs, setExecutionLogs] = useState<AgentLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isBackendOnline, setIsBackendOnline] = useState(true);

  // Settings State
  const [mockMode, setMockMode] = useState(true);
  const [geminiModel, setGeminiModel] = useState("gemini-2.5-flash");

  // Project evaluation modal or inputs
  const [projectTitleInput, setProjectTitleInput] = useState("");
  const [projectDescInput, setProjectDescInput] = useState("");
  const [projectCodeInput, setProjectCodeInput] = useState("");

  const chatEndRef = useRef<HTMLDivElement>(null);

  // Agent Map for UI Graph Mapping
  const agents = [
    { name: "Career Advisor", label: "Career Advisor", color: "text-blue-400 bg-blue-500/10 border-blue-500/30", glowClass: "shadow-glow-agent-career", key: "career" },
    { name: "Learning Planner", label: "Learning Planner", color: "text-cyan-400 bg-cyan-500/10 border-cyan-500/30", glowClass: "shadow-glow-agent-planner", key: "planner" },
    { name: "Resource Discovery", label: "Resource Hunter", color: "text-purple-400 bg-purple-500/10 border-purple-500/30", glowClass: "shadow-glow-agent-resource", key: "resource" },
    { name: "Progress Evaluation", label: "Progress Evaluator", color: "text-green-400 bg-green-500/10 border-green-500/30", glowClass: "shadow-glow-agent-evaluator", key: "evaluator" },
    { name: "Motivation Coach", label: "Motivation Coach", color: "text-orange-400 bg-orange-500/10 border-orange-500/30", glowClass: "shadow-glow-agent-coach", key: "coach" },
  ];

  const API_BASE = "http://localhost:8000/api";

  // Initial load
  useEffect(() => {
    fetchSessionData();
  }, [sessionId]);

  // Scroll to bottom on new messages
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const fetchSessionData = async () => {
    try {
      // 1. Check health
      const healthRes = await fetch("http://localhost:8000/");
      if (healthRes.ok) {
        setIsBackendOnline(true);
      }
      
      // 2. Load Profile
      const profileRes = await fetch(`${API_BASE}/sessions/${sessionId}`);
      if (profileRes.ok) {
        const profile = await profileRes.json();
        setTargetRole(profile.target_role);
        setCareerInterests(profile.career_interests || []);
      }

      // 3. Load Chat History
      const historyRes = await fetch(`${API_BASE}/sessions/${sessionId}/history`);
      if (historyRes.ok) {
        const historyData = await historyRes.json();
        setMessages(historyData.messages || []);
      }

      // 4. Load Milestones
      const milestonesRes = await fetch(`${API_BASE}/sessions/${sessionId}/milestones`);
      if (milestonesRes.ok) {
        const mData = await milestonesRes.json();
        setMilestones(mData.milestones || []);
      }

      // 5. Load Completed Projects
      const projectsRes = await fetch(`${API_BASE}/sessions/${sessionId}/projects`);
      if (projectsRes.ok) {
        const pData = await projectsRes.json();
        setProjects(pData.projects || []);
      }

      // 6. Load Settings
      const settingsRes = await fetch(`${API_BASE}/settings`);
      if (settingsRes.ok) {
        const sData = await settingsRes.json();
        setMockMode(sData.mock_mode);
        setGeminiModel(sData.gemini_model);
      }
    } catch (e) {
      console.warn("Backend offline or unreachable. Loading simulated data.");
      setIsBackendOnline(false);
      loadSimulatedData();
    }
  };

  const loadSimulatedData = () => {
    setTargetRole("Machine Learning Engineer");
    setCareerInterests(["Python", "Mathematics", "Statistics", "Machine Learning"]);
    setMessages([
      { role: "assistant", content: "👋 Hello! I am **EduPilot AI**, your multi-agent mentor. I help you plan career paths, learn skills, search GitHub/YouTube resources, evaluate your code, and maintain streak goals!\n\nTo begin, tell me about your goals (e.g. *'I want to learn frontend React'* or *'Help me become an ML engineer'*).", agent_name: "Orchestrator" }
    ]);
    setMilestones([
      { id: 1, title: "Milestone 1: Python Data Science Foundations", description: "Master NumPy, Pandas, Matplotlib, and basic statistical regression concepts.", is_completed: true, score: 92, feedback: "Awesome start! Great data analytics logic." },
      { id: 2, title: "Milestone 2: Core Machine Learning Models", description: "Implement classification and regression algorithms using Scikit-Learn; evaluate metrics.", is_completed: false },
      { id: 3, title: "Milestone 3: Deep Learning Capstone", description: "Train and deploy a neural network model using PyTorch or TensorFlow, and write a model evaluation dashboard.", is_completed: false }
    ]);
    setProjects([
      { id: 1, title: "Foundational Python Data Science", description: "Data analytics processing on student registry data using Pandas and NumPy.", score: 92, feedback: "Excellent performance, efficient vectorized data operations. Try adding structured exception handling.", created_at: new Date().toISOString() }
    ]);
  };

  const handleSendMessage = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputMessage.trim()) return;

    const userText = inputMessage;
    setInputMessage("");
    setIsLoading(true);

    // Optimistically update message list
    setMessages(prev => [...prev, { role: "user", content: userText }]);

    // Initialize routing visual logs
    const initialLogs = orchestratorRoutingLogic(userText).map(agent => ({
      agent, status: "running", color: getAgentColorName(agent)
    }));
    setExecutionLogs(initialLogs);

    if (isBackendOnline) {
      try {
        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: sessionId, message: userText, user_id: userId })
        });
        
        if (response.ok) {
          const data = await response.json();
          setMessages(prev => [...prev, { role: "assistant", content: data.response, agent_name: "Orchestrator" }]);
          setExecutionLogs(data.execution_logs);
          
          // Re-fetch milestones and profile in case they were updated
          setTimeout(fetchSessionData, 1000);
        } else {
          setMessages(prev => [...prev, { role: "assistant", content: "❌ *Failed to communicate with agent engine.*", agent_name: "Orchestrator" }]);
        }
      } catch (err) {
        console.error(err);
        setMessages(prev => [...prev, { role: "assistant", content: "❌ *Network connection lost.*", agent_name: "Orchestrator" }]);
      }
    } else {
      // Simulate backend routing and responses
      setTimeout(() => {
        const targetAgents = orchestratorRoutingLogic(userText);
        const aggregatedResponses: string[] = [];
        
        targetAgents.forEach(agent => {
          if (agent === "Career Advisor") {
            aggregatedResponses.push("### 🧭 Career Guidance (Simulated Blue)\n\nBased on your message, I've targetted your path to **Machine Learning Engineer**!\n\n#### Demand outlook:\n- **Growth Rate:** +33%.\n- **Skills needed:** Python, Calculus, Linear Algebra, Scikit-Learn.");
            setTargetRole("Machine Learning Engineer");
          } else if (agent === "Learning Planner") {
            aggregatedResponses.push("### 🗺️ Learning Roadmap (Simulated Cyan)\n\nI've generated a 3-step learning plan for you:\n- **Milestone 1:** Python Foundations\n- **Milestone 2:** Scikit-Learn Classification\n- **Milestone 3:** Deep Learning Capstone Project.");
          } else if (agent === "Resource Discovery") {
            aggregatedResponses.push("### 🔍 Resource Hunter (Simulated Purple)\n\nFound these resources:\n- [GitHub: awesome-machine-learning](https://github.com/josephmisiti/awesome-machine-learning) (★ 60k)\n- [YouTube: StatQuest ML Basics](https://www.youtube.com/watch?v=Gv9_4yMHFhI)");
          } else if (agent === "Progress Evaluation") {
            aggregatedResponses.push("### 📈 Progress Evaluator (Simulated Green)\n\nLet's check your milestone status! Submit a code snippet or description to evaluate.");
          } else if (agent === "Motivation Coach") {
            aggregatedResponses.push("### ⚡ Motivation Coach (Simulated Orange)\n\nKeep pushing! You are doing fantastic. A 4-day streak is solid progress! 🔥");
          }
        });

        const completedLogs = initialLogs.map(log => ({ ...log, status: "completed" }));
        setExecutionLogs(completedLogs);
        setMessages(prev => [...prev, { role: "assistant", content: aggregatedResponses.join("\n\n---\n\n"), agent_name: "Orchestrator" }]);
      }, 1500);
    }
    setIsLoading(false);
  };

  const orchestratorRoutingLogic = (text: str): string[] => {
    const p = text.lower ? text.lower() : text.toLowerCase();
    const is_onboarding = ["learn", "become", "career", "start"].some(x => p.includes(x));
    if (is_onboarding) return ["Career Advisor", "Learning Planner", "Resource Discovery"];
    if (["github", "youtube", "kaggle", "resource"].some(x => p.includes(x))) return ["Resource Discovery"];
    if (["evaluate", "quiz", "code"].some(x => p.includes(x))) return ["Progress Evaluation"];
    if (["motivate", "streak", "tired"].some(x => p.includes(x))) return ["Motivation Coach"];
    return ["Career Advisor", "Motivation Coach"];
  };

  const getAgentColorName = (name: str): string => {
    if (name === "Career Advisor") return "blue";
    if (name === "Learning Planner") return "cyan";
    if (name === "Resource Discovery") return "purple";
    if (name === "Progress Evaluation") return "green";
    return "orange";
  };

  const handleToggleMilestone = async (id: number, currentStatus: boolean) => {
    const nextStatus = !currentStatus;
    // Optimistic UI updates
    setMilestones(prev => prev.map(m => m.id === id ? { ...m, is_completed: nextStatus } : m));

    if (isBackendOnline) {
      try {
        await fetch(`${API_BASE}/milestones/${id}/toggle`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ is_completed: nextStatus })
        });
        fetchSessionData();
      } catch (err) {
        console.error(err);
      }
    }
  };

  const submitProjectForEvaluation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!projectTitleInput.trim() || !projectDescInput.trim()) return;

    setIsLoading(true);
    const prompt = `Please evaluate my project titled "${projectTitleInput}". Description: ${projectDescInput}.`;
    
    // Add message
    setMessages(prev => [...prev, { role: "user", content: `**Submitting Project:** ${projectTitleInput}\n\n*Description:* ${projectDescInput}\n\n*Code:* \`\`\`python\n${projectCodeInput}\n\`\`\`` }]);
    setProjectTitleInput("");
    setProjectDescInput("");
    setProjectCodeInput("");
    
    setExecutionLogs([{ agent: "Progress Evaluation", status: "running", color: "green" }]);

    if (isBackendOnline) {
      try {
        const response = await fetch(`${API_BASE}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            session_id: sessionId,
            message: `${prompt} Code: \`\`\`python\n${projectCodeInput}\n\`\`\``
          })
        });
        
        if (response.ok) {
          const data = await response.json();
          setMessages(prev => [...prev, { role: "assistant", content: data.response, agent_name: "Orchestrator" }]);
          setExecutionLogs(data.execution_logs);
          fetchSessionData();
        }
      } catch (err) {
        console.error(err);
      }
    } else {
      setTimeout(() => {
        setExecutionLogs([{ agent: "Progress Evaluation", status: "completed", color: "green" }]);
        
        const mockScore = 85;
        const mockFeedback = "Good component mapping. Needs structural error checking.";
        
        setProjects(prev => [
          { id: Date.now(), title: projectTitleInput, description: projectDescInput, score: mockScore, feedback: mockFeedback, created_at: new Date().toISOString() },
          ...prev
        ]);
        
        // Mark milestone 3 as completed
        setMilestones(prev => prev.map((m, idx) => idx === prev.length - 1 ? { ...m, is_completed: true, score: mockScore, feedback: mockFeedback } : m));
        
        setMessages(prev => [...prev, {
          role: "assistant",
          content: `### 📈 Progress Evaluator (Simulated Green)\n\n**Submission Grade:** \`${mockScore}/100\` ⭐\n\n**Feedback:** ${mockFeedback}\n\n✅ *Milestone 3 is now checked off!*`,
          agent_name: "Orchestrator"
        }]);
      }, 1500);
    }
    setIsLoading(false);
    setActiveTab("chat");
  };

  const handleUpdateSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isBackendOnline) {
      try {
        await fetch(`${API_BASE}/settings`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ mock_mode: mockMode, gemini_model: geminiModel })
        });
        alert("Settings saved successfully!");
      } catch (err) {
        console.error(err);
      }
    } else {
      alert("Simulated settings saved locally!");
    }
  };

  const resetSession = async () => {
    if (confirm("Reset current session data? This will clear logs and database records.")) {
      const newSessionId = `session_${Math.random().toString(36).substring(2, 9)}`;
      setSessionId(newSessionId);
    }
  };

  // Helper to color messages depending on sending agent
  const getMessageStyles = (msg: Message) => {
    if (msg.role === "user") {
      return "bg-brand-blue/15 border-brand-blue/30 text-slate-100 ml-auto max-w-[80%]";
    }
    
    // Check if contains specific agent headers to color border
    const c = msg.content;
    if (c.includes("Blue") || c.includes("Guidance") || c.includes("Career")) {
      return "border-l-4 border-l-blue-500 bg-brand-card/50 max-w-[90%]";
    }
    if (c.includes("Cyan") || c.includes("Roadmap") || c.includes("Syllabus")) {
      return "border-l-4 border-l-cyan-400 bg-brand-card/50 max-w-[90%]";
    }
    if (c.includes("Purple") || c.includes("Resource") || c.includes("Hunter")) {
      return "border-l-4 border-l-purple-500 bg-brand-card/50 max-w-[90%]";
    }
    if (c.includes("Green") || c.includes("Evaluator") || c.includes("Quiz")) {
      return "border-l-4 border-l-green-500 bg-brand-card/50 max-w-[90%]";
    }
    if (c.includes("Orange") || c.includes("Coach") || c.includes("Streak")) {
      return "border-l-4 border-l-orange-500 bg-brand-card/50 max-w-[90%]";
    }
    
    return "bg-brand-card/40 border-slate-700/50 max-w-[90%]";
  };

  return (
    <div className="flex h-screen bg-brand-bg text-slate-200">
      
      {/* 1. LEFT SIDEBAR: Stats and Settings */}
      <aside className="w-80 bg-brand-card border-r border-slate-800/80 flex flex-col p-6 space-y-6">
        
        {/* Logo block */}
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-brand-blue/10 rounded-xl border border-brand-blue/40 text-brand-cyan shadow-glow">
            <Sparkles className="h-6 w-6 animate-pulse" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-wide font-outfit text-white">EduPilot AI</h1>
            <span className="text-[10px] text-brand-cyan tracking-wider font-mono">GOOGLE ADK ARCHITECTURE</span>
          </div>
        </div>

        {/* System status pill */}
        <div className="flex items-center justify-between p-3.5 bg-slate-900/60 rounded-xl border border-slate-800/50">
          <span className="text-xs text-slate-400 flex items-center gap-1.5">
            <Activity className="h-3.5 w-3.5" />
            Backend Engine
          </span>
          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${isBackendOnline ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-orange-500/10 text-orange-400 border border-orange-500/20'}`}>
            {isBackendOnline ? "ONLINE" : "SIMULATOR"}
          </span>
        </div>

        {/* Streak card */}
        <div className="bg-gradient-to-br from-brand-card to-slate-900 p-5 rounded-2xl border border-slate-800/60 flex items-center space-x-4 relative overflow-hidden">
          <div className="absolute right-0 bottom-0 translate-x-2 translate-y-2 opacity-5">
            <Flame className="h-24 w-24 text-orange-500" />
          </div>
          <div className="p-3 bg-orange-500/10 rounded-xl border border-orange-500/30 text-orange-400">
            <Flame className="h-6 w-6 fill-orange-500/20" />
          </div>
          <div>
            <span className="text-[10px] text-slate-400 uppercase tracking-widest font-mono">Learning Velocity</span>
            <h2 className="text-2xl font-bold text-white">4 Day Streak</h2>
          </div>
        </div>

        {/* Profile Stats */}
        <div className="space-y-3.5">
          <span className="text-[10px] text-slate-500 uppercase tracking-wider font-mono">Active Target Path</span>
          {targetRole ? (
            <div className="p-4 bg-brand-blue/5 rounded-xl border border-brand-blue/20">
              <h3 className="text-sm font-semibold text-white">{targetRole}</h3>
              <p className="text-xs text-brand-cyan/80 mt-1">Beginner Level</p>
              <div className="flex flex-wrap gap-1 mt-2.5">
                {careerInterests.map((interest, idx) => (
                  <span key={idx} className="text-[9px] bg-slate-900 text-slate-300 px-2 py-0.5 rounded-full border border-slate-800">
                    {interest}
                  </span>
                ))}
              </div>
            </div>
          ) : (
            <div className="p-4 bg-slate-900/40 rounded-xl border border-dashed border-slate-800 text-center">
              <p className="text-xs text-slate-500">No career roadmap active.</p>
              <span className="text-[10px] text-slate-600 block mt-1">Say onboarding message to generate</span>
            </div>
          )}
        </div>

        {/* Navigation tabs */}
        <nav className="flex-1 flex flex-col space-y-1.5 pt-4">
          <button
            onClick={() => setActiveTab("chat")}
            className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === "chat" ? 'bg-brand-blue text-white shadow-glow-blue' : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-100'}`}
          >
            <Compass className="h-4.5 w-4.5" />
            <span>AI Mentor Chat</span>
          </button>
          
          <button
            onClick={() => setActiveTab("roadmap")}
            className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === "roadmap" ? 'bg-brand-blue text-white shadow-glow-blue' : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-100'}`}
          >
            <Map className="h-4.5 w-4.5" />
            <span>Milestone Roadmaps</span>
          </button>

          <button
            onClick={() => setActiveTab("portfolio")}
            className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === "portfolio" ? 'bg-brand-blue text-white shadow-glow-blue' : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-100'}`}
          >
            <Award className="h-4.5 w-4.5" />
            <span>Graded Portfolio</span>
          </button>

          <button
            onClick={() => setActiveTab("settings")}
            className={`flex items-center space-x-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${activeTab === "settings" ? 'bg-brand-blue text-white shadow-glow-blue' : 'text-slate-400 hover:bg-slate-900/50 hover:text-slate-100'}`}
          >
            <Settings className="h-4.5 w-4.5" />
            <span>System Settings</span>
          </button>
        </nav>

        {/* Reset Session Footer button */}
        <div className="pt-4 border-t border-slate-800/80">
          <button
            onClick={resetSession}
            className="w-full flex items-center justify-center gap-1.5 py-2 px-3 text-xs bg-slate-900 text-slate-500 rounded-lg hover:text-slate-300 border border-slate-800 hover:border-slate-700 transition"
          >
            <RotateCcw className="h-3 w-3" />
            Reset Learning State
          </button>
        </div>
      </aside>

      {/* 2. MIDDLE AREA: Tabs Contents */}
      <main className="flex-1 flex flex-col min-w-0 bg-slate-950 overflow-hidden">
        
        {/* Top Header bar */}
        <header className="h-16 border-b border-slate-900 bg-brand-bg/50 backdrop-blur-md px-8 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h2 className="text-sm font-bold font-mono tracking-wider text-slate-400">
              {activeTab === "chat" && "ACTIVE CHAT TRANSCRIPT"}
              {activeTab === "roadmap" && "SYLLABUS MILESTONES"}
              {activeTab === "portfolio" && "GRADED SUBMISSIONS PORTFOLIO"}
              {activeTab === "settings" && "DEVELOPER CONTROL BOARD"}
            </h2>
          </div>
          
          <div className="flex items-center gap-2 text-xs bg-slate-900/40 px-3 py-1 rounded-md border border-slate-800/50 text-slate-400">
            <span className="w-1.5 h-1.5 rounded-full bg-brand-cyan shadow-glow animate-pulse"></span>
            Session ID: <span className="font-mono text-slate-300">{sessionId}</span>
          </div>
        </header>

        {/* Tab view area */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* TAB: Chat Transcript */}
          {activeTab === "chat" && (
            <div className="h-full flex flex-col space-y-4">
              
              {/* Chat bubbles list */}
              <div className="flex-1 space-y-4 overflow-y-auto pr-2 min-h-[400px]">
                {messages.map((msg, index) => (
                  <div
                    key={index}
                    className={`p-5 rounded-2xl border text-sm leading-relaxed transition-all shadow-sm ${getMessageStyles(msg)}`}
                  >
                    {msg.agent_name && (
                      <div className="flex items-center gap-1.5 text-[10px] uppercase font-mono tracking-wider text-brand-cyan mb-2">
                        <span className="w-1.5 h-1.5 bg-brand-cyan rounded-full shadow-glow"></span>
                        {msg.agent_name}
                      </div>
                    )}
                    <div className="whitespace-pre-wrap">{msg.content}</div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex items-center space-x-2 text-slate-400 text-xs p-4 bg-brand-card/25 rounded-xl border border-slate-800 w-[200px]">
                    <span className="w-2 h-2 bg-brand-cyan rounded-full animate-bounce"></span>
                    <span className="w-2 h-2 bg-brand-cyan rounded-full animate-bounce [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 bg-brand-cyan rounded-full animate-bounce [animation-delay:0.4s]"></span>
                    <span>Routing agents...</span>
                  </div>
                )}
                
                <div ref={chatEndRef} />
              </div>

              {/* Chat input box */}
              <form onSubmit={handleSendMessage} className="relative pt-4 border-t border-slate-900/80">
                <input
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder="Ask EduPilot (e.g., 'Help me learn machine learning', or 'Evaluate my code')"
                  className="w-full bg-brand-card border border-slate-800 rounded-xl py-3.5 pl-4 pr-12 text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-blue/80 focus:shadow-glow-blue transition-all"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  className="absolute right-3 top-7 p-1.5 bg-brand-blue text-white rounded-lg hover:shadow-glow-blue transition-all disabled:opacity-50"
                  disabled={isLoading}
                >
                  <Send className="h-4 w-4" />
                </button>
              </form>
            </div>
          )}

          {/* TAB: Roadmaps */}
          {activeTab === "roadmap" && (
            <div className="space-y-6">
              <div className="bg-brand-card p-6 rounded-2xl border border-slate-800/80">
                <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                  <Map className="h-5 w-5 text-brand-cyan" />
                  Roadmap Milestone List
                </h3>
                <p className="text-xs text-slate-400 mb-6">
                  Check off completed milestones as you study. Completing Milestones will automatically activate evaluations.
                </p>
                
                {milestones.length === 0 ? (
                  <div className="py-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
                    <AlertTriangle className="h-8 w-8 mx-auto text-slate-600 mb-2" />
                    <p className="text-sm">No milestones generated yet.</p>
                    <button 
                      onClick={() => {
                        setInputMessage("Create a learning plan for me");
                        setActiveTab("chat");
                      }}
                      className="mt-3 text-xs text-brand-cyan hover:underline"
                    >
                      Ask AI Mentor to make a plan
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {milestones.map((m) => (
                      <div 
                        key={m.id} 
                        className={`p-5 rounded-xl border transition-all ${m.is_completed ? 'bg-green-500/5 border-green-500/20' : 'bg-slate-900/50 border-slate-800/60'}`}
                      >
                        <div className="flex items-start justify-between">
                          <div className="flex items-start gap-4">
                            <input 
                              type="checkbox"
                              checked={m.is_completed}
                              onChange={() => handleToggleMilestone(m.id, m.is_completed)}
                              className="mt-1 h-5 w-5 rounded bg-slate-800 border-slate-700 text-brand-cyan focus:ring-0 cursor-pointer"
                            />
                            <div>
                              <h4 className={`text-sm font-bold ${m.is_completed ? 'text-slate-300 line-through' : 'text-white'}`}>{m.title}</h4>
                              <p className="text-xs text-slate-400 mt-1">{m.description}</p>
                              
                              {m.feedback && (
                                <div className="mt-3 p-3 bg-slate-900 rounded-lg text-xs border border-slate-800/80">
                                  <span className="text-[9px] uppercase font-mono text-green-400 font-bold block mb-1">Evaluator Feedback (Score: {m.score}/100)</span>
                                  {m.feedback}
                                </div>
                              )}
                            </div>
                          </div>
                          
                          <span className={`text-[10px] font-mono px-2 py-0.5 rounded-full ${m.is_completed ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-slate-950 text-slate-500 border border-slate-800'}`}>
                            {m.is_completed ? "COMPLETED" : "PENDING"}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Project evaluation form */}
              {milestones.length > 0 && (
                <div className="bg-brand-card p-6 rounded-2xl border border-slate-800/80">
                  <h3 className="text-md font-bold text-white mb-4 flex items-center gap-2">
                    <FileCode className="h-5 w-5 text-brand-cyan" />
                    Submit Project for Review
                  </h3>
                  
                  <form onSubmit={submitProjectForEvaluation} className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-[10px] text-slate-400 block mb-1 font-mono uppercase">Project Title</label>
                        <input
                          type="text"
                          required
                          value={projectTitleInput}
                          onChange={(e) => setProjectTitleInput(e.target.value)}
                          placeholder="e.g. Pandas Student Registry Analysis"
                          className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-blue"
                        />
                      </div>
                      <div>
                        <label className="text-[10px] text-slate-400 block mb-1 font-mono uppercase">Target Milestone</label>
                        <select className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-400 focus:outline-none">
                          <option>Milestone 3: Deep Learning Capstone</option>
                        </select>
                      </div>
                    </div>

                    <div>
                      <label className="text-[10px] text-slate-400 block mb-1 font-mono uppercase">Project Description</label>
                      <textarea
                        required
                        rows={2}
                        value={projectDescInput}
                        onChange={(e) => setProjectDescInput(e.target.value)}
                        placeholder="Detail what logic your project resolves..."
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-brand-blue"
                      />
                    </div>

                    <div>
                      <label className="text-[10px] text-slate-400 block mb-1 font-mono uppercase">Code Snippet (Optional)</label>
                      <textarea
                        rows={4}
                        value={projectCodeInput}
                        onChange={(e) => setProjectCodeInput(e.target.value)}
                        placeholder="Paste python code snippet here..."
                        className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-300 font-mono focus:outline-none focus:border-brand-blue"
                      />
                    </div>

                    <button
                      type="submit"
                      disabled={isLoading}
                      className="py-2.5 px-4 bg-brand-cyan hover:shadow-glow text-slate-950 font-bold rounded-lg text-xs transition"
                    >
                      Submit to Progress Evaluator
                    </button>
                  </form>
                </div>
              )}
            </div>
          )}

          {/* TAB: Portfolio */}
          {activeTab === "portfolio" && (
            <div className="bg-brand-card p-6 rounded-2xl border border-slate-800/80">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Award className="h-5 w-5 text-brand-cyan" />
                Student Portfolio Project Grades
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Your evaluated submissions, grading scores, and coach feedback are catalogued below.
              </p>

              {projects.length === 0 ? (
                <div className="py-12 text-center text-slate-500 border border-dashed border-slate-800 rounded-xl">
                  <AlertTriangle className="h-8 w-8 mx-auto text-slate-600 mb-2" />
                  <p className="text-sm">No project submissions evaluated yet.</p>
                </div>
              ) : (
                <div className="space-y-6">
                  {projects.map((p) => (
                    <div key={p.id} className="p-6 bg-slate-900/60 rounded-xl border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center gap-2.5">
                          <h4 className="text-sm font-bold text-white">{p.title}</h4>
                          <span className="text-[10px] text-slate-500 font-mono">{new Date(p.created_at).toLocaleDateString()}</span>
                        </div>
                        <p className="text-xs text-slate-400">{p.description}</p>
                        
                        <div className="p-3.5 bg-slate-950 rounded-lg text-xs border border-slate-800/80 mt-3">
                          <span className="text-[9px] uppercase font-mono text-green-400 font-bold block mb-1">Evaluator Feedback</span>
                          {p.feedback}
                        </div>

                        {p.code_snippet && (
                          <details className="mt-2 text-xs">
                            <summary className="cursor-pointer text-brand-cyan hover:underline">View Submitted Code</summary>
                            <pre className="mt-2 p-3 bg-slate-950 text-slate-300 font-mono text-[10px] rounded border border-slate-800 overflow-x-auto">
                              {p.code_snippet}
                            </pre>
                          </details>
                        )}
                      </div>

                      <div className="flex flex-col items-center justify-center p-5 bg-green-500/10 border border-green-500/20 rounded-xl min-w-[120px]">
                        <span className="text-[10px] font-mono text-green-400 tracking-wider">GRADE SCORE</span>
                        <span className="text-3xl font-extrabold text-white mt-1">{p.score}</span>
                        <span className="text-[9px] text-slate-500 mt-1">out of 100</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* TAB: Settings */}
          {activeTab === "settings" && (
            <div className="bg-brand-card p-6 rounded-2xl border border-slate-800/80 max-w-xl">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center gap-2">
                <Settings className="h-5 w-5 text-brand-cyan" />
                Agent Settings
              </h3>
              <p className="text-xs text-slate-400 mb-6">
                Configure execution parameters, model endpoints, and simulation mode targets.
              </p>

              <form onSubmit={handleUpdateSettings} className="space-y-4">
                <div>
                  <label className="text-[10px] text-slate-400 block mb-1 font-mono uppercase">Simulation / Mock Mode</label>
                  <div className="flex items-center gap-3">
                    <input 
                      type="checkbox"
                      checked={mockMode}
                      onChange={(e) => setMockMode(e.target.checked)}
                      className="h-4.5 w-4.5 rounded bg-slate-950 border-slate-800 text-brand-blue cursor-pointer"
                    />
                    <span className="text-xs text-slate-300">
                      Fallback to simulated responses (Allows testing without active Gemini API keys)
                    </span>
                  </div>
                </div>

                <div>
                  <label className="text-[10px] text-slate-400 block mb-1.5 font-mono uppercase">Google ADK Model Target</label>
                  <select
                    value={geminiModel}
                    onChange={(e) => setGeminiModel(e.target.value)}
                    className="w-full bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs text-slate-300 focus:outline-none focus:border-brand-blue"
                  >
                    <option value="gemini-2.5-flash">gemini-2.5-flash (Standard model)</option>
                    <option value="gemini-2.5-pro">gemini-2.5-pro (Advanced coding)</option>
                    <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                  </select>
                </div>

                <button
                  type="submit"
                  className="py-2.5 px-4 bg-brand-blue hover:shadow-glow-blue text-white font-bold rounded-lg text-xs transition"
                >
                  Save Configuration
                </button>
              </form>
            </div>
          )}

        </div>
      </main>

      {/* 3. RIGHT SIDEBAR: Orchestrator Agent Routing Flow Graph */}
      <aside className="w-80 bg-brand-card border-l border-slate-800/80 flex flex-col p-6 space-y-6">
        <div className="flex items-center justify-between border-b border-slate-800/80 pb-3">
          <h3 className="text-xs font-bold font-mono tracking-wider text-slate-400 flex items-center gap-1.5">
            <Activity className="h-4 w-4 text-brand-cyan" />
            AGENT ROUTING MAP
          </h3>
          <span className="text-[9px] bg-brand-blue/15 border border-brand-blue/30 text-brand-cyan px-2 py-0.5 rounded-full font-mono">
            REALTIME
          </span>
        </div>

        <p className="text-[11px] text-slate-400 leading-relaxed">
          This connection graph visualizes the Orchestrator routing user prompts to specialized sub-agents in real-time.
        </p>

        {/* The Connection Graph Nodes */}
        <div className="flex-1 flex flex-col justify-center space-y-5 relative">
          
          {/* Main Orchestrator Node */}
          <div className="flex justify-center z-10">
            <div className="px-4 py-2.5 bg-slate-900 border-2 border-indigo-500 rounded-xl text-center shadow-md min-w-[150px] relative">
              <span className="text-[9px] uppercase font-mono text-indigo-400 font-bold block">DIRECTOR</span>
              <span className="text-xs font-bold text-white">Orchestrator Agent</span>
              <div className="absolute w-0.5 h-6 bg-indigo-500/20 top-full left-1/2 -translate-x-1/2"></div>
            </div>
          </div>

          {/* Connective lines representation in CSS */}
          <div className="absolute top-[28%] bottom-[20%] left-1/2 w-0.5 bg-slate-800 -translate-x-1/2 z-0"></div>

          {/* Sub nodes for individual agents */}
          <div className="space-y-3.5 z-10">
            {agents.map((agent) => {
              const activeLog = executionLogs.find(l => l.agent === agent.name);
              const isRunning = activeLog?.status === "running";
              const isCompleted = activeLog?.status === "completed";
              
              return (
                <div 
                  key={agent.key} 
                  className={`p-3.5 bg-slate-900/90 rounded-xl border text-center transition-all ${agent.color} ${isRunning ? `animate-pulse-glow border-brand-cyan ${agent.glowClass}` : 'border-slate-800/80 opacity-60'}`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[8px] font-mono tracking-wider font-bold">AGENT</span>
                    {isRunning && (
                      <span className="text-[8px] bg-brand-cyan/15 text-brand-cyan px-1.5 py-0.5 rounded-md animate-pulse">ACTIVE</span>
                    )}
                    {isCompleted && (
                      <span className="text-[8px] bg-green-500/15 text-green-400 px-1.5 py-0.5 rounded-md">READY</span>
                    )}
                  </div>
                  <h4 className="text-xs font-bold mt-1.5 text-white">{agent.label}</h4>
                </div>
              );
            })}
          </div>

        </div>

        {/* Legend */}
        <div className="bg-slate-900/40 p-4 rounded-xl border border-slate-800/50 text-[10px] space-y-2">
          <span className="font-mono text-slate-500 block uppercase font-bold">Color Index</span>
          <div className="grid grid-cols-2 gap-1.5 text-slate-400">
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span> Career</span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-cyan-400 rounded-full"></span> Planner</span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-purple-500 rounded-full"></span> Resource</span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> Evaluate</span>
            <span className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 bg-orange-500 rounded-full"></span> Coach</span>
          </div>
        </div>

      </aside>

    </div>
  );
}
