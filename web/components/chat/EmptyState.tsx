import { BotAvatar } from "@/components/ui/BotAvatar";
import { SuggestionChip } from "./SuggestionChip";

const SUGGESTIONS = ["¿Cuánto es 12 * 7?", "Calcula (8 + 4) * 3", "¿Qué puedes hacer?"];

interface EmptyStateProps {
  onSelectSuggestion: (text: string) => void;
}

export function EmptyState({ onSelectSuggestion }: EmptyStateProps) {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
      <BotAvatar size="lg" />
      <div className="space-y-1.5">
        <h2 className="text-base font-semibold text-foreground">Empieza una conversación</h2>
        <p className="max-w-sm text-sm text-muted-foreground">
          Este agente puede usar herramientas para resolver tareas. Prueba con un cálculo.
        </p>
      </div>
      <div className="grid w-full max-w-sm gap-2">
        {SUGGESTIONS.map((suggestion) => (
          <SuggestionChip
            key={suggestion}
            label={suggestion}
            onClick={() => onSelectSuggestion(suggestion)}
          />
        ))}
      </div>
    </div>
  );
}
