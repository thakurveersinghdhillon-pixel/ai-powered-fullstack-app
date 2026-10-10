"use client";

import React, { useState, useEffect } from "react";
import { Conversation } from "@/lib/types";
import { api } from "@/lib/api";
import { useAuth } from "@/context/AuthContext";
import {
  MessageSquare,
  LayoutTemplate,
  BarChart2,
  Plus,
  LogOut,
  Edit2,
  Trash2,
  Check,
  X,
  Bot,
} from "lucide-react";

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  activeConversationId: string | null;
  setActiveConversationId: (id: string | null) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  setActiveTab,
  activeConversationId,
  setActiveConversationId,
}) => {
  const { user, accessToken, logout } = useAuth();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState("");

  const loadConversations = async () => {
    if (!accessToken) return;
    setIsLoading(true);
    try {
      const res = await api.getConversations(accessToken);
      setConversations(res.items);
      // Auto-select first conversation if none selected
      if (res.items.length > 0 && !activeConversationId) {
        setActiveConversationId(res.items[0].id);
      }
    } catch (err) {
      // Ignore initial list load errors
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadConversations();
  }, [accessToken]);

  const handleNewChat = async () => {
    if (!accessToken) return;
    try {
      const newConv = await api.createConversation(accessToken, "New Conversation");
      setConversations((prev) => [newConv, ...prev]);
      setActiveConversationId(newConv.id);
      setActiveTab("chat");
    } catch (err: any) {
      alert(err.message || "Failed to create conversation");
    }
  };

  const handleStartEdit = (e: React.MouseEvent, conv: Conversation) => {
    e.stopPropagation();
    setEditingId(conv.id);
    setEditTitle(conv.title);
  };

  const handleSaveEdit = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (!editTitle.trim() || !accessToken) return;
    try {
      const updated = await api.updateConversation(accessToken, convId, editTitle);
      setConversations((prev) =>
        prev.map((c) => (c.id === convId ? updated : c))
      );
      setEditingId(null);
    } catch (err: any) {
      alert(err.message || "Failed to rename conversation");
    }
  };

  const handleDelete = async (e: React.MouseEvent, convId: string) => {
    e.stopPropagation();
    if (!accessToken || !confirm("Are you sure you want to delete this conversation?")) return;
    try {
      await api.deleteConversation(accessToken, convId);
      setConversations((prev) => prev.filter((c) => c.id !== convId));
      if (activeConversationId === convId) {
        setActiveConversationId(null);
      }
    } catch (err: any) {
      alert(err.message || "Failed to delete conversation");
    }
  };

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 h-screen flex flex-col justify-between p-4 shrink-0">
      <div className="flex flex-col h-full overflow-hidden">
        {/* Workspace Brand */}
        <div className="flex items-center gap-2 px-2 py-3 mb-4 border-b border-slate-800">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center font-bold text-white shadow-lg">
            AI
          </div>
          <div className="overflow-hidden">
            <h1 className="font-semibold text-slate-100 text-sm truncate">AI Workspace</h1>
            <p className="text-[10px] text-slate-400 truncate">{user?.email || "Authenticated"}</p>
          </div>
        </div>

        {/* New Chat Button */}
        <button
          onClick={handleNewChat}
          className="w-full bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium py-2.5 px-4 rounded-xl flex items-center justify-center gap-2 mb-4 transition-colors shadow-md"
        >
          <Plus size={16} />
          <span>New Chat</span>
        </button>

        {/* Navigation Tabs */}
        <nav className="space-y-1 mb-4">
          <button
            onClick={() => setActiveTab("chat")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs transition-colors ${
              activeTab === "chat"
                ? "bg-slate-800 text-indigo-400 font-medium"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            }`}
          >
            <MessageSquare size={16} />
            <span>Chat Workspace</span>
          </button>

          <button
            onClick={() => setActiveTab("templates")}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs transition-colors ${
              activeTab === "templates"
                ? "bg-slate-800 text-indigo-400 font-medium"
                : "text-slate-400 hover:bg-slate-800/50 hover:text-slate-200"
            }`}
          >
            <LayoutTemplate size={16} />
            <span>Prompt Templates</span>
          </button>
        </nav>

        {/* Conversations List */}
        <div className="flex-1 overflow-y-auto pr-1 space-y-1 border-t border-slate-800/80 pt-3">
          <div className="px-2 text-[10px] font-semibold uppercase tracking-wider text-slate-500 mb-2">
            Conversations
          </div>

          {isLoading ? (
            <div className="text-xs text-slate-500 px-3 py-2">Loading...</div>
          ) : conversations.length === 0 ? (
            <div className="text-xs text-slate-600 px-3 py-2 italic">No conversations yet</div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => {
                  setActiveConversationId(conv.id);
                  setActiveTab("chat");
                }}
                className={`group flex items-center justify-between px-3 py-2 rounded-xl text-xs cursor-pointer transition-colors ${
                  activeConversationId === conv.id && activeTab === "chat"
                    ? "bg-slate-800/90 text-slate-100 font-medium border border-slate-700/50"
                    : "text-slate-400 hover:bg-slate-800/40 hover:text-slate-200"
                }`}
              >
                {editingId === conv.id ? (
                  <div className="flex items-center gap-1 w-full" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="text"
                      value={editTitle}
                      onChange={(e) => setEditTitle(e.target.value)}
                      className="w-full bg-slate-950 text-slate-100 px-2 py-1 rounded text-xs focus:outline-none border border-indigo-500"
                      autoFocus
                    />
                    <button
                      onClick={(e) => handleSaveEdit(e, conv.id)}
                      className="p-1 text-indigo-400 hover:text-indigo-300"
                    >
                      <Check size={14} />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingId(null);
                      }}
                      className="p-1 text-slate-500 hover:text-slate-300"
                    >
                      <X size={14} />
                    </button>
                  </div>
                ) : (
                  <>
                    <span className="truncate pr-2">{conv.title}</span>
                    <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity shrink-0">
                      <button
                        onClick={(e) => handleStartEdit(e, conv)}
                        className="p-1 hover:text-slate-200 text-slate-500 transition-colors"
                        title="Rename conversation"
                      >
                        <Edit2 size={13} />
                      </button>
                      <button
                        onClick={(e) => handleDelete(e, conv.id)}
                        className="p-1 hover:text-red-400 text-slate-500 transition-colors"
                        title="Delete conversation"
                      >
                        <Trash2 size={13} />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* User Footer & Logout */}
      <div className="border-t border-slate-800 pt-3 mt-2">
        <button
          onClick={() => logout()}
          className="w-full flex items-center gap-3 px-3 py-2 rounded-xl text-xs text-slate-400 hover:bg-slate-800/50 hover:text-red-400 transition-colors"
        >
          <LogOut size={16} />
          <span>Sign Out</span>
        </button>
      </div>
    </aside>
  );
};
