"use client";

import { useCallback, useState } from "react";
import type { ErrorVariant } from "@/components/chat/ErrorBanner";
import { ApiError, postChat } from "@/lib/api";
import type { ChatMessage, Conversation } from "@/lib/types";
import { deriveTitle } from "./useConversations";

export interface ChatError {
  message: string;
  variant: ErrorVariant;
}

interface UseChatResult {
  isLoading: boolean;
  error: ChatError | null;
  sendMessage: (text: string) => Promise<void>;
}

function toChatError(err: unknown): ChatError {
  if (!(err instanceof ApiError)) {
    return { message: "Ocurrió un error inesperado.", variant: "unknown" };
  }
  if (err.status === undefined) return { message: err.message, variant: "offline" };
  if (err.status === 422) return { message: err.message, variant: "validation" };
  if (err.status === 502) return { message: err.message, variant: "agent" };
  return { message: err.message, variant: "unknown" };
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
  const [error, setError] = useState<ChatError | null>(null);

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
        setError(toChatError(err));
      } finally {
        setIsLoading(false);
      }
    },
    [conversation.conversationId, isLoading, onUpdate],
  );

  return { isLoading, error, sendMessage };
}
