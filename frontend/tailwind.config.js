/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          bg: "#0B132B",      // Deep navy/slate dark background (70%)
          card: "#1C2541",    // Slate card background
          blue: "#0072FF",    // Electric blue actions/status indicators (20%)
          cyan: "#00F2FE",    // Cyan highlights/glows (10%)
          glow: "rgba(0, 242, 254, 0.15)",
        },
        agent: {
          career: "#3B82F6",    // Career Advisor - Blue
          planner: "#06B6D4",   // Learning Planner - Cyan
          resource: "#A855F7",  // Resource Hunter - Purple
          evaluator: "#22C55E", // Progress Evaluator - Green
          coach: "#F97316",     // Motivation Coach - Orange
        }
      },
      boxShadow: {
        glow: "0 0 15px rgba(0, 242, 254, 0.35)",
        "glow-blue": "0 0 15px rgba(0, 114, 255, 0.35)",
        "glow-agent-career": "0 0 12px rgba(59, 130, 246, 0.4)",
        "glow-agent-planner": "0 0 12px rgba(6, 182, 212, 0.4)",
        "glow-agent-resource": "0 0 12px rgba(168, 85, 247, 0.4)",
        "glow-agent-evaluator": "0 0 12px rgba(34, 197, 94, 0.4)",
        "glow-agent-coach": "0 0 12px rgba(249, 115, 22, 0.4)",
      }
    },
  },
  plugins: [],
}
