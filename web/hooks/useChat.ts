"use client";

import { useCallback, useState } from "react";
import { ApiError, postChat } from "@/lib/api";
import type { ChatMessage, Conversation } from "@/lib/types";
import { deriveTitle } from "./useConversations";

interface UseChatResult {
  isLoading: boolean;
  error: string | null;
  sendMessage: (text: string) => Promise<void>;
}

/**
 * Lógica de envío de mensajes para UNA conversación. No sabe nada de la
 * lista de conversaciones ni del sidebar -- solo lee/actualiza la que se le
 * pasa, vía `onUpdate` (normalmente `updateActiveConversation` de
 * `useConversations`). Así se mantiene reutilizable y testeable aislado.
 */
export function useChat(
  conversation: Conversation,
  onUpdate: (updater: (conversation: Conversation) => Conversation) => void,
): UseChatResult {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || isLoading) return;

      setError(null);
      const userMessage: ChatMessage = { id: crypto.randomUUID(), role: "user", content: trimmed };
      onUpdate((current) => ({
        ...current,
        title: current.messages.length === 0 ? deriveTitle(trimmed) : current.title,
        messages: [...current.messages, userMessage],
      }));
      setIsLoading(true);

      try {
        const response = await postChat({
          message: trimmed,
          conversation_id: conversation.conversationId,
        });
        const assistantMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: "assistant",
          content: response.reply,
          toolCalls: response.tool_calls,
        };
        onUpdate((current) => ({
          ...current,
          conversationId: response.conversation_id,
          messages: [...current.messages, assistantMessage],
        }));
      } catch (err) {
        setError(err instanceof ApiError ? err.message : "Ocurrió un error inesperado.");
      } finally {
        setIsLoading(false);
      }
    },
    [conversation.conversationId, isLoading, onUpdate],
  );

  return { isLoading, error, sendMessage };
}
