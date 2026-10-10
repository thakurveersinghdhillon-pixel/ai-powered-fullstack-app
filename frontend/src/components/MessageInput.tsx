"use client";

import React, { useState } from "react";
import { Send } from "lucide-react";

interface MessageInputProps {
  onSendMessage: (text: string) => void;
  disabled?: boolean;
}

export const MessageInput: React.FC<MessageInputProps> = ({ onSendMessage, disabled }) => {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSendMessage(input);
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 bg-slate-900">
      <div className="max-w-4xl mx-auto flex items-center gap-2 bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 focus-within:border-indigo-500 transition-colors">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question or enter a prompt... (Placeholder response mode)"
          disabled={disabled}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none"
        />
        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-opacity"
        >
          <Send size={16} />
        </button>
      </div>
    </form>
  );
};
