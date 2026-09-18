"use client";

import { useState } from "react";
import { useChat } from "@/hooks/useChat";
import type { Conversation } from "@/lib/types";
import { ErrorBanner } from "./ErrorBanner";
import { MessageInput } from "./MessageInput";
import { MessageList } from "./MessageList";

interface ChatWindowProps {
  conversation: Conversation;
  onUpdateConversation: (updater: (conversation: Conversation) => Conversation) => void;
  backendOffline: boolean;
}

/** Orquesta UNA conversación: mensajes, composer y errores. La lista de
 * conversaciones y el estado del backend viven un nivel más arriba (AppShell). */
export function ChatWindow({ conversation, onUpdateConversation, backendOffline }: ChatWindowProps) {
  const { isLoading, error, sendMessage } = useChat(conversation, onUpdateConversation);
  const [composerValue, setComposerValue] = useState("");

  const banner =
    error ??
    (backendOffline
      ? {
          message: "No se pudo conectar con el backend. Verifica que el servidor FastAPI esté corriendo.",
          variant: "offline" as const,
        }
      : null);

  return (
    <div className="flex flex-1 flex-col overflow-hidden">
      <MessageList
        messages={conversation.messages}
        isLoading={isLoading}
        onSelectSuggestion={setComposerValue}
      />

      {banner && (
        <div className="px-4 pb-2 sm:px-6">
          <ErrorBanner message={banner.message} variant={banner.variant} />
        </div>
      )}

      <MessageInput
        value={composerValue}
        onChange={setComposerValue}
        onSend={sendMessage}
        disabled={isLoading}
      />
    </div>
  );
}
