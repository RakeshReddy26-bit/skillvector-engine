import type { DisplayResult } from "./types";

// ── Demo resume + job (for text paste mode) ──────────────────────────────

export const DEMO_RESUME = `RAKESH REDDY — Machine Learning Engineer
3+ years building ML systems. Python, TensorFlow, PyTorch, Scikit-learn.
Experience: Feature engineering, model training, A/B testing, monitoring.
Projects: Real-time recommendation engine (Python + Redis), NLP text classifier,
Computer vision pipeline for defect detection. Comfortable with SQL, Git, Linux.
Currently learning: LLMs, RAG pipelines, vector databases.`;

export const DEMO_JOB = `Senior ML Engineer at Stripe
Requirements: 5+ years ML experience. Expertise in MLOps, Kubeflow, model deployment
at scale. Experience with LLMOps, evaluation frameworks (deepeval, RAGAS).
Distributed systems knowledge (Ray, Spark). Feature stores (Feast/Tecton).
Strong Python, Docker, Kubernetes, CI/CD. Published research a plus.
Responsibilities: Lead ML platform team, build production model pipelines,
implement LLM-powered features, establish ML best practices.`;

// ── Demo result (exact data from spec — bypasses API) ────────────────────

export const DEMO_RESULT: DisplayResult = {
  match_score: 74,
  request_id: "demo_001",
  latency_ms: 2800,
  missing_skills: [
    {
      skill: "MLOps / Kubeflow",
      priority: "HIGH",
      why: "Required to deploy and monitor models at scale. Appears in 87% of senior ML job postings.",
      frequency: "87%",
    },
    {
      skill: "LLMOps & Evals",
      priority: "HIGH",
      why: "Eval frameworks like deepeval and RAGAS are now table-stakes for senior ML engineers.",
      frequency: "73%",
    },
    {
      skill: "Distributed Systems",
      priority: "MEDIUM",
      why: "Senior roles need deep fault tolerance and distributed training knowledge.",
      frequency: "61%",
    },
    {
      skill: "Feature Stores",
      priority: "LOW",
      why: "Feast/Tecton experience validates production ML mindset.",
      frequency: "44%",
    },
  ],
  learning_path: [
    {
      skill: "Week 1-2 \u00b7 MLOps Foundations",
      duration: "2 weeks",
      description:
        "Complete MLOps Zoomcamp. Build a Kubeflow pipeline. Deploy with FastAPI + Docker. Push to GitHub.",
    },
    {
      skill: "Week 3-4 \u00b7 LLMOps & Evals",
      duration: "2 weeks",
      description:
        "Build RAG pipeline with Claude. Add deepeval suite. Score with RAGAS. Publish results.",
    },
    {
      skill: "Week 5-6 \u00b7 Distributed Systems",
      duration: "2 weeks",
      description:
        "Read DDIA Ch 5-9. Build one Ray distributed training job. Document tradeoffs.",
    },
    {
      skill: "Week 7-8 \u00b7 Portfolio + Apply",
      duration: "2 weeks",
      description:
        "Bundle projects as Career Evidence Pack. Update LinkedIn. Begin targeted applications.",
    },
  ],
  evidence: [
    {
      project_title: "ML Model Deployment Pipeline",
      skill_covered: "MLOps",
      description:
        "Production-grade model serving with FastAPI, Docker, Kubeflow. Drift monitoring + Prometheus metrics.",
      deliverables: [
        "GitHub repo with CI/CD",
        "Docker Compose setup",
        "Grafana dashboard",
        "Architecture README",
      ],
    },
    {
      project_title: "RAG Evaluation Framework",
      skill_covered: "LLMOps",
      description:
        "Complete RAG pipeline with Claude as LLM layer. RAGAS + deepeval evaluation. Published benchmarks.",
      deliverables: [
        "Pinecone vector store",
        "Claude Sonnet eval layer",
        "RAGAS scorecard",
        "Public blog post",
      ],
    },
  ],
  related_jobs: [
    {
      title: "Senior ML Engineer",
      company: "Stripe",
      match_score: 74,
      required_skills: ["Python", "MLOps", "LLMOps", "Kubeflow"],
      location: "San Francisco, CA (Remote)",
      salary: "$220k-$310k",
      apply_url: "https://stripe.com/jobs",
      posted_days_ago: 3,
      match_label: "Strong Match",
      why_match: "Your Python, TensorFlow, and model training experience align well with their ML platform needs.",
      why_gap: "Missing MLOps/Kubeflow and LLMOps experience required for this senior role.",
      best_skill_to_close_gap: "MLOps / Kubeflow",
    },
    {
      title: "ML Platform Engineer",
      company: "Anthropic",
      match_score: 68,
      required_skills: ["Python", "Evals", "Ray", "Distributed Systems"],
      location: "San Francisco, CA",
      salary: "$250k-$375k",
      apply_url: "https://anthropic.com/careers",
      posted_days_ago: 7,
      match_label: "Good Match",
      why_match: "Strong Python skills and RAG/LLM learning trajectory match their research engineering focus.",
      why_gap: "Needs distributed systems experience with Ray and evaluation framework expertise.",
      best_skill_to_close_gap: "Distributed Systems",
    },
    {
      title: "AI/ML Engineer",
      company: "Notion",
      match_score: 61,
      required_skills: ["Python", "FastAPI", "LLMs", "Feature Stores"],
      location: "New York, NY (Hybrid)",
      salary: "$190k-$260k",
      apply_url: "https://notion.so/careers",
      posted_days_ago: 12,
      match_label: "Moderate Match",
      why_match: "Python and FastAPI experience directly applicable. ML fundamentals are solid.",
      why_gap: "Feature store experience (Feast/Tecton) and production LLM integration not demonstrated.",
      best_skill_to_close_gap: "Feature Stores",
    },
  ],
};
