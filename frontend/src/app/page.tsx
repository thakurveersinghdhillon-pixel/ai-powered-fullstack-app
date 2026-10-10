"use client";

import React, { useState } from "react";
import { Sidebar } from "@/components/Sidebar";
import { ChatArea } from "@/components/ChatArea";

export default function Home() {
  const [activeTab, setActiveTab] = useState("chat");

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />
      <main className="flex-1 flex flex-col">
        {activeTab === "chat" && <ChatArea />}
        {activeTab === "templates" && (
          <div className="flex-1 p-8 bg-slate-950 flex flex-col items-center justify-center text-center">
            <h3 className="text-xl font-semibold text-slate-200 mb-2">Prompt Templates</h3>
            <p className="text-sm text-slate-400 max-w-md">
              Reusable prompt templates with variable interpolation will be implemented in Phase 3.
            </p>
          </div>
        )}
        {activeTab === "analytics" && (
          <div className="flex-1 p-8 bg-slate-950 flex flex-col items-center justify-center text-center">
            <h3 className="text-xl font-semibold text-slate-200 mb-2">Token Usage & Cost Analytics</h3>
            <p className="text-sm text-slate-400 max-w-md">
              Token tracking, response latency charts, and cost estimation widgets will be implemented in Phase 6.
            </p>
          </div>
        )}
      </main>
    </div>
  );
}
