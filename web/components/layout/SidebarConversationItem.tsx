import { IconButton } from "@/components/ui/IconButton";

interface SidebarConversationItemProps {
  title: string;
  active: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

export function SidebarConversationItem({
  title,
  active,
  onSelect,
  onDelete,
}: SidebarConversationItemProps) {
  return (
    <div className={`flex items-center rounded-md ${active ? "bg-muted" : "hover:bg-muted"}`}>
      <button
        type="button"
        onClick={onSelect}
        aria-current={active ? "true" : undefined}
        className={`min-w-0 flex-1 truncate rounded-md px-3 py-2 text-left text-sm transition focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
          active ? "font-medium text-foreground" : "text-muted-foreground"
        }`}
      >
        {title}
      </button>
      <IconButton
        label={`Eliminar conversación "${title}"`}
        onClick={onDelete}
        className="mr-1 h-7 w-7 shrink-0 text-muted-foreground hover:bg-danger-subtle hover:text-danger"
      >
        <TrashIcon className="h-3.5 w-3.5" />
      </IconButton>
    </div>
  );
}

function TrashIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M4 7h16M9 7V5a1 1 0 011-1h4a1 1 0 011 1v2m-8 0h10l-1 13a2 2 0 01-2 2H8a2 2 0 01-2-2L5 7z"
      />
    </svg>
  );
}
