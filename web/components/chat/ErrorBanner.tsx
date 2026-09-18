export type ErrorVariant = "offline" | "validation" | "agent" | "unknown";

interface ErrorBannerProps {
  message: string;
  variant?: ErrorVariant;
}

const VARIANT_STYLES: Record<ErrorVariant, string> = {
  offline: "border-danger-subtle bg-danger-subtle text-danger",
  agent: "border-danger-subtle bg-danger-subtle text-danger",
  unknown: "border-danger-subtle bg-danger-subtle text-danger",
  // Los errores de validación son recuperables con solo corregir el mensaje --
  // tono de advertencia, no de fallo grave. Único uso real de --warning hoy.
  validation: "border-warning-subtle bg-warning-subtle text-warning",
};

export function ErrorBanner({ message, variant = "unknown" }: ErrorBannerProps) {
  return (
    <div
      role="alert"
      className={`animate-fade-in flex items-start gap-2 rounded-md border px-4 py-3 text-sm ${VARIANT_STYLES[variant]}`}
    >
      <ErrorIcon variant={variant} className="mt-0.5 h-4 w-4 shrink-0" />
      <span>{message}</span>
    </div>
  );
}

function ErrorIcon({ variant, className = "" }: { variant: ErrorVariant; className?: string }) {
  if (variant === "offline") {
    return (
      <svg
        className={className}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        aria-hidden="true"
      >
        <path strokeLinecap="round" strokeLinejoin="round" d="M2 2l20 20" />
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M8.5 16.5a5 5 0 015.7-1.2M5 13a9 9 0 012.8-2M12 20h.01M19 13a9 9 0 00-1.3-1.7M15.5 9.5A9 9 0 0012 9c-.6 0-1.1.05-1.7.15"
        />
      </svg>
    );
  }

  if (variant === "validation") {
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
          d="M12 9v4M12 17h.01M10.3 3.9L2.5 17a1.5 1.5 0 001.3 2.2h16.4a1.5 1.5 0 001.3-2.2L13.7 3.9a1.5 1.5 0 00-2.6 0z"
        />
      </svg>
    );
  }

  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      aria-hidden="true"
    >
      <circle cx="12" cy="12" r="9" />
      <path strokeLinecap="round" d="M12 8v5" />
      <circle cx="12" cy="16" r="0.5" fill="currentColor" />
    </svg>
  );
}
