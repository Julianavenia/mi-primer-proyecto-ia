import { BotAvatar } from "@/components/ui/BotAvatar";
import type { ChatMessage } from "@/lib/types";
import { ToolUseBadge } from "./ToolUseBadge";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === "user";

  return (
    <div
      className={`animate-fade-in flex items-end gap-2 ${isUser ? "flex-row-reverse" : "flex-row"}`}
    >
      {!isUser && <BotAvatar />}
      <div className={`flex max-w-[75%] flex-col gap-1.5 ${isUser ? "items-end" : "items-start"}`}>
        {message.toolCalls && message.toolCalls.length > 0 && (
          <div className="flex w-full flex-col gap-1">
            {message.toolCalls.map((toolCall, index) => (
              <ToolUseBadge key={`${message.id}-tool-${index}`} toolCall={toolCall} />
            ))}
          </div>
        )}
        <div
          className={`whitespace-pre-wrap rounded-lg px-4 py-3 text-sm leading-relaxed ${
            isUser
              ? "rounded-br-sm bg-accent text-accent-foreground"
              : "rounded-bl-sm border border-border bg-surface text-surface-foreground"
          }`}
        >
          {message.content}
        </div>
      </div>
    </div>
  );
}
