"use client";

import { useEffect, useRef } from "react";

interface ScoreRingProps {
  score: number;
  requestId: string;
  latencyMs: number;
}

export default function ScoreRing({ score, requestId, latencyMs }: ScoreRingProps) {
  const circleRef = useRef<SVGCircleElement>(null);
  const rounded = Math.round(score);
  const radius = 70;
  const circumference = 2 * Math.PI * radius; // ~440
  const offset = circumference - (score / 100) * circumference;

  const color =
    rounded > 70 ? "#00e5a0" : rounded > 40 ? "#f59e0b" : "#ef4444";
  const title =
    rounded >= 80
      ? "Excellent Match"
      : rounded >= 60
        ? "Strong Candidate Signal"
        : rounded >= 40
          ? "Moderate Match"
          : "Significant Gaps Detected";

  useEffect(() => {
    const el = circleRef.current;
    if (!el) return;
    el.style.strokeDashoffset = String(circumference);
    requestAnimationFrame(() => {
      el.style.transition = "stroke-dashoffset 1.2s ease";
      el.style.strokeDashoffset = String(offset);
    });
  }, [circumference, offset]);

  return (
    <div className="bg-surface border border-white/10 rounded-xl p-10 flex flex-col md:flex-row items-center gap-10 relative overflow-hidden">
      {/* Glow */}
      <div className="absolute -top-16 -right-16 w-52 h-52 rounded-full bg-accent/5 blur-2xl" />

      {/* Ring */}
      <div className="score-ring-container">
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle cx="80" cy="80" r={radius} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
          <circle
            ref={circleRef}
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={circumference}
            transform="rotate(-90 80 80)"
            style={{ filter: `drop-shadow(0 0 8px ${color})` }}
          />
        </svg>
        <div className="score-center">
          <span className="score-number" style={{ color }}>{rounded}</span>
          <span className="score-label">MATCH %</span>
        </div>
      </div>

      {/* Info */}
      <div className="relative">
        <h2 className="text-2xl font-extrabold mb-2">{title}</h2>
        <p className="font-mono text-xs text-muted leading-relaxed max-w-sm mb-4">
          Claude analyzed your resume against the target role. {rounded > 70 ? "Strong alignment detected." : `${Math.max(1, 4 - Math.floor(rounded / 25))} critical gaps identified.`}
        </p>
        <p className="font-mono text-xs text-muted mb-4">
          Analyzed in <span className="text-accent">{(latencyMs / 1000).toFixed(1)}s</span>
        </p>
        <div className="flex flex-wrap gap-3">
          <span className="font-mono text-[10px] text-muted bg-white/5 border border-white/10 px-2.5 py-1 rounded-sm">
            Score: <span style={{ color }}>{rounded}%</span>
          </span>
          <span className="font-mono text-[10px] text-muted bg-white/5 border border-white/10 px-2.5 py-1 rounded-sm truncate max-w-[200px]">
            ID: {requestId}
          </span>
        </div>
      </div>
    </div>
  );
}
