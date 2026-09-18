interface BotAvatarProps {
  size?: "sm" | "lg";
}

const sizeClasses: Record<NonNullable<BotAvatarProps["size"]>, string> = {
  sm: "h-7 w-7",
  lg: "h-12 w-12",
};

const iconSizeClasses: Record<NonNullable<BotAvatarProps["size"]>, string> = {
  sm: "h-4 w-4",
  lg: "h-6 w-6",
};

/** Avatar del agente: reutilizado en burbujas de mensaje, indicador de escritura y estado vacío. */
export function BotAvatar({ size = "sm" }: BotAvatarProps) {
  return (
    <div
      className={`flex shrink-0 items-center justify-center rounded-full bg-accent text-accent-foreground ${sizeClasses[size]}`}
    >
      <svg
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        className={iconSizeClasses[size]}
        aria-hidden="true"
      >
        <rect x="4" y="8" width="16" height="12" rx="2" />
        <path strokeLinecap="round" d="M12 8V4" />
        <circle cx="9" cy="14" r="1" fill="currentColor" stroke="none" />
        <circle cx="15" cy="14" r="1" fill="currentColor" stroke="none" />
      </svg>
    </div>
  );
}
