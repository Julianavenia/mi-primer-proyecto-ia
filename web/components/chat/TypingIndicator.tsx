import { BotAvatar } from "@/components/ui/BotAvatar";

export function TypingIndicator() {
  return (
    <div
      className="flex items-end gap-2"
      aria-live="polite"
      aria-label="El agente está escribiendo"
    >
      <BotAvatar />
      <div className="flex items-center gap-1 rounded-lg rounded-bl-sm border border-border bg-surface px-4 py-3">
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.3s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.15s]" />
        <span className="h-1.5 w-1.5 animate-bounce rounded-full bg-muted-foreground" />
      </div>
    </div>
  );
}
