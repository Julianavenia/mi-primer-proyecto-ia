import type { BackendStatus } from "@/hooks/useBackendStatus";

export function StatusPill({ status }: { status: BackendStatus }) {
  if (status.state === "loading") {
    return (
      <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-muted px-2.5 py-1 text-xs font-medium text-muted-foreground">
        <span className="h-1.5 w-1.5 rounded-full bg-current opacity-60" />
        Conectando…
      </span>
    );
  }

  if (status.state === "offline") {
    return (
      <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-danger-subtle px-2.5 py-1 text-xs font-medium text-danger">
        <span className="h-1.5 w-1.5 rounded-full bg-current" />
        Backend desconectado
      </span>
    );
  }

  return (
    <span className="inline-flex shrink-0 items-center gap-1.5 rounded-full bg-success-subtle px-2.5 py-1 text-xs font-medium text-success">
      <span className="h-1.5 w-1.5 rounded-full bg-current" />
      {status.llmBackend === "fake" ? "Modo simulado" : `Backend: ${status.llmBackend}`}
    </span>
  );
}
