"use client";

import { useCallback, useReducer } from "react";
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

interface State {
  conversations: Conversation[];
  activeId: string;
}

type Action =
  | { type: "create" }
  | { type: "select"; id: string }
  | { type: "delete"; id: string }
  | { type: "update"; id: string; updater: (conversation: Conversation) => Conversation };

function reducer(state: State, action: Action): State {
  switch (action.type) {
    case "create": {
      const conversation = createEmptyConversation();
      return { conversations: [conversation, ...state.conversations], activeId: conversation.id };
    }
    case "select":
      return { ...state, activeId: action.id };
    case "delete": {
      const remaining = state.conversations.filter((c) => c.id !== action.id);
      const conversations = remaining.length > 0 ? remaining : [createEmptyConversation()];
      const activeId = action.id === state.activeId ? conversations[0].id : state.activeId;
      return { conversations, activeId };
    }
    case "update":
      return {
        ...state,
        conversations: state.conversations.map((c) =>
          c.id === action.id ? action.updater(c) : c,
        ),
      };
    default:
      return state;
  }
}

function initState(): State {
  const conversation = createEmptyConversation();
  return { conversations: [conversation], activeId: conversation.id };
}

interface UseConversationsResult {
  conversations: Conversation[];
  activeConversation: Conversation;
  createConversation: () => void;
  selectConversation: (id: string) => void;
  deleteConversation: (id: string) => void;
  updateActiveConversation: (updater: (conversation: Conversation) => Conversation) => void;
}

/**
 * Lista de conversaciones de la sesión del navegador. Sin persistencia (se
 * pierde al recargar) -- no hay base de datos todavía, es deliberado.
 * `conversations` y `activeId` se coordinan en un solo reducer (en vez de dos
 * useState separados) para que borrar la conversación activa y elegir la
 * siguiente ocurran de forma atómica, sin estados intermedios inconsistentes.
 */
export function useConversations(): UseConversationsResult {
  const [state, dispatch] = useReducer(reducer, undefined, initState);

  const createConversation = useCallback(() => dispatch({ type: "create" }), []);
  const selectConversation = useCallback((id: string) => dispatch({ type: "select", id }), []);
  const deleteConversation = useCallback((id: string) => dispatch({ type: "delete", id }), []);
  const updateActiveConversation = useCallback(
    (updater: (conversation: Conversation) => Conversation) =>
      dispatch({ type: "update", id: state.activeId, updater }),
    [state.activeId],
  );

  const activeConversation =
    state.conversations.find((c) => c.id === state.activeId) ?? state.conversations[0];

  return {
    conversations: state.conversations,
    activeConversation,
    createConversation,
    selectConversation,
    deleteConversation,
    updateActiveConversation,
  };
}
