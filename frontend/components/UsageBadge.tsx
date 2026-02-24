"use client";

import { useAuth } from "@/lib/auth-context";

export default function UsageBadge() {
  const { user } = useAuth();

  if (!user) return null;

  if (user.plan_tier === "pro") {
    return (
      <span className="font-mono text-[10px] tracking-widest text-[#7c6fff] bg-[#7c6fff]/10 border border-[#7c6fff]/20 px-2.5 py-0.5 rounded-sm">
        PRO
      </span>
    );
  }

  return (
    <span className="font-mono text-[10px] tracking-widest text-[#5a6478] bg-white/5 border border-white/10 px-2.5 py-0.5 rounded-sm">
      {user.analyses_used}/{user.analyses_limit} USED
    </span>
  );
}
