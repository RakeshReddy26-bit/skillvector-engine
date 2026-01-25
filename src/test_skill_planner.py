from src.graph.skill_planner import SkillPlanner


def test_skill_planner():
    planner = SkillPlanner()

    missing_skills = ["Python", "Docker", "Kubernetes"]

    ordered = planner.order_skills(missing_skills)

    print("\nOrdered Skills:")
    for skill in ordered:
        print("-", skill)


if __name__ == "__main__":
    test_skill_planner()