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

const TOKEN_KEY = "sv_token";

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

  // Validate stored token on mount
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (!stored) {
      setIsLoading(false);
      return;
    }
    api.setToken(stored);
    setToken(stored);
    api
      .getMe()
      .then((u) => setUser(u))
      .catch(() => {
        // Token expired or invalid
        persistToken(null);
      })
      .finally(() => setIsLoading(false));
  }, [persistToken]);

  const login = useCallback(
    async (email: string, password: string) => {
      const res = await api.login(email, password);
      persistToken(res.token);
      setUser(res.user);
    },
    [persistToken],
  );

  const register = useCallback(
    async (email: string, password: string) => {
      const res = await api.register(email, password);
      persistToken(res.token);
      setUser(res.user);
    },
    [persistToken],
  );

  const logout = useCallback(() => {
    persistToken(null);
    setUser(null);
  }, [persistToken]);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    try {
      const u = await api.getMe();
      setUser(u);
    } catch {
      // Ignore — stale token handled on next action
    }
  }, [token]);

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
