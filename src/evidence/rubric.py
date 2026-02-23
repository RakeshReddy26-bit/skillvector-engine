"""Evaluation rubric engine for SkillVector Engine.

Generates assessment criteria for portfolio projects so candidates
know exactly what constitutes a strong demonstration of each skill.
"""

import logging

logger = logging.getLogger(__name__)


# Rubric templates per skill, each with criteria and levels
RUBRIC_CATALOG: dict[str, dict] = {
    "python": {
        "criteria": [
            {
                "name": "Code Quality",
                "weight": 25,
                "levels": {
                    "Excellent": "Clean, idiomatic Python following PEP 8. Uses type hints, "
                                 "meaningful variable names, and appropriate data structures.",
                    "Good": "Readable code with minor style inconsistencies. Some type hints.",
                    "Needs Work": "Functional but hard to read. No type hints or documentation.",
                },
            },
            {
                "name": "Testing",
                "weight": 25,
                "levels": {
                    "Excellent": "Comprehensive test suite with unit and integration tests. "
                                 "Edge cases covered. Uses pytest fixtures and parametrize.",
                    "Good": "Tests for main functionality. Some edge cases covered.",
                    "Needs Work": "Few or no tests. No edge case coverage.",
                },
            },
            {
                "name": "Architecture",
                "weight": 25,
                "levels": {
                    "Excellent": "Well-structured with clear separation of concerns. "
                                 "Uses appropriate design patterns. Easy to extend.",
                    "Good": "Reasonable structure with some modularity.",
                    "Needs Work": "Monolithic code with mixed concerns.",
                },
            },
            {
                "name": "Documentation",
                "weight": 25,
                "levels": {
                    "Excellent": "Clear README with setup instructions, usage examples, "
                                 "and architecture overview. Docstrings on public APIs.",
                    "Good": "README with basic setup steps. Some docstrings.",
                    "Needs Work": "Minimal or no documentation.",
                },
            },
        ],
    },
    "docker": {
        "criteria": [
            {
                "name": "Dockerfile Quality",
                "weight": 30,
                "levels": {
                    "Excellent": "Multi-stage build, minimal image size, non-root user, "
                                 "proper layer caching, .dockerignore configured.",
                    "Good": "Working Dockerfile with reasonable layer ordering.",
                    "Needs Work": "Large image, no caching optimization, runs as root.",
                },
            },
            {
                "name": "Compose Setup",
                "weight": 25,
                "levels": {
                    "Excellent": "Services properly isolated, health checks, named volumes, "
                                 "networks configured, environment variables externalized.",
                    "Good": "Working compose file with multiple services.",
                    "Needs Work": "Hardcoded values, no health checks.",
                },
            },
            {
                "name": "Security",
                "weight": 25,
                "levels": {
                    "Excellent": "Non-root user, secrets management, minimal base image, "
                                 "no sensitive data in image layers.",
                    "Good": "Some security considerations addressed.",
                    "Needs Work": "Runs as root, secrets in Dockerfile.",
                },
            },
            {
                "name": "Documentation",
                "weight": 20,
                "levels": {
                    "Excellent": "README with build/run instructions, architecture diagram, "
                                 "environment variable documentation.",
                    "Good": "Basic build and run instructions.",
                    "Needs Work": "No documentation.",
                },
            },
        ],
    },
    "kubernetes": {
        "criteria": [
            {
                "name": "Manifest Quality",
                "weight": 30,
                "levels": {
                    "Excellent": "Proper resource limits, liveness/readiness probes, "
                                 "pod disruption budgets, security contexts.",
                    "Good": "Working manifests with health checks.",
                    "Needs Work": "Minimal manifests without health checks or limits.",
                },
            },
            {
                "name": "Scaling & Resilience",
                "weight": 25,
                "levels": {
                    "Excellent": "HPA configured, pod anti-affinity, rolling update strategy, "
                                 "resource requests/limits properly tuned.",
                    "Good": "Basic HPA or replica count.",
                    "Needs Work": "Single replica, no scaling consideration.",
                },
            },
            {
                "name": "Configuration Management",
                "weight": 25,
                "levels": {
                    "Excellent": "ConfigMaps and Secrets properly used, Helm chart or "
                                 "Kustomize for environment management.",
                    "Good": "ConfigMaps used for basic configuration.",
                    "Needs Work": "Hardcoded configuration values.",
                },
            },
            {
                "name": "Networking",
                "weight": 20,
                "levels": {
                    "Excellent": "Ingress configured, NetworkPolicies defined, "
                                 "service mesh considerations.",
                    "Good": "Services and Ingress configured.",
                    "Needs Work": "Only ClusterIP services.",
                },
            },
        ],
    },
    "ci/cd": {
        "criteria": [
            {
                "name": "Pipeline Design",
                "weight": 30,
                "levels": {
                    "Excellent": "Multi-stage pipeline with lint, test, build, deploy stages. "
                                 "Proper parallelization and caching.",
                    "Good": "Pipeline with test and build stages.",
                    "Needs Work": "Single-stage or manual deployment.",
                },
            },
            {
                "name": "Testing Integration",
                "weight": 25,
                "levels": {
                    "Excellent": "Unit, integration, and e2e tests. Coverage reports. "
                                 "Fail-fast on test failures.",
                    "Good": "Automated tests run in pipeline.",
                    "Needs Work": "No tests in pipeline.",
                },
            },
            {
                "name": "Security",
                "weight": 25,
                "levels": {
                    "Excellent": "Secrets in vault/encrypted, dependency scanning, "
                                 "container image scanning, SAST.",
                    "Good": "Secrets stored in CI variables.",
                    "Needs Work": "Secrets hardcoded or in plain text.",
                },
            },
            {
                "name": "Deployment Strategy",
                "weight": 20,
                "levels": {
                    "Excellent": "Blue-green or canary deployment, rollback capability, "
                                 "environment promotion pipeline.",
                    "Good": "Automated deployment to one environment.",
                    "Needs Work": "Manual deployment steps.",
                },
            },
        ],
    },
    "rest apis": {
        "criteria": [
            {
                "name": "API Design",
                "weight": 30,
                "levels": {
                    "Excellent": "RESTful conventions followed, proper status codes, "
                                 "versioning, HATEOAS links, pagination.",
                    "Good": "Proper HTTP methods and status codes.",
                    "Needs Work": "Inconsistent patterns, wrong HTTP methods.",
                },
            },
            {
                "name": "Validation & Error Handling",
                "weight": 25,
                "levels": {
                    "Excellent": "Request validation, consistent error format, "
                                 "proper error codes, input sanitization.",
                    "Good": "Basic validation and error responses.",
                    "Needs Work": "No validation, generic error messages.",
                },
            },
            {
                "name": "Authentication & Authorization",
                "weight": 25,
                "levels": {
                    "Excellent": "JWT or OAuth2, role-based access control, "
                                 "rate limiting, CORS properly configured.",
                    "Good": "Basic authentication implemented.",
                    "Needs Work": "No authentication.",
                },
            },
            {
                "name": "Documentation",
                "weight": 20,
                "levels": {
                    "Excellent": "OpenAPI/Swagger docs, example requests/responses, "
                                 "Postman collection.",
                    "Good": "README with endpoint documentation.",
                    "Needs Work": "No API documentation.",
                },
            },
        ],
    },
    "microservices": {
        "criteria": [
            {
                "name": "Service Design",
                "weight": 30,
                "levels": {
                    "Excellent": "Clear bounded contexts, well-defined APIs between services, "
                                 "single responsibility per service.",
                    "Good": "Logical service separation with defined interfaces.",
                    "Needs Work": "Distributed monolith with tight coupling.",
                },
            },
            {
                "name": "Communication Patterns",
                "weight": 25,
                "levels": {
                    "Excellent": "Async messaging for events, sync for queries. "
                                 "Circuit breakers, retries, timeouts.",
                    "Good": "Mix of sync and async communication.",
                    "Needs Work": "Only synchronous HTTP calls.",
                },
            },
            {
                "name": "Data Management",
                "weight": 25,
                "levels": {
                    "Excellent": "Database per service, saga pattern for transactions, "
                                 "eventual consistency handled.",
                    "Good": "Separate databases with some coordination.",
                    "Needs Work": "Shared database across services.",
                },
            },
            {
                "name": "Observability",
                "weight": 20,
                "levels": {
                    "Excellent": "Distributed tracing, centralized logging, "
                                 "health checks, metrics dashboards.",
                    "Good": "Basic logging and health endpoints.",
                    "Needs Work": "No observability tooling.",
                },
            },
        ],
    },
    "system design": {
        "criteria": [
            {
                "name": "Requirements Analysis",
                "weight": 20,
                "levels": {
                    "Excellent": "Clear functional and non-functional requirements, "
                                 "capacity estimation, constraints identified.",
                    "Good": "Functional requirements addressed.",
                    "Needs Work": "Vague or missing requirements.",
                },
            },
            {
                "name": "Architecture",
                "weight": 30,
                "levels": {
                    "Excellent": "Well-reasoned component design, clear data flow, "
                                 "trade-offs documented, alternatives considered.",
                    "Good": "Reasonable architecture with main components.",
                    "Needs Work": "Unclear or incomplete architecture.",
                },
            },
            {
                "name": "Scalability",
                "weight": 25,
                "levels": {
                    "Excellent": "Horizontal scaling strategy, caching layers, "
                                 "database sharding, CDN usage, load balancing.",
                    "Good": "Some scaling considerations addressed.",
                    "Needs Work": "No scaling strategy.",
                },
            },
            {
                "name": "Trade-off Analysis",
                "weight": 25,
                "levels": {
                    "Excellent": "CAP theorem applied, consistency vs availability discussed, "
                                 "cost-performance trade-offs analyzed.",
                    "Good": "Some trade-offs mentioned.",
                    "Needs Work": "No trade-off discussion.",
                },
            },
        ],
    },
}


