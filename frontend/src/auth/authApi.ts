import { apiRequest } from "../api/http";
import { env } from "../env";
import type { LoginPayload, RegisterPayload, TokenResponse, User } from "./types";

export function login(payload: LoginPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(env.authBaseUrl, "/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
    timeoutMs: 12000,
  });
}

export function register(payload: RegisterPayload): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(env.authBaseUrl, "/auth/register", {
    method: "POST",
    body: JSON.stringify({ role: "teacher", ...payload }),
    timeoutMs: 12000,
  });
}

export function refresh(refreshToken: string): Promise<TokenResponse> {
  return apiRequest<TokenResponse>(env.authBaseUrl, "/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
    timeoutMs: 8000,
  });
}

export function logout(refreshToken: string): Promise<{ message: string }> {
  return apiRequest<{ message: string }>(env.authBaseUrl, "/auth/logout", {
    method: "POST",
    body: JSON.stringify({ refresh_token: refreshToken }),
    timeoutMs: 8000,
  });
}

export function me(accessToken: string): Promise<User> {
  return apiRequest<User>(env.authBaseUrl, "/auth/me", {
    token: accessToken,
    timeoutMs: 8000,
  });
}
