// ── API Types matching FastAPI backend exactly ───────────────────────────

export interface AnalyzeRequest {
  resume: string;
  target_job: string;
}

// ── Raw API response (what backend actually returns) ─────────────────────

export interface ApiLearningStep {
  skill: string;
  estimated_weeks: number;
  estimated_days: number;
}

export interface ApiEvidenceProject {
  skill: string;
  project: string;
  description: string;
  deliverables: string[];
  estimated_weeks: number;
}

export interface ApiRelatedJob {
  score: number;
  job_title: string;
  company: string;
  skills: string[];
  chunk: string;
  // RAG-enriched fields (optional for backward compatibility)
  location?: string;
  salary?: string;
  apply_url?: string;
  posted_days_ago?: number;
  match_score?: number;
  match_label?: string;
  why_match?: string;
  why_gap?: string;
  best_skill_to_close_gap?: string;
}

export interface AnalyzeResponse {
  match_score: number;
  learning_priority: string;
  missing_skills: string[];
  learning_path: ApiLearningStep[];
  evidence: ApiEvidenceProject[];
  interview_prep: Record<string, unknown>[];
  rubrics: Record<string, unknown>[];
  related_jobs: ApiRelatedJob[];
  request_id: string;
  latency_ms: number;
}

// ── Display types (what the panels render — matches spec) ────────────────

export interface DisplayMissingSkill {
  skill: string;
  priority: "HIGH" | "MEDIUM" | "LOW";
  why: string;
  frequency: string;
}

export interface DisplayLearningStep {
  skill: string;
  duration: string;
  description: string;
}

export interface DisplayEvidenceProject {
  project_title: string;
  skill_covered: string;
  description: string;
  deliverables: string[];
}

export interface DisplayRelatedJob {
  title: string;
  company: string;
  match_score: number;
  required_skills: string[];
  // RAG-enriched fields
  location?: string;
  salary?: string;
  apply_url?: string;
  posted_days_ago?: number;
  match_label?: string;
  why_match?: string;
  why_gap?: string;
  best_skill_to_close_gap?: string;
}

export interface DisplayResult {
  match_score: number;
  request_id: string;
  latency_ms: number;
  missing_skills: DisplayMissingSkill[];
  learning_path: DisplayLearningStep[];
  evidence: DisplayEvidenceProject[];
  related_jobs: DisplayRelatedJob[];
}

export interface HealthResponse {
  status: string;
  version: string;
  model: string;
  anthropic: string;
  neo4j: string;
  pinecone: string;
  checks_ms: number;
}

export interface ApiError {
  error: string;
}

// ── Auth types (v3) ──────────────────────────────────────────────────────

export interface AuthResponse {
  token: string;
  user: UserInfo;
}

export interface UserInfo {
  id: string;
  email: string;
  plan_tier: "free" | "pro";
  analyses_used: number;
  analyses_limit: number; // 3 for free, -1 for unlimited
}
