interface SuggestionChipProps {
  label: string;
  onClick: () => void;
}

export function SuggestionChip({ label, onClick }: SuggestionChipProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded-sm border border-border bg-surface px-3 py-2 text-left text-sm text-foreground transition-colors hover:border-accent hover:bg-muted focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-accent"
    >
      {label}
    </button>
  );
}
