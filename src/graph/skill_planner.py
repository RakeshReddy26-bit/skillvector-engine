class SkillPlanner:
    """
    Orders missing skills into a learning path.
    Neo4j integration can be added later.
    This version is STABLE and deterministic.
    """

    def plan(self, missing_skills: list[str]) -> list[dict]:
        """
        Input:
            ["Kubernetes", "cloud-native experience"]

        Output:
            [
                {"skill": "Kubernetes", "estimated_weeks": 2},
                {"skill": "cloud-native experience", "estimated_weeks": 2}
            ]
        """

        learning_path = []

        for skill in missing_skills:
            learning_path.append({
                "skill": skill,
                "estimated_weeks": 2
            })

        return learning_path