"use client";

import React, { useState, useEffect, useRef } from "react";
import { MessageInput } from "./MessageInput";
import { useAuth } from "@/context/AuthContext";
import { useChatStream } from "@/hooks/useChatStream";
import { api } from "@/lib/api";
import { Message } from "@/lib/types";
import { Bot, User, Sparkles, AlertCircle, Code } from "lucide-react";

interface ChatAreaProps {
  conversationId: string | null;
  selectedTemplateContent?: string;
}

export const ChatArea: React.FC<ChatAreaProps> = ({
  conversationId,
  selectedTemplateContent,
}) => {
  const { accessToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { isStreaming, streamError, streamMessage, cancelStream } = useChatStream();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Load conversation messages on conversationId change
  useEffect(() => {
    if (!conversationId || !accessToken) {
      setMessages([]);
      return;
    }

    const fetchMessages = async () => {
      setIsLoadingMessages(true);
      setLoadError(null);
      try {
        const res = await api.getMessages(accessToken, conversationId, 100);
        setMessages(res.items);
      } catch (err: any) {
        setLoadError(err.message || "Failed to load conversation history");
      } finally {
        setIsLoadingMessages(false);
      }
    };

    fetchMessages();
  }, [conversationId, accessToken]);

  // Auto-scroll when messages change or streaming token arrives
  useEffect(() => {
    scrollToBottom();
  }, [messages, isStreaming]);

  const handleSendMessage = async (text: string) => {
    if (!conversationId || !accessToken || isStreaming) return;

    // Create optimistic user message & placeholder assistant message
    const tempUserMsgId = `user-temp-${Date.now()}`;
    const tempAssistantMsgId = `asst-temp-${Date.now()}`;

    const userMessage: Message = {
      id: tempUserMsgId,
      conversation_id: conversationId,
      role: "user",
      content: text,
      created_at: new Date().toISOString(),
    };

    const assistantMessage: Message = {
      id: tempAssistantMsgId,
      conversation_id: conversationId,
      role: "assistant",
      content: "",
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage, assistantMessage]);

    let activeAssistantId = tempAssistantMsgId;

    await streamMessage(
      conversationId,
      text,
      accessToken,
      (startData) => {
        activeAssistantId = startData.assistant_message_id;
        setMessages((prev) =>
          prev.map((msg) => {
            if (msg.id === tempUserMsgId) {
              return { ...msg, id: startData.user_message_id };
            }
            if (msg.id === tempAssistantMsgId) {
              return { ...msg, id: startData.assistant_message_id };
            }
            return msg;
          })
        );
      },
      (token) => {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === activeAssistantId
              ? { ...msg, content: msg.content + token }
              : msg
          )
        );
      },
      (metadata) => {
        if (metadata.structured_output) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === activeAssistantId
                ? { ...msg, structured_output: metadata.structured_output }
                : msg
            )
          );
        }
      },
      (_doneData) => {
        // Generation finished successfully
      }
    );
  };

  if (!conversationId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center bg-slate-950 text-slate-400 p-8 text-center">
        <div className="w-16 h-16 rounded-2xl bg-indigo-600/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-4">
          <Sparkles size={32} />
        </div>
        <h3 className="text-lg font-semibold text-slate-200 mb-2">No Active Conversation</h3>
        <p className="text-sm text-slate-500 max-w-sm">
          Select an existing conversation from the sidebar or click "New Chat" to begin.
        </p>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-screen bg-slate-950 overflow-hidden">
      {/* Header */}
      <header className="px-6 py-4 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Sparkles className="text-indigo-400" size={20} />
          <h2 className="font-medium text-slate-200 text-sm">Conversation Workspace</h2>
        </div>
        <div className="text-xs text-slate-400 bg-slate-900 border border-slate-800 px-3 py-1 rounded-full flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          <span>SSE Streaming Enabled</span>
        </div>
      </header>

      {/* Stream / Load Error Alert */}
      {(streamError || loadError) && (
        <div className="bg-red-500/10 border-b border-red-500/20 px-6 py-2.5 flex items-center justify-between text-red-400 text-xs">
          <div className="flex items-center gap-2">
            <AlertCircle size={15} />
            <span>{streamError || loadError}</span>
          </div>
        </div>
      )}

      {/* Messages Feed */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {isLoadingMessages ? (
            <div className="text-center text-xs text-slate-500 py-8">Loading message history...</div>
          ) : messages.length === 0 ? (
            <div className="text-center text-xs text-slate-600 py-12 italic">
              No messages in this conversation yet. Send a prompt to get started!
            </div>
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex gap-4 ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                {msg.role === "assistant" && (
                  <div className="w-8 h-8 rounded-lg bg-indigo-600/20 border border-indigo-500/30 flex items-center justify-center text-indigo-400 shrink-0 mt-1">
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
                  <p className="whitespace-pre-wrap">{msg.content || (isStreaming && msg.role === "assistant" ? "..." : "")}</p>

                  {/* Render Structured Output if Present */}
                  {msg.structured_output && (
                    <div className="mt-3 pt-3 border-t border-slate-800">
                      <div className="flex items-center gap-1.5 text-xs text-indigo-400 font-mono mb-2">
                        <Code size={14} />
                        <span>Structured Output</span>
                      </div>
                      <pre className="bg-slate-950 p-3 rounded-xl text-xs font-mono text-emerald-400 overflow-x-auto border border-slate-800">
                        {JSON.stringify(msg.structured_output, null, 2)}
                      </pre>
                    </div>
                  )}

                  <span className="block text-[10px] opacity-60 mt-1.5 text-right">
                    {msg.created_at ? new Date(msg.created_at).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                  </span>
                </div>
                {msg.role === "user" && (
                  <div className="w-8 h-8 rounded-lg bg-slate-800 flex items-center justify-center text-slate-300 shrink-0 mt-1">
                    <User size={18} />
                  </div>
                )}
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Component */}
      <MessageInput
        onSendMessage={handleSendMessage}
        isStreaming={isStreaming}
        onCancelStream={cancelStream}
        initialValue={selectedTemplateContent}
        disabled={isLoadingMessages}
      />
    </div>
  );
};
