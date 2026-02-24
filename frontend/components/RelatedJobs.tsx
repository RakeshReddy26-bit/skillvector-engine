"use client";

import type { DisplayRelatedJob } from "@/lib/types";

interface RelatedJobsProps {
  jobs: DisplayRelatedJob[];
}

function scoreColor(score: number): string {
  if (score >= 80) return "#00e5a0";
  if (score >= 60) return "#f59e0b";
  return "#ef4444";
}

function scoreBg(score: number): string {
  if (score >= 80) return "rgba(0,229,160,0.08)";
  if (score >= 60) return "rgba(245,158,11,0.08)";
  return "rgba(239,68,68,0.08)";
}

export default function RelatedJobs({ jobs }: RelatedJobsProps) {
  if (jobs.length === 0) return null;

  return (
    <div className="flex flex-col gap-4">
      {jobs.map((job, i) => {
        const hasRichData = !!(job.why_match || job.match_label);

        if (!hasRichData) {
          // Fallback: simple row (backward compatible)
          return (
            <div key={`${job.title}-${i}`} className="job-row">
              <span className="match-pct">{job.match_score}%</span>
              <div className="job-info">
                <strong>{job.title}</strong>
                <span>{job.company}</span>
              </div>
              <div className="skill-chips">
                {job.required_skills.map((s) => (
                  <span key={s} className="chip">{s}</span>
                ))}
              </div>
              <span className="arrow">&rarr;</span>
            </div>
          );
        }

        // Rich card with Claude scoring
        return (
          <div
            key={`${job.title}-${i}`}
            className="job-card-rich"
            style={{ animationDelay: `${i * 0.08}s` }}
          >
            {/* Header row */}
            <div className="job-card-header">
              <div
                className="job-card-score"
                style={{ color: scoreColor(job.match_score), background: scoreBg(job.match_score) }}
              >
                {job.match_score}%
              </div>
              <div className="job-card-title-block">
                <strong>{job.title}</strong>
                <span className="job-card-company">{job.company}</span>
                {job.location && (
                  <span className="job-card-meta">{job.location}</span>
                )}
              </div>
              <div className="job-card-right">
                {job.salary && <span className="job-card-salary">{job.salary}</span>}
                {job.match_label && (
                  <span
                    className="job-card-label"
                    style={{ color: scoreColor(job.match_score), borderColor: scoreColor(job.match_score) }}
                  >
                    {job.match_label}
                  </span>
                )}
              </div>
            </div>

            {/* Claude explanations */}
            {(job.why_match || job.why_gap) && (
              <div className="job-card-insights">
                {job.why_match && (
                  <div className="job-card-insight">
                    <span className="insight-icon" style={{ color: "#00e5a0" }}>+</span>
                    <span>{job.why_match}</span>
                  </div>
                )}
                {job.why_gap && (
                  <div className="job-card-insight">
                    <span className="insight-icon" style={{ color: "#f59e0b" }}>!</span>
                    <span>{job.why_gap}</span>
                  </div>
                )}
                {job.best_skill_to_close_gap && (
                  <div className="job-card-insight">
                    <span className="insight-icon" style={{ color: "#7c6fff" }}>&rarr;</span>
                    <span>Focus on: <strong>{job.best_skill_to_close_gap}</strong></span>
                  </div>
                )}
              </div>
            )}

            {/* Footer: skills + apply */}
            <div className="job-card-footer">
              <div className="skill-chips">
                {job.required_skills.slice(0, 5).map((s) => (
                  <span key={s} className="chip">{s}</span>
                ))}
                {job.required_skills.length > 5 && (
                  <span className="chip">+{job.required_skills.length - 5}</span>
                )}
              </div>
              <div className="job-card-actions">
                {job.posted_days_ago !== undefined && job.posted_days_ago > 0 && (
                  <span className="job-card-posted">
                    {job.posted_days_ago}d ago
                  </span>
                )}
                {job.apply_url && (
                  <a
                    href={job.apply_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="job-apply-btn"
                  >
                    Apply &rarr;
                  </a>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
