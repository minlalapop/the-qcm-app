type RequestOptions = RequestInit & {
  token?: string | null;
};

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(message: string, status: number, details: unknown = null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

export async function apiRequest<T>(baseUrl: string, path: string, options: RequestOptions = {}): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Accept", "application/json");

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  if (options.token) {
    headers.set("Authorization", `Bearer ${options.token}`);
  }

  const response = await fetch(`${baseUrl}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get("content-type") ?? "";
  const payload = contentType.includes("application/json") ? await response.json() : await response.text();

  if (!response.ok) {
    const message = formatApiErrorMessage(payload, response.status);
    throw new ApiError(message, response.status, payload);
  }

  return payload as T;
}

function formatApiErrorMessage(payload: unknown, status: number): string {
  if (typeof payload === "string" && payload.trim()) {
    return payload;
  }

  if (payload && typeof payload === "object" && "detail" in payload) {
    return formatDetail((payload as { detail: unknown }).detail);
  }

  return `Request failed with status ${status}`;
}

function formatDetail(detail: unknown): string {
  if (typeof detail === "string") {
    return formatErrorString(detail);
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (item && typeof item === "object" && "msg" in item) {
          const location = "loc" in item && Array.isArray(item.loc) ? item.loc.join(".") : null;
          return location ? `${location}: ${String(item.msg)}` : String(item.msg);
        }
        return formatDetail(item);
      })
      .filter(Boolean)
      .join(" ");
  }

  if (detail && typeof detail === "object" && "message" in detail) {
    return String((detail as { message: unknown }).message);
  }

  try {
    return formatErrorString(JSON.stringify(detail));
  } catch {
    return "Unexpected API error";
  }
}

function formatErrorString(message: string): string {
  if (message.includes("Insufficient credits")) {
    return "OpenRouter refuse la generation: le compte lie a cette cle API n'a pas de credits disponibles. Ajoute des credits sur OpenRouter ou utilise une cle d'un compte credite.";
  }

  if (message.includes("User not found") && message.includes("OpenRouter")) {
    return "OpenRouter refuse la generation: la cle API ne correspond a aucun compte OpenRouter valide. Verifie OPENROUTER_API_KEY dans .env.";
  }

  const openRouterMessage = extractJsonMessage(message);
  if (openRouterMessage) {
    return openRouterMessage;
  }

  return message;
}

function extractJsonMessage(message: string): string | null {
  const start = message.indexOf("{");
  if (start === -1) return null;

  try {
    const parsed = JSON.parse(message.slice(start));
    const detail = parsed?.detail;
    if (typeof detail === "string" && detail !== message) {
      return formatErrorString(detail);
    }
    const nestedMessage = parsed?.error?.message ?? parsed?.message;
    return typeof nestedMessage === "string" ? nestedMessage : null;
  } catch {
    return null;
  }
}
