"use client";

import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/context/AuthContext";
import { Sidebar } from "@/components/Sidebar";
import { ChatArea } from "@/components/ChatArea";
import { TemplateManager } from "@/components/TemplateManager";

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState("chat");
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [selectedTemplateContent, setSelectedTemplateContent] = useState<string | undefined>(undefined);

  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-slate-950 text-slate-400">
        <div className="flex flex-col items-center gap-3">
          <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
          <p className="text-xs">Authenticating workspace...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  const handleSelectTemplate = (content: string) => {
    setSelectedTemplateContent(content);
    setActiveTab("chat");
  };

  return (
    <div className="flex h-screen overflow-hidden bg-slate-950">
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        activeConversationId={activeConversationId}
        setActiveConversationId={setActiveConversationId}
      />
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab === "chat" && (
          <ChatArea
            conversationId={activeConversationId}
            selectedTemplateContent={selectedTemplateContent}
          />
        )}
        {activeTab === "templates" && (
          <TemplateManager onSelectTemplate={handleSelectTemplate} />
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
