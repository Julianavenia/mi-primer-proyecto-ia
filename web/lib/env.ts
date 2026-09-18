const DEFAULT_API_URL = "http://localhost:8000";

/**
 * URL del backend FastAPI. Se lee una sola vez aquí -- el resto del código
 * nunca debe leer `process.env.NEXT_PUBLIC_API_URL` directamente.
 */
export function getApiUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? DEFAULT_API_URL;
}
