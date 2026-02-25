import type { AnalyzeRequest, AnalyzeResponse, AuthResponse, DisplayResult, HealthResponse, UserInfo } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "https://api.skill-vector.com";

// ── Transform API response → Display format ──────────────────────────────

export function transformApiResponse(raw: AnalyzeResponse): DisplayResult {
  return {
    match_score: raw.match_score,
    request_id: raw.request_id,
    latency_ms: raw.latency_ms,

    // API returns string[], transform to rich objects
    missing_skills: raw.missing_skills.map((skill, i) => ({
      skill,
      priority: (i < 2 ? "HIGH" : i < 4 ? "MEDIUM" : "LOW") as "HIGH" | "MEDIUM" | "LOW",
      why: `Identified as a critical gap between your profile and the target role.`,
      frequency: "",
    })),

    // API returns {skill, estimated_weeks, estimated_days}
    learning_path: raw.learning_path.map((step) => ({
      skill: step.skill,
      duration: `${step.estimated_weeks} week${step.estimated_weeks !== 1 ? "s" : ""}`,
      description: `Focus on ${step.skill} for approximately ${step.estimated_weeks} weeks (${step.estimated_days} days).`,
    })),

    // API returns {skill, project, description, deliverables, estimated_weeks}
    evidence: raw.evidence.map((item) => ({
      project_title: item.project,
      skill_covered: item.skill,
      description: item.description,
      deliverables: item.deliverables,
    })),

    // API returns {score, job_title, company, skills, chunk} + RAG-enriched fields
    related_jobs: raw.related_jobs.map((job) => ({
      title: job.job_title,
      company: job.company,
      match_score: job.match_score ?? Math.round(job.score * 100),
      required_skills: job.skills,
      location: job.location,
      salary: job.salary,
      apply_url: job.apply_url,
      posted_days_ago: job.posted_days_ago,
      match_label: job.match_label,
      why_match: job.why_match,
      why_gap: job.why_gap,
      best_skill_to_close_gap: job.best_skill_to_close_gap,
    })),
  };
}

// ── API Client ───────────────────────────────────────────────────────────

class ApiClient {
  private base: string;
  private token: string | null = null;

  constructor(base: string) {
    this.base = base;
  }

  setToken(t: string | null) {
    this.token = t;
  }

  private authHeaders(json = true): Record<string, string> {
    const h: Record<string, string> = {};
    if (json) h["Content-Type"] = "application/json";
    if (this.token) h["Authorization"] = `Bearer ${this.token}`;
    return h;
  }

  // ── Health ──────────────────────────────────────────────────────────

  async health(): Promise<HealthResponse> {
    const res = await fetch(`${this.base}/health`, {
      signal: AbortSignal.timeout(15_000),
    });
    if (!res.ok) throw new Error(`Health check failed: ${res.status}`);
    return res.json() as Promise<HealthResponse>;
  }

  // ── Analyze ─────────────────────────────────────────────────────────

  async analyze(request: AnalyzeRequest): Promise<DisplayResult> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120_000);

    try {
      const res = await fetch(`${this.base}/analyze`, {
        method: "POST",
        headers: this.authHeaders(),
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: `Request failed: ${res.status}` }));
        const err = new Error((body as { error: string }).error ?? "Analysis failed");
        (err as Error & { status?: number }).status = res.status;
        throw err;
      }

      const raw = (await res.json()) as AnalyzeResponse;
      return transformApiResponse(raw);
    } finally {
      clearTimeout(timeout);
    }
  }

  async uploadResume(file: File, targetJob: string): Promise<DisplayResult> {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 120_000);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("target_job", targetJob);

    try {
      const res = await fetch(`${this.base}/upload-resume`, {
        method: "POST",
        headers: this.authHeaders(false), // no Content-Type for FormData
        body: formData,
        signal: controller.signal,
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({ error: `Request failed: ${res.status}` }));
        const err = new Error((body as { error: string }).error ?? "Upload failed");
        (err as Error & { status?: number }).status = res.status;
        throw err;
      }

      const raw = (await res.json()) as AnalyzeResponse;
      return transformApiResponse(raw);
    } finally {
      clearTimeout(timeout);
    }
  }

  // ── Auth ────────────────────────────────────────────────────────────

  async register(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${this.base}/auth/register`, {
      method: "POST",
      headers: this.authHeaders(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ error: "Registration failed" }));
      throw new Error((body as { error: string }).error ?? "Registration failed");
    }
    return res.json() as Promise<AuthResponse>;
  }

  async login(email: string, password: string): Promise<AuthResponse> {
    const res = await fetch(`${this.base}/auth/login`, {
      method: "POST",
      headers: this.authHeaders(),
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ error: "Login failed" }));
      throw new Error((body as { error: string }).error ?? "Login failed");
    }
    return res.json() as Promise<AuthResponse>;
  }

  async getMe(): Promise<UserInfo> {
    const res = await fetch(`${this.base}/auth/me`, {
      headers: this.authHeaders(),
    });
    if (!res.ok) throw new Error("Not authenticated");
    return res.json() as Promise<UserInfo>;
  }

  // ── Stripe ──────────────────────────────────────────────────────────

  async createCheckout(): Promise<{ checkout_url: string }> {
    const res = await fetch(`${this.base}/stripe/create-checkout`, {
      method: "POST",
      headers: this.authHeaders(),
    });
    if (!res.ok) {
      const body = await res.json().catch(() => ({ error: "Checkout failed" }));
      throw new Error((body as { error: string }).error ?? "Checkout failed");
    }
    return res.json() as Promise<{ checkout_url: string }>;
  }

  async getPortalUrl(): Promise<{ portal_url: string }> {
    const res = await fetch(`${this.base}/stripe/portal`, {
      headers: this.authHeaders(),
    });
    if (!res.ok) throw new Error("Portal unavailable");
    return res.json() as Promise<{ portal_url: string }>;
  }
}

export const api = new ApiClient(API_BASE);
