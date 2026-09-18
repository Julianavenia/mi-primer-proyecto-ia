"use client";

import { useState } from "react";
import { ChatWindow } from "@/components/chat/ChatWindow";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { useConversations } from "@/hooks/useConversations";
import { Header } from "./Header";
import { MobileDrawer } from "./MobileDrawer";
import { Sidebar } from "./Sidebar";

/** Layout raíz de la app: sidebar + header + área de chat. Dueño del estado
 * de conversaciones (vía useConversations) y del estado del backend. */
export function AppShell() {
  const backendStatus = useBackendStatus();
  const {
    conversations,
    activeConversation,
    createConversation,
    selectConversation,
    deleteConversation,
    updateActiveConversation,
  } = useConversations();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const handleSelectConversation = (id: string) => {
    selectConversation(id);
    setMobileMenuOpen(false);
  };

  const handleCreateConversation = () => {
    createConversation();
    setMobileMenuOpen(false);
  };

  return (
    <div className="flex h-dvh w-full bg-background">
      <aside className="hidden w-[280px] shrink-0 border-r border-border lg:block">
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversation.id}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
          onDeleteConversation={deleteConversation}
          backendStatus={backendStatus}
        />
      </aside>

      <MobileDrawer
        open={mobileMenuOpen}
        onClose={() => setMobileMenuOpen(false)}
        label="Conversaciones"
      >
        <Sidebar
          conversations={conversations}
          activeConversationId={activeConversation.id}
          onSelectConversation={handleSelectConversation}
          onCreateConversation={handleCreateConversation}
          onDeleteConversation={deleteConversation}
          backendStatus={backendStatus}
          onClose={() => setMobileMenuOpen(false)}
        />
      </MobileDrawer>

      <div className="flex min-w-0 flex-1 flex-col">
        <Header
          title={activeConversation.title}
          backendStatus={backendStatus}
          onOpenMenu={() => setMobileMenuOpen(true)}
        />
        <ChatWindow
          conversation={activeConversation}
          onUpdateConversation={updateActiveConversation}
          backendOffline={backendStatus.state === "offline"}
        />
      </div>
    </div>
  );
}
