"""Personalized project generator for SkillVector Engine.

Generates portfolio project ideas tailored to a candidate's background
and target role, going beyond the static templates in EvidenceEngine.
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


# Comprehensive project templates organized by skill and difficulty
PROJECT_CATALOG: dict[str, list[dict]] = {
    "python": [
        {
            "project": "CLI Task Manager with SQLite",
            "description": "Build a command-line task management tool with persistence, "
                           "categories, priorities, and due dates using SQLite.",
            "deliverables": ["cli.py", "models.py", "tests/", "README.md"],
            "difficulty": "Beginner",
            "skills_demonstrated": ["Python", "SQLite", "CLI design", "Testing"],
        },
        {
            "project": "Async Web Scraper with Rate Limiting",
            "description": "Build an async web scraper using aiohttp that respects "
                           "robots.txt and implements polite rate limiting.",
            "deliverables": ["scraper.py", "rate_limiter.py", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["Python", "Async/await", "HTTP", "Rate limiting"],
        },
    ],
    "docker": [
        {
            "project": "Multi-Service Docker Compose Stack",
            "description": "Containerize a web app with a database, cache, "
                           "and reverse proxy using Docker Compose.",
            "deliverables": ["Dockerfile", "docker-compose.yml", "nginx.conf", "README.md"],
            "difficulty": "Beginner",
            "skills_demonstrated": ["Docker", "Networking", "Nginx", "Compose"],
        },
        {
            "project": "Custom Docker Image Registry",
            "description": "Set up a private Docker registry with authentication, "
                           "TLS, and garbage collection.",
            "deliverables": ["Dockerfile", "docker-compose.yml", "auth/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["Docker", "Security", "TLS", "Registry"],
        },
    ],
    "kubernetes": [
        {
            "project": "Kubernetes Microservice Deployment",
            "description": "Deploy a multi-tier application to Kubernetes with "
                           "rolling updates, health checks, and autoscaling.",
            "deliverables": ["k8s/deployment.yaml", "k8s/service.yaml", "k8s/hpa.yaml", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["Kubernetes", "Deployments", "HPA", "Health checks"],
        },
        {
            "project": "Helm Chart for a Stateful Application",
            "description": "Create a Helm chart for deploying a stateful app "
                           "with persistent volumes and config management.",
            "deliverables": ["charts/", "values.yaml", "templates/", "README.md"],
            "difficulty": "Advanced",
            "skills_demonstrated": ["Kubernetes", "Helm", "StatefulSets", "PVCs"],
        },
    ],
    "ci/cd": [
        {
            "project": "Full CI/CD Pipeline with GitHub Actions",
            "description": "Build a pipeline that lints, tests, builds a Docker image, "
                           "and deploys to a staging environment automatically.",
            "deliverables": [".github/workflows/ci.yml", ".github/workflows/deploy.yml", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["CI/CD", "GitHub Actions", "Docker", "Automation"],
        },
    ],
    "rest apis": [
        {
            "project": "RESTful Bookstore API with FastAPI",
            "description": "Build a complete REST API with authentication, pagination, "
                           "filtering, and OpenAPI documentation.",
            "deliverables": ["app/", "tests/", "alembic/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["REST APIs", "FastAPI", "SQLAlchemy", "Auth"],
        },
    ],
    "sql": [
        {
            "project": "Analytics Dashboard Database",
            "description": "Design a normalized database schema for an analytics platform "
                           "with optimized queries, views, and stored procedures.",
            "deliverables": ["schema.sql", "queries.sql", "seed_data.sql", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["SQL", "Schema design", "Query optimization", "Indexing"],
        },
    ],
    "aws": [
        {
            "project": "Serverless REST API on AWS",
            "description": "Build a serverless API using Lambda, API Gateway, and DynamoDB "
                           "with infrastructure defined in CloudFormation/SAM.",
            "deliverables": ["template.yaml", "src/handlers/", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["AWS", "Lambda", "API Gateway", "DynamoDB", "IaC"],
        },
        {
            "project": "Static Website with CloudFront CDN",
            "description": "Deploy a static site to S3 with CloudFront distribution, "
                           "custom domain, and CI/CD pipeline.",
            "deliverables": ["template.yaml", "buildspec.yml", "src/", "README.md"],
            "difficulty": "Beginner",
            "skills_demonstrated": ["AWS", "S3", "CloudFront", "Route53"],
        },
    ],
    "microservices": [
        {
            "project": "E-Commerce Microservices System",
            "description": "Build a small e-commerce system with separate services for "
                           "users, products, orders, and notifications communicating via events.",
            "deliverables": ["services/", "docker-compose.yml", "gateway/", "README.md"],
            "difficulty": "Advanced",
            "skills_demonstrated": ["Microservices", "Event-driven", "API Gateway", "Docker"],
        },
    ],
    "system design": [
        {
            "project": "Distributed URL Shortener",
            "description": "Design and implement a URL shortener that handles high throughput "
                           "with caching, analytics, and horizontal scaling.",
            "deliverables": ["app/", "docs/architecture.md", "load_tests/", "README.md"],
            "difficulty": "Advanced",
            "skills_demonstrated": ["System Design", "Caching", "Scaling", "Analytics"],
        },
    ],
    "terraform": [
        {
            "project": "Multi-Environment AWS Infrastructure",
            "description": "Define dev/staging/prod environments on AWS using Terraform modules "
                           "with remote state and workspaces.",
            "deliverables": ["modules/", "environments/", "backend.tf", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["Terraform", "AWS", "IaC", "State management"],
        },
    ],
    "react": [
        {
            "project": "Real-Time Dashboard with React",
            "description": "Build a responsive dashboard with live data updates, "
                           "charts, filters, and dark mode using React and TypeScript.",
            "deliverables": ["src/components/", "src/hooks/", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["React", "TypeScript", "WebSockets", "Responsive design"],
        },
    ],
    "typescript": [
        {
            "project": "Type-Safe Express API",
            "description": "Build an Express.js API with full TypeScript coverage, "
                           "Zod validation, and auto-generated API docs.",
            "deliverables": ["src/", "tsconfig.json", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["TypeScript", "Express", "Validation", "API design"],
        },
    ],
    "graphql": [
        {
            "project": "GraphQL API with Apollo Server",
            "description": "Build a GraphQL API with queries, mutations, subscriptions, "
                           "and DataLoader for efficient data fetching.",
            "deliverables": ["src/schema/", "src/resolvers/", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["GraphQL", "Apollo", "DataLoader", "Subscriptions"],
        },
    ],
    "redis": [
        {
            "project": "Caching Layer with Redis",
            "description": "Implement a caching layer for an API with cache invalidation "
                           "strategies, session storage, and rate limiting.",
            "deliverables": ["cache.py", "rate_limiter.py", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["Redis", "Caching", "Rate limiting", "Session management"],
        },
    ],
    "kafka": [
        {
            "project": "Event-Driven Order Processing",
            "description": "Build an event-driven order pipeline with Kafka producers, "
                           "consumers, and dead letter queues.",
            "deliverables": ["producer/", "consumer/", "docker-compose.yml", "README.md"],
            "difficulty": "Advanced",
            "skills_demonstrated": ["Kafka", "Event-driven", "Error handling", "Docker"],
        },
    ],
    "mongodb": [
        {
            "project": "Blog Platform with MongoDB",
            "description": "Build a blog platform with MongoDB for content storage, "
                           "text search, aggregation pipelines, and indexing.",
            "deliverables": ["app/", "models/", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["MongoDB", "Aggregation", "Indexing", "Text search"],
        },
    ],
    "postgresql": [
        {
            "project": "Multi-Tenant SaaS Database",
            "description": "Design a PostgreSQL schema for a multi-tenant SaaS app "
                           "with row-level security, partitioning, and migrations.",
            "deliverables": ["migrations/", "schema.sql", "rls_policies.sql", "README.md"],
            "difficulty": "Advanced",
            "skills_demonstrated": ["PostgreSQL", "RLS", "Partitioning", "Migrations"],
        },
    ],
    "gcp": [
        {
            "project": "Cloud Run Microservice",
            "description": "Deploy a containerized service to Cloud Run with "
                           "Cloud SQL, Pub/Sub integration, and monitoring.",
            "deliverables": ["Dockerfile", "cloudbuild.yaml", "src/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": ["GCP", "Cloud Run", "Pub/Sub", "Cloud SQL"],
        },
    ],
    "git": [
        {
            "project": "Git Workflow Automation",
            "description": "Create Git hooks and scripts for automated versioning, "
                           "changelog generation, and branch management.",
            "deliverables": [".githooks/", "scripts/", "CHANGELOG.md", "README.md"],
            "difficulty": "Beginner",
            "skills_demonstrated": ["Git", "Automation", "Scripting", "Versioning"],
        },
    ],
}


class ProjectGenerator:
    """Generates personalized portfolio project ideas.

    Goes beyond static templates by considering the candidate's existing
    skills and target role to suggest the most impactful projects.
    """

    def generate(
        self,
        missing_skills: list[str],
        existing_skills: Optional[list[str]] = None,
        target_role: Optional[str] = None,
        max_projects_per_skill: int = 2,
    ) -> list[dict]:
        """Generate project ideas for missing skills.

        Args:
            missing_skills: Skills the candidate needs to learn.
            existing_skills: Skills the candidate already has (for personalization).
            target_role: Target job title for context.
            max_projects_per_skill: Maximum projects to suggest per skill.

        Returns:
            List of project dicts with skill, project, description, deliverables,
            difficulty, and skills_demonstrated.
        """
        if not missing_skills:
            return []

        logger.info("Generating projects for %d skills", len(missing_skills))
        existing = set(s.lower().strip() for s in (existing_skills or []))
        projects = []

        for skill in missing_skills:
            skill_lower = skill.lower().strip()
            catalog_projects = PROJECT_CATALOG.get(skill_lower, [])

            if catalog_projects:
                selected = catalog_projects[:max_projects_per_skill]
                for proj in selected:
                    entry = {
                        "skill": skill,
                        "project": proj["project"],
                        "description": proj["description"],
                        "deliverables": proj["deliverables"],
                        "difficulty": proj["difficulty"],
                        "skills_demonstrated": proj["skills_demonstrated"],
                        "estimated_weeks": self._estimate_weeks(proj["difficulty"]),
                    }

                    # Add personalization note if candidate has related skills
                    overlap = existing & set(
                        s.lower() for s in proj["skills_demonstrated"]
                    )
                    if overlap:
                        entry["leverage_existing"] = (
                            f"You can leverage your existing {', '.join(overlap)} "
                            f"experience for this project."
                        )

                    projects.append(entry)
            else:
                # Generate a generic project for unknown skills
                projects.append(self._generic_project(skill))

        logger.info("Generated %d project ideas", len(projects))
        return projects

    @staticmethod
    def _estimate_weeks(difficulty: str) -> int:
        """Estimate project duration based on difficulty."""
        return {"Beginner": 1, "Intermediate": 2, "Advanced": 3}.get(difficulty, 2)

    @staticmethod
    def _generic_project(skill: str) -> dict:
        """Generate a generic project for a skill not in the catalog."""
        return {
            "skill": skill,
            "project": f"Build a practical {skill} portfolio project",
            "description": (
                f"Create a hands-on project that demonstrates your {skill} "
                f"proficiency. Include documentation, tests, and a README "
                f"explaining your design decisions."
            ),
            "deliverables": ["src/", "tests/", "README.md"],
            "difficulty": "Intermediate",
            "skills_demonstrated": [skill],
            "estimated_weeks": 2,
        }

    def get_roadmap(
        self,
        missing_skills: list[str],
        existing_skills: Optional[list[str]] = None,
    ) -> dict:
        """Generate a project roadmap ordering projects by dependency and difficulty.

        Returns a dict with 'phases' (ordered list) and 'total_weeks' estimate.
        """
        projects = self.generate(missing_skills, existing_skills, max_projects_per_skill=1)

        if not projects:
            return {"phases": [], "total_weeks": 0}

        # Sort by difficulty: Beginner -> Intermediate -> Advanced
        difficulty_order = {"Beginner": 0, "Intermediate": 1, "Advanced": 2}
        projects.sort(key=lambda p: difficulty_order.get(p["difficulty"], 1))

        phases = []
        current_phase = []
        current_difficulty = None

        for proj in projects:
            if current_difficulty and proj["difficulty"] != current_difficulty:
                phases.append({
                    "difficulty": current_difficulty,
                    "projects": current_phase,
                })
                current_phase = []

            current_difficulty = proj["difficulty"]
            current_phase.append(proj)

        if current_phase:
            phases.append({
                "difficulty": current_difficulty,
                "projects": current_phase,
            })

        total_weeks = sum(p["estimated_weeks"] for p in projects)

        return {"phases": phases, "total_weeks": total_weeks}
