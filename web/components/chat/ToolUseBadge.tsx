import type { ToolCallInfo } from "@/lib/types";

function formatResult(toolCall: ToolCallInfo): string {
  if (toolCall.is_error) return toolCall.result;
  try {
    const parsed: unknown = JSON.parse(toolCall.result);
    if (parsed && typeof parsed === "object" && "result" in parsed) {
      return String((parsed as { result: unknown }).result);
    }
  } catch {
    // no era JSON estructurado -- se muestra tal cual
  }
  return toolCall.result;
}

export function ToolUseBadge({ toolCall }: { toolCall: ToolCallInfo }) {
  return (
    <div
      className={`flex max-w-full items-center gap-2 rounded-md border px-3 py-1.5 font-mono text-xs ${
        toolCall.is_error
          ? "border-danger-subtle bg-danger-subtle text-danger"
          : "border-border bg-muted text-muted-foreground"
      }`}
    >
      <ToolIcon className="h-3.5 w-3.5 shrink-0" />
      <span className="font-medium text-foreground">{toolCall.name}</span>
      <span aria-hidden="true">→</span>
      <span className="truncate">{formatResult(toolCall)}</span>
    </div>
  );
}

function ToolIcon({ className = "" }: { className?: string }) {
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
        d="M14.7 6.3a1 1 0 000 1.4l1.6 1.6a1 1 0 001.4 0l3.77-3.77a6 6 0 01-7.94 7.94l-6.91 6.91a2.12 2.12 0 11-3-3l6.91-6.91a6 6 0 017.94-7.94z"
      />
    </svg>
  );
}
