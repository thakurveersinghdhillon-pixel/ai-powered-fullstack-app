"use client";

import { useState, useRef, useCallback } from "react";
import { Message, SSEStartPayload, SSETokenPayload, SSEMetadataPayload, SSEDonePayload, SSEErrorPayload } from "@/lib/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export function useChatStream() {
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamError, setStreamError] = useState<string | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  const cancelStream = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
      setIsStreaming(false);
    }
  }, []);

  const streamMessage = useCallback(
    async (
      conversationId: string,
      content: string,
      accessToken: string,
      onStart: (data: SSEStartPayload) => void,
      onToken: (token: string) => void,
      onMetadata: (data: SSEMetadataPayload) => void,
      onDone: (data: SSEDonePayload) => void,
      systemPrompt?: string
    ) => {
      setIsStreaming(true);
      setStreamError(null);

      const abortController = new AbortController();
      abortControllerRef.current = abortController;

      try {
        const response = await fetch(
          `${API_BASE_URL}/conversations/${conversationId}/messages/stream`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify({
              content,
              system_prompt: systemPrompt || null,
            }),
            signal: abortController.signal,
          }
        );

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          const errorMsg = errorData.detail || `HTTP Error ${response.status}`;
          setStreamError(errorMsg);
          setIsStreaming(false);
          return;
        }

        if (!response.body) {
          setStreamError("Response body is missing");
          setIsStreaming(false);
          return;
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder("utf-8");
        let buffer = "";

        while (true) {
          const { value, done } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const parts = buffer.split("\n\n");
          buffer = parts.pop() || ""; // Keep incomplete chunk in buffer

          for (const part of parts) {
            if (!part.trim()) continue;

            const lines = part.split("\n");
            let eventType = "message";
            let eventData = "";

            for (const line of lines) {
              if (line.startsWith("event: ")) {
                eventType = line.substring(7).trim();
              } else if (line.startsWith("data: ")) {
                eventData = line.substring(6).trim();
              }
            }

            if (!eventData) continue;

            try {
              const parsed = JSON.parse(eventData);

              if (eventType === "start") {
                onStart(parsed as SSEStartPayload);
              } else if (eventType === "token") {
                onToken((parsed as SSETokenPayload).content);
              } else if (eventType === "metadata") {
                onMetadata(parsed as SSEMetadataPayload);
              } else if (eventType === "done") {
                onDone(parsed as SSEDonePayload);
              } else if (eventType === "error") {
                const err = (parsed as SSEErrorPayload).error || "Stream error occurred";
                setStreamError(err);
              }
            } catch (e) {
              // Ignore malformed JSON line chunks
            }
          }
        }
      } catch (err: any) {
        if (err.name !== "AbortError") {
          setStreamError(err.message || "Failed to stream message");
        }
      } finally {
        setIsStreaming(false);
        abortControllerRef.current = null;
      }
    },
    []
  );

  return {
    isStreaming,
    streamError,
    streamMessage,
    cancelStream,
  };
}
