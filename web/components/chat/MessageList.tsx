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
      className="flex flex-1 flex-col overflow-y-auto px-4 py-6 sm:px-6"
      role="log"
      aria-live="polite"
      aria-label="Historial de la conversación"
    >
      {/* Columna de lectura con ancho máximo: en monitores anchos, el área de
          chat no debe estirar las líneas de texto más allá de lo legible. */}
      <div className="mx-auto flex w-full max-w-3xl flex-col gap-4">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
