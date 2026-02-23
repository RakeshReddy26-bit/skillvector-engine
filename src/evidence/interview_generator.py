"""Interview question generator for SkillVector Engine.

Generates targeted interview questions for each missing skill to help
candidates prepare for technical interviews.
"""

import json
import logging
from typing import Optional

from src.utils.errors import LLMError

logger = logging.getLogger(__name__)


# Fallback questions when LLM is unavailable
FALLBACK_QUESTIONS: dict[str, list[str]] = {
    "python": [
        "Explain the difference between a list and a tuple in Python.",
        "What are Python decorators and when would you use them?",
        "How does Python's garbage collector work?",
        "What is the GIL and how does it affect multithreading?",
        "Explain the difference between `deepcopy` and `copy`.",
    ],
    "docker": [
        "What is the difference between a Docker image and a container?",
        "How would you reduce the size of a Docker image?",
        "Explain multi-stage builds and when you'd use them.",
        "What is the difference between CMD and ENTRYPOINT?",
        "How do you handle persistent data in Docker?",
    ],
    "kubernetes": [
        "Explain the difference between a Deployment and a StatefulSet.",
        "How does Kubernetes service discovery work?",
        "What is the role of an Ingress controller?",
        "How would you debug a pod that keeps crashing?",
        "Explain the difference between a ConfigMap and a Secret.",
    ],
    "ci/cd": [
        "What are the key stages of a CI/CD pipeline?",
        "How would you handle secrets in a CI/CD pipeline?",
        "Explain the difference between continuous delivery and continuous deployment.",
        "How do you implement rollback strategies?",
        "What testing strategies do you include in a pipeline?",
    ],
    "rest apis": [
        "Explain the differences between PUT and PATCH.",
        "How do you version a REST API?",
        "What is HATEOAS and when is it useful?",
        "How do you handle pagination in a REST API?",
        "Explain idempotency and why it matters.",
    ],
    "sql": [
        "What is the difference between INNER JOIN and LEFT JOIN?",
        "Explain database normalization and when to denormalize.",
        "How do indexes work and when should you use them?",
        "What is a database transaction and what are ACID properties?",
        "How would you optimize a slow query?",
    ],
    "aws": [
        "Explain the difference between EC2, ECS, and Lambda.",
        "When would you use S3 vs EBS vs EFS?",
        "How does IAM role-based access control work?",
        "What is a VPC and how do you design one?",
        "Explain the shared responsibility model.",
    ],
    "microservices": [
        "What are the pros and cons of microservices vs monoliths?",
        "How do you handle inter-service communication?",
        "Explain the saga pattern for distributed transactions.",
        "How do you implement service discovery?",
        "What is the circuit breaker pattern?",
    ],
    "system design": [
        "How would you design a URL shortening service?",
        "Explain CAP theorem and its implications.",
        "How would you design a rate limiter?",
        "What strategies would you use for database scaling?",
        "How do you handle eventual consistency?",
    ],
    "terraform": [
        "What is the difference between Terraform state and plan?",
        "How do you manage Terraform state in a team?",
        "Explain Terraform modules and when to use them.",
        "What is the difference between count and for_each?",
        "How do you handle secrets in Terraform?",
    ],
    "react": [
        "Explain the React component lifecycle.",
        "What is the difference between useState and useReducer?",
        "How does React's reconciliation algorithm work?",
        "When would you use Context API vs Redux?",
        "Explain the purpose of useEffect cleanup functions.",
    ],
    "typescript": [
        "What are union types and intersection types?",
        "Explain the difference between interface and type.",
        "What are generics and when would you use them?",
        "How does TypeScript's type inference work?",
        "What are utility types like Partial, Required, and Pick?",
    ],
    "graphql": [
        "What are the differences between GraphQL and REST?",
        "How do you handle the N+1 query problem in GraphQL?",
        "Explain GraphQL subscriptions.",
        "What are resolvers and how do they work?",
        "How do you handle authentication in GraphQL?",
    ],
    "redis": [
        "What data structures does Redis support?",
        "Explain Redis persistence options (RDB vs AOF).",
        "How would you implement a distributed lock with Redis?",
        "What are Redis pub/sub use cases?",
        "How do you handle cache invalidation?",
    ],
    "kafka": [
        "Explain Kafka's architecture (brokers, topics, partitions).",
        "What is the difference between at-most-once and exactly-once delivery?",
        "How do consumer groups work?",
        "What is the role of ZooKeeper in Kafka?",
        "How would you handle message ordering?",
    ],
    "mongodb": [
        "When would you choose MongoDB over a relational database?",
        "Explain MongoDB's aggregation pipeline.",
        "What are the trade-offs of embedding vs referencing documents?",
        "How does sharding work in MongoDB?",
        "What are MongoDB indexes and how do they differ from SQL indexes?",
    ],
    "postgresql": [
        "What are PostgreSQL's advantages over MySQL?",
        "Explain JSONB support and when to use it.",
        "How do you optimize PostgreSQL query performance?",
        "What are CTEs and window functions?",
        "Explain PostgreSQL's MVCC concurrency model.",
    ],
    "gcp": [
        "What is the difference between Cloud Run and App Engine?",
        "How does BigQuery differ from Cloud SQL?",
        "Explain GCP's IAM hierarchy.",
        "When would you use Pub/Sub vs Cloud Tasks?",
        "How does Cloud Storage compare to AWS S3?",
    ],
    "azure": [
        "Explain the difference between Azure Functions and App Service.",
        "What is Azure DevOps and how does it compare to GitHub Actions?",
        "How does Azure Active Directory work?",
        "What is Cosmos DB and when would you use it?",
        "Explain Azure's resource group hierarchy.",
    ],
    "git": [
        "Explain the difference between merge and rebase.",
        "What is a Git stash and when would you use it?",
        "How do you resolve merge conflicts?",
        "Explain Git's branching strategies (GitFlow, trunk-based).",
        "What is the difference between reset and revert?",
    ],
}


