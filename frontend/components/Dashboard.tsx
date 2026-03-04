"use client";

import { useEffect, useState, useCallback } from "react";
import { api } from "@/lib/api";
import type { DashboardHistory, DashboardStats } from "@/lib/types";

// ── Score color helper ───────────────────────────────────────────────────
function scoreColor(score: number): string {
  if (score >= 70) return "#00e5a0";
  if (score >= 40) return "#f59e0b";
  return "#ef4444";
}

function scoreBg(score: number): string {
  if (score >= 70) return "rgba(0,229,160,0.08)";
  if (score >= 40) return "rgba(245,158,11,0.08)";
  return "rgba(239,68,68,0.08)";
}

function scoreLabel(score: number): string {
  if (score >= 70) return "Strong";
  if (score >= 40) return "Moderate";
  return "Needs Work";
}

interface DashboardProps {
  onClose: () => void;
}

export default function Dashboard({ onClose }: DashboardProps) {
  const [history, setHistory] = useState<DashboardHistory | null>(null);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [historyData, statsData] = await Promise.all([
        api.getDashboardHistory(),
        api.getDashboardStats(),
      ]);
      setHistory(historyData);
      setStats(statsData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleDelete = useCallback(async (analysisId: string) => {
    setDeletingId(analysisId);
    try {
      await api.deleteAnalysis(analysisId);
      await fetchData();
    } catch {
      setError("Failed to delete analysis");
    } finally {
      setDeletingId(null);
    }
  }, [fetchData]);

  const downloadReport = useCallback(async (result: Record<string, unknown>) => {
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "https://api.skill-vector.com";
      const token = localStorage.getItem("token");
      const response = await fetch(`${apiBase}/reports/generate`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token ?? ""}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify(result),
      });
      if (!response.ok) throw new Error("PDF generation failed");
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "skillvector_report.pdf";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error("Download failed:", err);
    }
  }, []);

  // ── Loading state ──────────────────────────────────────────────────
  if (loading) {
    return (
      <div className="fixed inset-0 z-50 bg-[#080b10]/95 backdrop-blur-xl overflow-auto">
        <div className="max-w-5xl mx-auto px-6 py-12">
          <div className="flex items-center justify-center h-64">
            <div className="text-center">
              <div className="w-8 h-8 border-2 border-[#00e5a0] border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <p className="font-mono text-sm text-[#5a6478]">Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-[#080b10]/95 backdrop-blur-xl overflow-auto">
      <div className="max-w-5xl mx-auto px-6 py-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight text-[#e8edf5]">
              Your <span className="text-[#00e5a0]">Dashboard</span>
            </h1>
            {history?.user && (
              <p className="font-mono text-xs text-[#5a6478] mt-1">
                {history.user.email} &middot;{" "}
                <span className="text-[#7c6fff]">{history.user.plan_tier.toUpperCase()}</span>
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="font-mono text-sm text-[#5a6478] hover:text-[#e8edf5] transition-colors px-4 py-2 border border-white/10 rounded-lg hover:border-white/20"
          >
            CLOSE &times;
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="mb-6 p-4 rounded-lg border border-[#ef4444]/30 bg-[#ef4444]/5 text-[#ef4444] font-mono text-sm">
            {error}
          </div>
        )}

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
            <StatCard label="Total Analyses" value={String(stats.total_analyses)} accent="#00e5a0" />
            <StatCard label="Avg Match Score" value={`${stats.avg_match_score}%`} accent={scoreColor(stats.avg_match_score)} />
            <StatCard label="Best Score" value={`${stats.best_match_score}%`} accent={scoreColor(stats.best_match_score)} />
            <StatCard
              label="Improvement"
              value={stats.improvement > 0 ? `+${stats.improvement}` : String(stats.improvement)}
              accent={stats.improvement > 0 ? "#00e5a0" : stats.improvement < 0 ? "#ef4444" : "#5a6478"}
            />
          </div>
        )}

        {/* Most Common Gap */}
        {stats?.most_common_gap && (
          <div className="mb-8 p-4 rounded-lg border border-[#7c6fff]/20 bg-[#7c6fff]/5">
            <span className="font-mono text-[10px] text-[#7c6fff] tracking-widest">MOST COMMON GAP</span>
            <p className="text-[#e8edf5] font-bold mt-1">{stats.most_common_gap}</p>
          </div>
        )}

        {/* Analysis History */}
        <div className="mb-4">
          <h2 className="text-lg font-bold text-[#e8edf5]">Analysis History</h2>
          <p className="font-mono text-xs text-[#5a6478]">
            {history?.total ?? 0} past analyses
          </p>
        </div>

        {(!history?.analyses || history.analyses.length === 0) ? (
          /* Empty State */
          <div className="text-center py-20 border border-white/10 rounded-xl bg-[#0d1117]">
            <div className="text-4xl mb-4">📊</div>
            <h3 className="text-lg font-bold text-[#e8edf5] mb-2">No analyses yet</h3>
            <p className="font-mono text-sm text-[#5a6478] max-w-md mx-auto mb-6">
              Upload your resume and a target job description to get your first skill gap analysis.
            </p>
            <button
              onClick={onClose}
              className="px-6 py-2.5 bg-[#00e5a0] text-black font-bold text-sm rounded-lg hover:bg-[#00ffb3] transition-all"
            >
              START ANALYSIS &rarr;
            </button>
          </div>
        ) : (
          /* Analysis List */
          <div className="space-y-3">
            {history.analyses.map((analysis) => {
              const score = Math.round(analysis.match_score ?? 0);
              const gaps = analysis.missing_skills ?? [];
              const gapCount = Array.isArray(gaps) ? gaps.length : 0;
              const date = analysis.created_at
                ? new Date(analysis.created_at).toLocaleDateString("en-US", {
                    month: "short",
                    day: "numeric",
                    year: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })
                : "—";

              return (
                <div
                  key={analysis.id}
                  className="flex items-center gap-4 p-4 rounded-xl border border-white/10 bg-[#0d1117] hover:border-white/20 transition-all group"
                >
                  {/* Score Ring */}
                  <div
                    className="w-14 h-14 rounded-full flex items-center justify-center flex-shrink-0 border-2"
                    style={{
                      borderColor: scoreColor(score),
                      backgroundColor: scoreBg(score),
                    }}
                  >
                    <span className="font-mono text-sm font-bold" style={{ color: scoreColor(score) }}>
                      {score}%
                    </span>
                  </div>

                  {/* Details */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className="font-mono text-[10px] px-2 py-0.5 rounded"
                        style={{
                          color: scoreColor(score),
                          backgroundColor: scoreBg(score),
                        }}
                      >
                        {scoreLabel(score)}
                      </span>
                      {analysis.detected_language && analysis.detected_language !== "English" && (
                        <span className="font-mono text-[10px] px-2 py-0.5 rounded text-[#7c6fff] bg-[#7c6fff]/10">
                          {analysis.detected_language}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-[#e8edf5] font-medium truncate">
                      {analysis.result?.target_role ?? "Analysis"}
                    </p>
                    <p className="font-mono text-[11px] text-[#5a6478]">
                      {date} &middot; {gapCount} skill gap{gapCount !== 1 ? "s" : ""}
                    </p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {analysis.result && (
                      <button
                        onClick={() => downloadReport(analysis.result as Record<string, unknown>)}
                        className="font-mono text-[11px] px-3 py-1.5 rounded-md border border-[#00e5a0]/30 text-[#00e5a0] hover:bg-[#00e5a0]/10 transition-all"
                      >
                        View Report
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(analysis.id)}
                      disabled={deletingId === analysis.id}
                      className="font-mono text-[11px] px-3 py-1.5 rounded-md border border-[#ef4444]/30 text-[#ef4444] hover:bg-[#ef4444]/10 transition-all disabled:opacity-50"
                    >
                      {deletingId === analysis.id ? "..." : "Delete"}
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Stat Card ────────────────────────────────────────────────────────────

function StatCard({ label, value, accent }: { label: string; value: string; accent: string }) {
  return (
    <div className="p-4 rounded-xl border border-white/10 bg-[#0d1117] text-center">
      <div className="text-2xl font-extrabold font-mono" style={{ color: accent }}>
        {value}
      </div>
      <div className="font-mono text-[10px] text-[#5a6478] tracking-widest mt-1">
        {label.toUpperCase()}
      </div>
    </div>
  );
}
