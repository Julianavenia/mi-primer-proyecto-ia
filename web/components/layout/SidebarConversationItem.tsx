interface SidebarConversationItemProps {
  title: string;
  active: boolean;
  onClick: () => void;
}

export function SidebarConversationItem({ title, active, onClick }: SidebarConversationItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? "true" : undefined}
      className={`w-full truncate rounded-sm px-3 py-2 text-left text-sm transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent ${
        active
          ? "bg-muted font-medium text-foreground"
          : "text-muted-foreground hover:bg-muted hover:text-foreground"
      }`}
    >
      {title}
    </button>
  );
}
