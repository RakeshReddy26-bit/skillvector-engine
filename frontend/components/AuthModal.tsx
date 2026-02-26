"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth-context";

interface AuthModalProps {
  open: boolean;
  onClose: () => void;
}

export default function AuthModal({ open, onClose }: AuthModalProps) {
  const { login, register } = useAuth();
  const [tab, setTab] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "https://api.skill-vector.com";

  if (!open) return null;

  const handleOAuth = (provider: "google" | "github") => {
    window.location.href = `${API_BASE}/auth/${provider}`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (tab === "login") {
        await login(email, password);
      } else {
        await register(email, password);
      }
      setEmail("");
      setPassword("");
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      {/* Modal */}
      <div className="relative w-full max-w-md mx-4 bg-[#0d1117] border border-white/10 rounded-xl p-8 animate-fade-up">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#5a6478] hover:text-white transition-colors text-lg"
        >
          &times;
        </button>

        {/* Tabs */}
        <div className="flex gap-1 mb-8 bg-[#080b10] rounded-lg p-1">
          <button
            onClick={() => { setTab("login"); setError(""); }}
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-all ${
              tab === "login"
                ? "bg-[#00e5a0]/10 text-[#00e5a0] border border-[#00e5a0]/20"
                : "text-[#5a6478] hover:text-white border border-transparent"
            }`}
          >
            SIGN IN
          </button>
          <button
            onClick={() => { setTab("register"); setError(""); }}
            className={`flex-1 py-2 text-sm font-bold rounded-md transition-all ${
              tab === "register"
                ? "bg-[#00e5a0]/10 text-[#00e5a0] border border-[#00e5a0]/20"
                : "text-[#5a6478] hover:text-white border border-transparent"
            }`}
          >
            CREATE ACCOUNT
          </button>
        </div>

        {/* OAuth Buttons */}
        <div className="space-y-3 mb-6">
          <button
            type="button"
            onClick={() => handleOAuth("google")}
            className="w-full py-3 bg-white text-black font-bold text-sm rounded-lg hover:bg-gray-100 transition-all flex items-center justify-center gap-3"
          >
            <svg width="18" height="18" viewBox="0 0 18 18"><path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844a4.14 4.14 0 01-1.796 2.716v2.259h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/><path d="M9 18c2.43 0 4.467-.806 5.956-2.184l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/><path d="M3.964 10.706A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.706V4.962H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.038l3.007-2.332z" fill="#FBBC05"/><path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.962L3.964 7.294C4.672 5.166 6.656 3.58 9 3.58z" fill="#EA4335"/></svg>
            Continue with Google
          </button>
          <button
            type="button"
            onClick={() => handleOAuth("github")}
            className="w-full py-3 bg-[#24292f] text-white font-bold text-sm rounded-lg hover:bg-[#32383f] transition-all flex items-center justify-center gap-3"
          >
            <svg width="18" height="18" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
            Continue with GitHub
          </button>
        </div>

        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-[10px] font-mono text-[#5a6478] tracking-widest">OR</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        {/* Email/Password Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block font-mono text-[10px] text-[#5a6478] tracking-widest mb-2">
              EMAIL
            </label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 bg-[#080b10] border border-white/10 rounded-lg text-sm text-white font-mono focus:outline-none focus:border-[#00e5a0]/40 transition-colors"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block font-mono text-[10px] text-[#5a6478] tracking-widest mb-2">
              PASSWORD
            </label>
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 bg-[#080b10] border border-white/10 rounded-lg text-sm text-white font-mono focus:outline-none focus:border-[#00e5a0]/40 transition-colors"
              placeholder={tab === "register" ? "Min 8 characters" : "Your password"}
            />
          </div>

          {error && (
            <div className="text-sm text-[#fca5a5] font-mono bg-[#ef4444]/5 border border-[#ef4444]/20 rounded-lg px-4 py-3">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-[#00e5a0] text-black font-bold text-sm rounded-lg hover:bg-[#00ffb3] transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading
              ? "PLEASE WAIT..."
              : tab === "login"
                ? "SIGN IN"
                : "CREATE ACCOUNT"}
          </button>
        </form>

        <p className="mt-6 text-center font-mono text-[11px] text-[#5a6478]">
          {tab === "login" ? (
            <>
              No account?{" "}
              <button onClick={() => setTab("register")} className="text-[#00e5a0] hover:underline">
                Create one
              </button>
            </>
          ) : (
            <>
              Already have an account?{" "}
              <button onClick={() => setTab("login")} className="text-[#00e5a0] hover:underline">
                Sign in
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
