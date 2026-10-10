"use client";

import React, { useState, useEffect, useRef } from "react";
import { Send, Square } from "lucide-react";

interface MessageInputProps {
  onSendMessage: (text: string) => void;
  isStreaming?: boolean;
  onCancelStream?: () => void;
  disabled?: boolean;
  initialValue?: string;
}

export const MessageInput: React.FC<MessageInputProps> = ({
  onSendMessage,
  isStreaming,
  onCancelStream,
  disabled,
  initialValue = "",
}) => {
  const [input, setInput] = useState(initialValue);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (initialValue) {
      setInput(initialValue);
    }
  }, [initialValue]);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 160)}px`;
    }
  }, [input]);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!input.trim() || disabled || isStreaming) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="p-4 border-t border-slate-800 bg-slate-900">
      <div className="max-w-4xl mx-auto flex items-end gap-2 bg-slate-950 border border-slate-800 rounded-xl p-2 px-4 focus-within:border-indigo-500 transition-colors">
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question or enter a prompt... (Shift+Enter for newline)"
          disabled={disabled || isStreaming}
          rows={1}
          className="flex-1 bg-transparent text-slate-100 placeholder-slate-500 text-sm focus:outline-none resize-none py-1.5 max-h-40 overflow-y-auto font-sans"
        />
        {isStreaming ? (
          <button
            type="button"
            onClick={onCancelStream}
            className="p-2 rounded-lg bg-red-600/80 hover:bg-red-600 text-white transition-colors flex items-center justify-center"
            title="Stop generation"
          >
            <Square size={16} className="fill-current" />
          </button>
        ) : (
          <button
            type="button"
            onClick={() => handleSubmit()}
            disabled={!input.trim() || disabled}
            className="p-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white transition-opacity"
            title="Send message"
          >
            <Send size={16} />
          </button>
        )}
      </div>
    </div>
  );
};
