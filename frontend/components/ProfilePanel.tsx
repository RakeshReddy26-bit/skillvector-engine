"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/lib/auth-context";
import { useGeoPrice } from "@/lib/use-geo-price";
import { api } from "@/lib/api";
import type { AnalysisHistoryItem } from "@/lib/types";

interface ProfilePanelProps {
  open: boolean;
  onClose: () => void;
  onUpgrade: () => void;
}

export default function ProfilePanel({ open, onClose, onUpgrade }: ProfilePanelProps) {
  const { user } = useAuth();
  const geo = useGeoPrice();
  const [history, setHistory] = useState<AnalysisHistoryItem[]>([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    if (!open || !user) return;
    setLoadingHistory(true);
    api
      .getHistory()
      .then(setHistory)
      .catch(() => setHistory([]))
      .finally(() => setLoadingHistory(false));
  }, [open, user]);

  if (!open || !user) return null;

  const isFree = user.plan_tier === "free";
  const usagePercent = isFree
    ? Math.min((user.analyses_used / user.analyses_limit) * 100, 100)
    : 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center">
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" onClick={onClose} />

      <div className="relative w-full max-w-lg mx-4 bg-[#0d1117] border border-white/10 rounded-xl p-8 animate-fade-up max-h-[90vh] overflow-y-auto">
        {/* Close */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#5a6478] hover:text-white transition-colors text-lg"
        >
          &times;
        </button>

        {/* Profile Header */}
        <div className="flex items-center gap-4 mb-8">
          <div className="w-12 h-12 rounded-full bg-[#00e5a0]/10 border border-[#00e5a0]/20 flex items-center justify-center text-[#00e5a0] font-bold text-lg">
            {user.email[0].toUpperCase()}
          </div>
          <div>
            <p className="text-sm font-bold text-white truncate max-w-[280px]">{user.email}</p>
            <span className={`font-mono text-[10px] tracking-widest px-2 py-0.5 rounded-sm ${
              isFree
                ? "text-[#5a6478] bg-white/5 border border-white/10"
                : "text-[#7c6fff] bg-[#7c6fff]/10 border border-[#7c6fff]/20"
            }`}>
              {isFree ? "FREE PLAN" : "PRO PLAN"}
            </span>
          </div>
        </div>

        {/* Usage */}
        <div className="mb-8 p-4 bg-[#080b10] border border-white/10 rounded-lg">
          <div className="flex justify-between items-center mb-2">
            <span className="font-mono text-[10px] text-[#5a6478] tracking-widest">MONTHLY USAGE</span>
            <span className="font-mono text-sm text-white">
              {user.analyses_used}/{isFree ? user.analyses_limit : "∞"}
            </span>
          </div>
          {isFree && (
            <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
              <div
                className="h-full rounded-full transition-all duration-500"
                style={{
                  width: `${usagePercent}%`,
                  backgroundColor: usagePercent >= 100 ? "#ef4444" : "#00e5a0",
                }}
              />
            </div>
          )}
          {isFree && (
            <p className="mt-2 font-mono text-[10px] text-[#5a6478]">
              {user.analyses_limit - user.analyses_used > 0
                ? `${user.analyses_limit - user.analyses_used} analyses remaining this month`
                : "No analyses remaining this month"}
            </p>
          )}
        </div>

        {/* Plan Cards */}
        <div className="grid grid-cols-2 gap-3 mb-8">
          {/* Free Plan */}
          <div className={`p-4 rounded-lg border ${isFree ? "border-[#00e5a0]/30 bg-[#00e5a0]/5" : "border-white/10 bg-[#080b10]"}`}>
            <p className="font-bold text-sm mb-1">Free</p>
            <p className="text-2xl font-extrabold mb-2">{geo.symbol}0</p>
            <ul className="space-y-1 font-mono text-[10px] text-[#5a6478]">
              <li>✓ 3 analyses/month</li>
              <li>✓ Demo mode</li>
              <li>✓ Basic results</li>
            </ul>
            {isFree && (
              <div className="mt-3 text-center font-mono text-[10px] text-[#00e5a0]">CURRENT</div>
            )}
          </div>

          {/* Pro Plan */}
          <div className={`p-4 rounded-lg border ${!isFree ? "border-[#7c6fff]/30 bg-[#7c6fff]/5" : "border-white/10 bg-[#080b10]"}`}>
            <p className="font-bold text-sm mb-1">Pro</p>
            <p className="text-2xl font-extrabold mb-0.5">
              {geo.label}<span className="text-xs font-normal text-[#5a6478]">/mo</span>
            </p>
            <p className="font-mono text-[9px] text-[#00e5a0] mb-2">
              or {geo.yearlyLabel}/year
            </p>
            <ul className="space-y-1 font-mono text-[10px] text-[#5a6478]">
              <li>✓ Unlimited analyses</li>
              <li>✓ File uploads</li>
              <li>✓ Interview prep</li>
              <li>✓ Priority support</li>
            </ul>
            {isFree ? (
              <button
                onClick={onUpgrade}
                className="mt-3 w-full py-1.5 bg-[#00e5a0] text-black font-bold text-[11px] rounded-md hover:bg-[#00ffb3] transition-all"
              >
                UPGRADE
              </button>
            ) : (
              <div className="mt-3 text-center font-mono text-[10px] text-[#7c6fff]">CURRENT</div>
            )}
          </div>
        </div>

        {/* Analysis History */}
        <div>
          <h3 className="font-mono text-[10px] text-[#5a6478] tracking-widest mb-3">ANALYSIS HISTORY</h3>
          {loadingHistory ? (
            <div className="text-center py-6 font-mono text-xs text-[#5a6478]">Loading...</div>
          ) : history.length === 0 ? (
            <div className="text-center py-6 font-mono text-xs text-[#5a6478]">
              No analyses yet. Run your first analysis!
            </div>
          ) : (
            <div className="space-y-2 max-h-[200px] overflow-y-auto">
              {history.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3 bg-[#080b10] border border-white/10 rounded-lg"
                >
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className={`font-mono text-xs font-bold ${
                        item.match_score >= 75
                          ? "text-[#00e5a0]"
                          : item.match_score >= 50
                            ? "text-[#f59e0b]"
                            : "text-[#ef4444]"
                      }`}>
                        {item.match_score}%
                      </span>
                      <span className="font-mono text-[10px] text-[#5a6478]">
                        {item.missing_skills.length} missing skills
                      </span>
                    </div>
                    <p className="font-mono text-[10px] text-[#5a6478] mt-0.5 truncate">
                      {item.missing_skills.slice(0, 3).join(", ")}
                      {item.missing_skills.length > 3 ? "..." : ""}
                    </p>
                  </div>
                  <span className="font-mono text-[9px] text-[#5a6478] ml-2 whitespace-nowrap">
                    {new Date(item.created_at).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