class InterviewGenerator:
    """Generates interview preparation questions for missing skills.

    Uses LLM when available, falls back to curated question templates.
    """

    def __init__(self, use_llm: bool = False) -> None:
        self.use_llm = use_llm
        self._llm = None

    def _get_llm(self):
        """Lazy-load LLM only when needed."""
        if self._llm is None:
            try:
                from langchain_anthropic import ChatAnthropic
                self._llm = ChatAnthropic(temperature=0.3, model="claude-sonnet-4-20250514")
            except Exception as e:
                logger.warning("Could not initialize LLM for interview generation: %s", e)
                self._llm = None
        return self._llm

    def generate(
        self,
        missing_skills: list[str],
        questions_per_skill: int = 5,
        job_context: Optional[str] = None,
    ) -> list[dict]:
        """Generate interview questions for each missing skill.

        Args:
            missing_skills: List of skill names to generate questions for.
            questions_per_skill: Number of questions per skill.
            job_context: Optional job description for context-specific questions.

        Returns:
            List of dicts with 'skill', 'questions', and 'difficulty' keys.
        """
        if not missing_skills:
            return []

        logger.info("Generating interview questions for %d skills", len(missing_skills))
        results = []

        for skill in missing_skills:
            if self.use_llm:
                questions = self._generate_llm(skill, questions_per_skill, job_context)
            else:
                questions = self._generate_fallback(skill, questions_per_skill)

            results.append({
                "skill": skill,
                "questions": questions,
                "difficulty": self._estimate_difficulty(skill),
                "tips": self._get_tips(skill),
            })

        return results

    def _generate_llm(
        self,
        skill: str,
        count: int,
        job_context: Optional[str] = None,
    ) -> list[str]:
        """Generate questions using LLM."""
        llm = self._get_llm()
        if llm is None:
            return self._generate_fallback(skill, count)

        context_part = ""
        if job_context:
            context_part = f"\nJob context: {job_context}\n"

        prompt = (
            f"Generate {count} technical interview questions for a candidate "
            f"who needs to demonstrate knowledge of '{skill}'.{context_part}\n"
            f"Mix difficulty levels (easy, medium, hard).\n"
            f"Return a JSON array of strings. Only output the JSON array, nothing else."
        )

        try:
            response = llm.invoke(prompt)
            questions = json.loads(response.content)
            if isinstance(questions, list) and len(questions) > 0:
                return questions[:count]
        except (json.JSONDecodeError, TypeError, LLMError) as e:
            logger.warning("LLM interview generation failed for %s: %s", skill, e)
        except Exception as e:
            logger.warning("Unexpected error generating interview Qs for %s: %s", skill, e)

        return self._generate_fallback(skill, count)

    def _generate_fallback(self, skill: str, count: int) -> list[str]:
        """Generate questions from curated templates."""
        skill_lower = skill.lower().strip()
        questions = FALLBACK_QUESTIONS.get(skill_lower)

        if questions:
            return questions[:count]

        # Generic questions for unknown skills
        return [
            f"Explain the core concepts of {skill}.",
            f"Describe a project where you used {skill} effectively.",
            f"What are common challenges when working with {skill}?",
            f"How does {skill} compare to alternative technologies?",
            f"What best practices do you follow when using {skill}?",
        ][:count]

    @staticmethod
    def _estimate_difficulty(skill: str) -> str:
        """Estimate interview difficulty level for a skill."""
        advanced = {"system design", "microservices", "kubernetes", "kafka", "terraform"}
        intermediate = {"docker", "aws", "gcp", "azure", "ci/cd", "graphql", "redis"}

        if skill.lower().strip() in advanced:
            return "Advanced"
        elif skill.lower().strip() in intermediate:
            return "Intermediate"
        return "Foundational"

    @staticmethod
    def _get_tips(skill: str) -> list[str]:
        """Return preparation tips for a skill."""
        skill_lower = skill.lower().strip()

        tips_map = {
            "system design": [
                "Practice drawing architecture diagrams",
                "Learn to estimate scale (users, QPS, storage)",
                "Study real-world systems (e.g., how Twitter/Netflix work)",
            ],
            "microservices": [
                "Understand trade-offs vs monolithic architecture",
                "Study common patterns: saga, CQRS, event sourcing",
                "Be prepared to discuss service boundaries",
            ],
            "kubernetes": [
                "Set up a local cluster with minikube or kind",
                "Practice writing YAML manifests from scratch",
                "Understand networking: Services, Ingress, NetworkPolicies",
            ],
            "docker": [
                "Practice writing Dockerfiles without a reference",
                "Understand layers and caching",
                "Learn docker-compose for multi-container setups",
            ],
        }

        return tips_map.get(skill_lower, [
            f"Build a small project using {skill}",
            f"Read the official {skill} documentation",
            "Practice explaining concepts out loud",
        ])
