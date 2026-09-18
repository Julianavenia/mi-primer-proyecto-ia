import { Button } from "@/components/ui/Button";
import { IconButton } from "@/components/ui/IconButton";
import { StatusPill } from "@/components/ui/StatusPill";
import type { BackendStatus } from "@/hooks/useBackendStatus";
import type { Conversation } from "@/lib/types";
import { SidebarConversationItem } from "./SidebarConversationItem";

interface SidebarProps {
  conversations: Conversation[];
  activeConversationId: string;
  onSelectConversation: (id: string) => void;
  onCreateConversation: () => void;
  onDeleteConversation: (id: string) => void;
  backendStatus: BackendStatus;
  /** Presente solo cuando el sidebar se muestra como drawer móvil. */
  onClose?: () => void;
}

export function Sidebar({
  conversations,
  activeConversationId,
  onSelectConversation,
  onCreateConversation,
  onDeleteConversation,
  backendStatus,
  onClose,
}: SidebarProps) {
  return (
    <div className="flex h-full flex-col">
      <div className="flex items-center justify-between gap-2 px-4 py-4">
        <div>
          <p className="text-base font-semibold text-foreground">mi-primer-proyecto-ia</p>
          <p className="text-xs text-muted-foreground">Agente con tool use</p>
        </div>
        {onClose && (
          <IconButton label="Cerrar menú" onClick={onClose} className="lg:hidden">
            <CloseIcon className="h-5 w-5" />
          </IconButton>
        )}
      </div>

      <div className="px-3">
        <Button variant="outline" onClick={onCreateConversation} className="w-full justify-start">
          <PlusIcon className="h-4 w-4" />
          Nueva conversación
        </Button>
      </div>

      <nav aria-label="Conversaciones" className="mt-4 flex-1 overflow-y-auto px-3">
        <p className="px-3 pb-2 text-[11px] font-medium uppercase tracking-wide text-muted-foreground">
          Conversaciones
        </p>
        {conversations.length === 0 ? (
          <p className="px-3 py-2 text-sm text-muted-foreground">Aún no tienes conversaciones.</p>
        ) : (
          <ul className="flex flex-col gap-0.5">
            {conversations.map((conversation) => (
              <li key={conversation.id}>
                <SidebarConversationItem
                  title={conversation.title}
                  active={conversation.id === activeConversationId}
                  onSelect={() => onSelectConversation(conversation.id)}
                  onDelete={() => onDeleteConversation(conversation.id)}
                />
              </li>
            ))}
          </ul>
        )}
      </nav>

      <div className="border-t border-border px-4 py-3">
        <StatusPill status={backendStatus} />
      </div>
    </div>
  );
}

function PlusIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path strokeLinecap="round" d="M12 5v14M5 12h14" />
    </svg>
  );
}

function CloseIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path strokeLinecap="round" d="M6 6l12 12M18 6L6 18" />
    </svg>
  );
}
