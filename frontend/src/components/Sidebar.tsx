"use client";

import React from "react";
import { MessageSquare, LayoutTemplate, BarChart2, Plus, Settings } from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 h-screen flex flex-col justify-between p-4">
      <div>
        <div className="flex items-center gap-2 px-2 py-3 mb-6 border-b border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white">
            AI
          </div>
          <div>
            <h1 className="font-semibold text-slate-100 text-sm">AI Assistant Hub</h1>
            <p className="text-xs text-slate-400">Skeleton Foundation</p>
          </div>
        </div>

        <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-sm font-medium py-2 px-4 rounded-lg flex items-center justify-center gap-2 mb-6 transition-colors">
          <Plus size={16} />
          <span>New Chat</span>
        </button>

        <nav className="space-y-1">
          <button
            onClick={() => setActiveTab("chat")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeTab === "chat"
                ? "bg-slate-800 text-indigo-400 font-medium"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            }`}
          >
            <MessageSquare size={18} />
            <span>Conversations</span>
          </button>

          <button
            onClick={() => setActiveTab("templates")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeTab === "templates"
                ? "bg-slate-800 text-indigo-400 font-medium"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            }`}
          >
            <LayoutTemplate size={18} />
            <span>Prompt Templates</span>
          </button>

          <button
            onClick={() => setActiveTab("analytics")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
              activeTab === "analytics"
                ? "bg-slate-800 text-indigo-400 font-medium"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            }`}
          >
            <BarChart2 size={18} />
            <span>Token Analytics</span>
          </button>
        </nav>
      </div>

      <div className="border-t border-slate-800 pt-4">
        <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm text-slate-400 hover:bg-slate-800/50 hover:text-slate-200 transition-colors">
          <Settings size={18} />
          <span>Settings</span>
        </button>
      </div>
    </aside>
  );
};
