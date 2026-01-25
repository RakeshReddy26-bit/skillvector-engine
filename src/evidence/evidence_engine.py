class EvidenceEngine:
    """
    Converts a learning path into concrete, resume-ready evidence projects.
    """

    def generate(self, learning_path: list[dict]) -> list[dict]:
        """
        learning_path example:
        [
            {
                "skill": "Docker",
                "priority": "Medium",
                "estimated_weeks": 1
            }
        ]
        """

        evidence = []

        for step in learning_path:
            skill = step.get("skill", "")
            skill_name = skill.lower()
            weeks = step.get("estimated_weeks", 1)

            if skill_name == "docker":
                evidence.append({
                    "skill": "Docker",
                    "project": "Dockerize a FastAPI Application",
                    "deliverables": [
                        "Dockerfile",
                        "docker-compose.yml",
                        "README.md"
                    ],
                    "estimated_weeks": weeks
                })

            elif skill_name == "kubernetes":
                evidence.append({
                    "skill": "Kubernetes",
                    "project": "Deploy a Service to Kubernetes",
                    "deliverables": [
                        "deployment.yaml",
                        "service.yaml",
                        "README.md"
                    ],
                    "estimated_weeks": weeks
                })

            else:
                evidence.append({
                    "skill": skill,
                    "project": f"Build a practical project for {skill}",
                    "deliverables": ["README.md"],
                    "estimated_weeks": weeks
                })

        return evidence