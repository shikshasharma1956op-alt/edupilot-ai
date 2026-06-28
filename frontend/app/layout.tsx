import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EduPilot AI - Multi-Agent Mentor Platform",
  description: "A premium AI coach matching interests to career paths, establishing custom learning roadmaps, tracking progress, and discovering online resources.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased min-h-screen bg-brand-bg text-slate-100 selection:bg-brand-blue selection:text-white">
        {children}
      </body>
    </html>
  );
}
