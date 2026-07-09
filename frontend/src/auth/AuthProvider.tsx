import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { ReactNode } from "react";

import * as authApi from "./authApi";
import { clearStoredSession, readStoredSession, writeStoredSession } from "./storage";
import type { LoginPayload, RegisterPayload, User } from "./types";

type AuthContextValue = {
  user: User | null;
  accessToken: string | null;
  isAuthenticated: boolean;
  isBootstrapping: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [refreshToken, setRefreshToken] = useState<string | null>(null);
  const [isBootstrapping, setIsBootstrapping] = useState(true);

  useEffect(() => {
    const stored = readStoredSession();
    if (!stored) {
      setIsBootstrapping(false);
      return;
    }

    setUser(stored.user);
    setAccessToken(stored.accessToken);
    setRefreshToken(stored.refreshToken);

    authApi
      .me(stored.accessToken)
      .then(setUser)
      .catch(async () => {
        try {
          const response = await authApi.refresh(stored.refreshToken);
          const session = writeStoredSession(response);
          setUser(session.user);
          setAccessToken(session.accessToken);
          setRefreshToken(session.refreshToken);
        } catch {
          clearStoredSession();
          setUser(null);
          setAccessToken(null);
          setRefreshToken(null);
        }
      })
      .finally(() => setIsBootstrapping(false));
  }, []);

  const handleLogin = useCallback(async (payload: LoginPayload) => {
    const response = await authApi.login(payload);
    const session = writeStoredSession(response);
    setUser(session.user);
    setAccessToken(session.accessToken);
    setRefreshToken(session.refreshToken);
  }, []);

  const handleRegister = useCallback(async (payload: RegisterPayload) => {
    const response = await authApi.register(payload);
    const session = writeStoredSession(response);
    setUser(session.user);
    setAccessToken(session.accessToken);
    setRefreshToken(session.refreshToken);
  }, []);

  const handleLogout = useCallback(async () => {
    const token = refreshToken;
    clearStoredSession();
    setUser(null);
    setAccessToken(null);
    setRefreshToken(null);

    if (token) {
      try {
        await authApi.logout(token);
      } catch {
        // Session is already cleared locally.
      }
    }
  }, [refreshToken]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      accessToken,
      isAuthenticated: Boolean(user && accessToken),
      isBootstrapping,
      login: handleLogin,
      register: handleRegister,
      logout: handleLogout,
    }),
    [accessToken, handleLogin, handleLogout, handleRegister, isBootstrapping, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }
  return context;
}
