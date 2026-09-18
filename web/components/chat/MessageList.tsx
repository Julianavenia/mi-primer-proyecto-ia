"use client";

import { useEffect, useRef } from "react";
import type { ChatMessage } from "@/lib/types";
import { EmptyState } from "./EmptyState";
import { MessageBubble } from "./MessageBubble";
import { TypingIndicator } from "./TypingIndicator";

interface MessageListProps {
  messages: ChatMessage[];
  isLoading: boolean;
  onSelectSuggestion: (text: string) => void;
}

export function MessageList({ messages, isLoading, onSelectSuggestion }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  if (messages.length === 0 && !isLoading) {
    return <EmptyState onSelectSuggestion={onSelectSuggestion} />;
  }

  return (
    <div
      className="flex flex-1 flex-col gap-4 overflow-y-auto px-4 py-6 sm:px-6"
      role="log"
      aria-live="polite"
      aria-label="Historial de la conversación"
    >
      {messages.map((message) => (
        <MessageBubble key={message.id} message={message} />
      ))}
      {isLoading && <TypingIndicator />}
      <div ref={bottomRef} />
    </div>
  );
}
