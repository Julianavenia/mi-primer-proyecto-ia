import { IconButton } from "@/components/ui/IconButton";
import { StatusPill } from "@/components/ui/StatusPill";
import type { BackendStatus } from "@/hooks/useBackendStatus";

interface HeaderProps {
  title: string;
  backendStatus: BackendStatus;
  onOpenMenu: () => void;
}

export function Header({ title, backendStatus, onOpenMenu }: HeaderProps) {
  return (
    <header className="flex items-center justify-between gap-3 border-b border-border px-4 py-3 sm:px-6">
      <div className="flex min-w-0 items-center gap-2">
        <IconButton label="Abrir menú" onClick={onOpenMenu} className="lg:hidden">
          <MenuIcon className="h-5 w-5" />
        </IconButton>
        <h1 className="truncate text-sm font-medium text-foreground">{title}</h1>
      </div>
      <div className="lg:hidden">
        <StatusPill status={backendStatus} />
      </div>
    </header>
  );
}

function MenuIcon({ className = "" }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <path strokeLinecap="round" d="M4 6h16M4 12h16M4 18h16" />
    </svg>
  );
}
