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

  if (!open) return null;

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
