import type { TokenResponse, User } from "./types";

const ACCESS_TOKEN_KEY = "evasym.accessToken";
const REFRESH_TOKEN_KEY = "evasym.refreshToken";
const USER_KEY = "evasym.user";

export type StoredSession = {
  accessToken: string;
  refreshToken: string;
  user: User;
};

export function readStoredSession(): StoredSession | null {
  const accessToken = sessionStorage.getItem(ACCESS_TOKEN_KEY);
  const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY);
  const userRaw = sessionStorage.getItem(USER_KEY);

  if (!accessToken || !refreshToken || !userRaw) {
    return null;
  }

  try {
    return {
      accessToken,
      refreshToken,
      user: JSON.parse(userRaw) as User,
    };
  } catch {
    clearStoredSession();
    return null;
  }
}

export function writeStoredSession(response: TokenResponse): StoredSession {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, response.access_token);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, response.refresh_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(response.user));

  return {
    accessToken: response.access_token,
    refreshToken: response.refresh_token,
    user: response.user,
  };
}

export function clearStoredSession(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}
