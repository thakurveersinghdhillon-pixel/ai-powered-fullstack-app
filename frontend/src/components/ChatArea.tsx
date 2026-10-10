"use client";

import React, { useState } from "react";
import { MessageInput } from "./MessageInput";
import { Bot, User, Sparkles } from "lucide-react";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: string;
}

export const ChatArea: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Welcome to the AI Assistant Hub (Phase 1 Skeleton). The application infrastructure is currently initialized. Ask a question to see placeholder interactivity.",
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);

  const handleSendMessage = (text: string) => {
    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: text,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    const placeholderAssistantMsg: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: `[Placeholder Response]: Received prompt "${text}". Real-time LLM streaming will be connected in Phase 4.`,
      timestamp: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };

    setMessages((prev) => [...prev, userMsg, placeholderAssistantMsg]);
  };

  return (
    <div className="flex-1 flex flex-col h-screen bg-slate-950">
      {/* Header */}
      <header className="px-6 py-4 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="text-indigo-400" size={20} />
          <h2 className="font-medium text-slate-200">Active Conversation</h2>
        </div>
        <div className="text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full">
          Phase 1 Foundation Setup
        </div>
      </header>

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
            >
              {msg.role === "assistant" && (
                <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0">
                  <Bot size={18} />
                </div>
              )}
              <div
                className={`max-w-2xl rounded-2xl px-4 py-3 text-sm leading-relaxed ${
                  msg.role === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : "bg-slate-900 border border-slate-800 text-slate-200 rounded-bl-none"
                }`}
              >
                <p>{msg.content}</p>
                <span className="block text-[10px] opacity-60 mt-1 text-right">
                  {msg.timestamp}
                </span>
              </div>
              {msg.role === "user" && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300 shrink-0">
                  <User size={18} />
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Input */}
      <MessageInput onSendMessage={handleSendMessage} />
    </div>
  );
};
