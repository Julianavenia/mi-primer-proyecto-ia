import { getApiUrl } from "./env";
import type {
  ApiErrorBody,
  ChatRequestBody,
  ChatResponseBody,
  HealthResponseBody,
} from "./types";

export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseErrorDetail(response: Response): Promise<string | undefined> {
  try {
    const body = (await response.json()) as ApiErrorBody;
    return body.detail;
  } catch {
    return undefined;
  }
}

export async function postChat(body: ChatRequestBody): Promise<ChatResponseBody> {
  let response: Response;
  try {
    response = await fetch(`${getApiUrl()}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "No se pudo conectar con el backend. Verifica que el servidor FastAPI esté corriendo.",
    );
  }

  if (!response.ok) {
    const detail = await parseErrorDetail(response);
    throw new ApiError(
      detail ?? `El backend respondió con un error (${response.status}).`,
      response.status,
    );
  }

  return (await response.json()) as ChatResponseBody;
}

export async function getHealth(): Promise<HealthResponseBody> {
  let response: Response;
  try {
    response = await fetch(`${getApiUrl()}/health`);
  } catch {
    throw new ApiError("No se pudo conectar con el backend.");
  }

  if (!response.ok) {
    throw new ApiError(
      `No se pudo verificar el estado del backend (${response.status}).`,
      response.status,
    );
  }

  return (await response.json()) as HealthResponseBody;
}
