"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth-context";
import UsageBadge from "@/components/UsageBadge";
import type { HealthResponse } from "@/lib/types";

interface HealthBannerProps {
  onSignIn?: () => void;
}

export default function HealthBanner({ onSignIn }: HealthBannerProps) {
  const { user, logout } = useAuth();
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [status, setStatus] = useState<"checking" | "ok" | "error">("checking");
  const [latency, setLatency] = useState(0);

  useEffect(() => {
    const start = Date.now();
    api
      .health()
      .then((data) => {
        setHealth(data);
        setLatency(Date.now() - start);
        setStatus("ok");
      })
      .catch(() => {
        setStatus("error");
      });
  }, []);

  const dotClass =
    status === "ok"
      ? "bg-accent animate-pulse"
      : status === "error"
        ? "bg-warn"
        : "bg-muted animate-pulse";

  const label =
    status === "ok"
      ? `API CONNECTED (${latency}ms)`
      : status === "error"
        ? "API OFFLINE"
        : "WAKING SERVER...";

  return (
    <nav className="sticky top-0 z-50 border-b border-white/10 backdrop-blur-xl bg-bg/80">
      <div className="max-w-7xl mx-auto px-6 h-[60px] flex items-center justify-between">
        {/* Logo */}
        <div className="text-lg font-extrabold tracking-tight">
          Skill<span className="text-accent">Vector</span>
        </div>

        {/* Version tag */}
        <span className="hidden sm:inline font-mono text-[10px] text-accent bg-accent/10 border border-accent/20 px-2.5 py-0.5 rounded-sm tracking-widest">
          V3.0 PRODUCTION
        </span>

        {/* Right side */}
        <div className="flex items-center gap-4">
          {/* Health status */}
          <div className="hidden sm:flex items-center gap-1.5 font-mono text-[11px] text-muted">
            <span className={`w-1.5 h-1.5 rounded-full ${dotClass}`} />
            {label}
          </div>

          {health && (
            <span className="hidden md:inline font-mono text-[10px] text-muted">
              {health.model}
            </span>
          )}

          {/* Auth section */}
          {user ? (
            <div className="flex items-center gap-3">
              <UsageBadge />
              <span className="hidden sm:inline font-mono text-[11px] text-muted truncate max-w-[140px]">
                {user.email}
              </span>
              <button
                onClick={logout}
                className="font-mono text-[11px] text-muted hover:text-[#fca5a5] transition-colors tracking-wider"
              >
                SIGN OUT
              </button>
            </div>
          ) : (
            <button
              onClick={onSignIn}
              className="font-mono text-[11px] text-accent hover:text-[#00ffb3] transition-colors tracking-wider"
            >
              SIGN IN
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
