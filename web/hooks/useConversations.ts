"use client";

import { useCallback, useState } from "react";
import type { Conversation } from "@/lib/types";

const DEFAULT_TITLE = "Nueva conversación";
const MAX_TITLE_LENGTH = 40;

function createEmptyConversation(): Conversation {
  return {
    id: crypto.randomUUID(),
    conversationId: null,
    title: DEFAULT_TITLE,
    messages: [],
  };
}

export function deriveTitle(firstMessage: string): string {
  const trimmed = firstMessage.trim();
  if (trimmed.length <= MAX_TITLE_LENGTH) return trimmed;
  return `${trimmed.slice(0, MAX_TITLE_LENGTH).trimEnd()}…`;
}

interface UseConversationsResult {
  conversations: Conversation[];
  activeConversation: Conversation;
  createConversation: () => void;
  selectConversation: (id: string) => void;
  updateActiveConversation: (updater: (conversation: Conversation) => Conversation) => void;
}

/**
 * Lista de conversaciones de la sesión del navegador. Sin persistencia (se
 * pierde al recargar) -- no hay base de datos todavía, es deliberado.
 */
export function useConversations(): UseConversationsResult {
  const [conversations, setConversations] = useState<Conversation[]>(() => [
    createEmptyConversation(),
  ]);
  const [activeId, setActiveId] = useState(() => conversations[0].id);

  const createConversation = useCallback(() => {
    const conversation = createEmptyConversation();
    setConversations((prev) => [conversation, ...prev]);
    setActiveId(conversation.id);
  }, []);

  const selectConversation = useCallback((id: string) => {
    setActiveId(id);
  }, []);

  const updateActiveConversation = useCallback(
    (updater: (conversation: Conversation) => Conversation) => {
      setConversations((prev) =>
        prev.map((conversation) =>
          conversation.id === activeId ? updater(conversation) : conversation,
        ),
      );
    },
    [activeId],
  );

  const activeConversation =
    conversations.find((conversation) => conversation.id === activeId) ?? conversations[0];

  return {
    conversations,
    activeConversation,
    createConversation,
    selectConversation,
    updateActiveConversation,
  };
}