class RubricEngine:
    """Generates evaluation rubrics for portfolio projects.

    Provides structured criteria so candidates know exactly what
    constitutes a strong demonstration of each skill.
    """

    def generate(
        self,
        missing_skills: list[str],
        project_context: list[dict] | None = None,
    ) -> list[dict]:
        """Generate rubrics for each missing skill.

        Args:
            missing_skills: List of skill names.
            project_context: Optional list of project dicts (from EvidenceEngine)
                to provide project-specific criteria.

        Returns:
            List of rubric dicts with 'skill', 'criteria', and 'scoring' keys.
        """
        if not missing_skills:
            return []

        logger.info("Generating rubrics for %d skills", len(missing_skills))
        rubrics = []

        for skill in missing_skills:
            skill_lower = skill.lower().strip()
            catalog_rubric = RUBRIC_CATALOG.get(skill_lower)

            if catalog_rubric:
                rubric = {
                    "skill": skill,
                    "criteria": catalog_rubric["criteria"],
                    "scoring": self._scoring_guide(),
                    "total_points": 100,
                }
            else:
                rubric = {
                    "skill": skill,
                    "criteria": self._generic_criteria(skill),
                    "scoring": self._scoring_guide(),
                    "total_points": 100,
                }

            rubrics.append(rubric)

        return rubrics

    def evaluate_checklist(self, skill: str) -> list[dict]:
        """Generate a pass/fail checklist for quick self-assessment.

        Returns a list of checklist items with 'item' and 'category' keys.
        """
        skill_lower = skill.lower().strip()
        catalog_rubric = RUBRIC_CATALOG.get(skill_lower)

        if not catalog_rubric:
            return self._generic_checklist(skill)

        checklist = []
        for criterion in catalog_rubric["criteria"]:
            excellent = criterion["levels"]["Excellent"]
            items = [s.strip().rstrip(".") for s in excellent.split(",")]
            for item in items:
                if item:
                    checklist.append({
                        "item": item,
                        "category": criterion["name"],
                    })

        return checklist

    @staticmethod
    def _scoring_guide() -> dict:
        """Return standard scoring guide."""
        return {
            "Excellent": {"range": "90-100", "description": "Exceeds expectations"},
            "Good": {"range": "70-89", "description": "Meets expectations"},
            "Needs Work": {"range": "0-69", "description": "Below expectations"},
        }

    @staticmethod
    def _generic_criteria(skill: str) -> list[dict]:
        """Generate generic rubric criteria for unknown skills."""
        return [
            {
                "name": "Technical Implementation",
                "weight": 30,
                "levels": {
                    "Excellent": f"Demonstrates deep understanding of {skill}. "
                                 f"Uses best practices and advanced features.",
                    "Good": f"Working implementation using {skill} correctly.",
                    "Needs Work": f"Basic or incorrect use of {skill}.",
                },
            },
            {
                "name": "Code Quality",
                "weight": 25,
                "levels": {
                    "Excellent": "Clean, well-structured code with tests and documentation.",
                    "Good": "Readable code with some tests.",
                    "Needs Work": "Messy code without tests.",
                },
            },
            {
                "name": "Problem Solving",
                "weight": 25,
                "levels": {
                    "Excellent": "Elegant solution addressing edge cases and error scenarios.",
                    "Good": "Functional solution for the main use case.",
                    "Needs Work": "Incomplete or fragile solution.",
                },
            },
            {
                "name": "Documentation",
                "weight": 20,
                "levels": {
                    "Excellent": "Clear README, setup instructions, design decisions explained.",
                    "Good": "Basic README with setup instructions.",
                    "Needs Work": "No documentation.",
                },
            },
        ]

    @staticmethod
    def _generic_checklist(skill: str) -> list[dict]:
        """Generate generic checklist for unknown skills."""
        return [
            {"item": f"Project demonstrates practical use of {skill}", "category": "Technical"},
            {"item": "Code follows best practices and conventions", "category": "Quality"},
            {"item": "Tests cover main functionality", "category": "Testing"},
            {"item": "README explains how to run the project", "category": "Documentation"},
            {"item": "Error handling is implemented", "category": "Reliability"},
            {"item": "Code is version controlled with meaningful commits", "category": "Process"},
        ]
