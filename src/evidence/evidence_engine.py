import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class EvidenceEngine:
    """Converts a learning path into concrete, resume-ready evidence projects."""

    TEMPLATES: Dict[str, Dict] = {
        "docker": {
            "project": "Dockerize a FastAPI Application",
            "deliverables": ["Dockerfile", "docker-compose.yml", "README.md"],
            "description": "Create a production-ready Docker setup for a FastAPI service.",
        },
        "kubernetes": {
            "project": "Deploy a Service to Kubernetes",
            "deliverables": ["deployment.yaml", "service.yaml", "README.md"],
            "description": "Deploy a containerized application using Kubernetes manifests.",
        },
        "ci/cd": {
            "project": "Build a CI/CD Pipeline",
            "deliverables": [".github/workflows/ci.yml", "README.md"],
            "description": "Set up automated testing and deployment with GitHub Actions.",
        },
        "rest apis": {
            "project": "Build a RESTful API",
            "deliverables": ["app.py", "tests/", "README.md"],
            "description": "Design and implement a REST API with proper routing and validation.",
        },
        "terraform": {
            "project": "Infrastructure as Code with Terraform",
            "deliverables": ["main.tf", "variables.tf", "README.md"],
            "description": "Provision cloud infrastructure using Terraform modules.",
        },
    }

    def generate(self, learning_path: List[Dict]) -> List[Dict]:
        """Generate evidence projects for each skill in the learning path."""
        if not learning_path:
            return []

        logger.info("Generating evidence for %d skills", len(learning_path))
        evidence = []

        for step in learning_path:
            skill = step.get("skill", "")
            skill_lower = skill.lower().strip()
            weeks = step.get("estimated_weeks", 1)

            template = self.TEMPLATES.get(skill_lower)
            if template:
                evidence.append({
                    "skill": skill,
                    "project": template["project"],
                    "description": template["description"],
                    "deliverables": template["deliverables"],
                    "estimated_weeks": weeks,
                })
            else:
                evidence.append({
                    "skill": skill,
                    "project": f"Build a practical project for {skill}",
                    "description": f"Hands-on project demonstrating {skill} proficiency.",
                    "deliverables": ["README.md"],
                    "estimated_weeks": weeks,
                })

        return evidence
