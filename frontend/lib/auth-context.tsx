"use client";

import { createContext, useCallback, useContext, useEffect, useState } from "react";
import { api } from "./api";
import type { UserInfo } from "./types";

interface AuthState {
  user: UserInfo | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

const TOKEN_KEY = "token";
const USER_KEY = "user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserInfo | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Sync token with API client and localStorage
  const persistToken = useCallback((t: string | null) => {
    setToken(t);
    api.setToken(t);
    if (t) {
      localStorage.setItem(TOKEN_KEY, t);
    } else {
      localStorage.removeItem(TOKEN_KEY);
    }
  }, []);

  const persistUser = useCallback((u: UserInfo | null) => {
    setUser(u);
    if (u) {
      localStorage.setItem(USER_KEY, JSON.stringify(u));
    } else {
      localStorage.removeItem(USER_KEY);
    }
  }, []);

  // Validate stored token on mount + handle OAuth callback
  useEffect(() => {
    // Check for OAuth token in URL params
    const params = new URLSearchParams(window.location.search);
    const oauthToken = params.get("token");
    const oauthError = params.get("error");

    if (oauthError) {
      window.history.replaceState({}, "", window.location.pathname);
      setIsLoading(false);
      return;
    }

    if (oauthToken) {
      // Clean URL
      window.history.replaceState({}, "", window.location.pathname);
      api.setToken(oauthToken);
      setToken(oauthToken);
      localStorage.setItem(TOKEN_KEY, oauthToken);
      api
        .getMe()
        .then((u) => persistUser(u))
        .catch(() => {
          persistToken(null);
          persistUser(null);
        })
        .finally(() => setIsLoading(false));
      return;
    }

    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setIsLoading(false);
      return;
    }
    api.setToken(stored);
    setToken(stored);
    api
      .getMe()
      .then((u) => persistUser(u))
      .catch(() => {
        // Token expired or invalid
        persistToken(null);
        persistUser(null);
      })
      .finally(() => setIsLoading(false));
  }, [persistToken, persistUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.login(email, password);
      localStorage.setItem("token", res.token);
      localStorage.setItem("user", JSON.stringify(res.user));
      persistToken(res.token);
      persistUser(res.user);
    },
    [persistToken, persistUser],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await api.register(email, password);
      persistToken(res.token);
      persistUser(res.user);
    },
    [persistToken, persistUser],
  );

  const logout = useCallback(() => {
    persistToken(null);
    persistUser(null);
  }, [persistToken, persistUser]);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    try {
      const u = await api.getMe();
      persistUser(u);
    } catch {
      // Ignore — stale token handled on next action
    }
  }, [persistUser, token]);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
