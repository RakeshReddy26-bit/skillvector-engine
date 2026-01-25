from src.graph.skill_planner import SkillPlanner


def test_learning_path():
    planner = SkillPlanner()

    missing_skills = ["Python", "Docker", "Kubernetes"]
    path = planner.build_learning_path(missing_skills)

    print("\nGenerated Learning Path:\n")

    for step in path:
        days = step["estimated_time_days"]
        weeks = round(days / 7, 1)

        print(f"- {step['skill']} (~{weeks} week(s))")
        print(f"  Reason: {step['reason']}")
        print(f"  Prerequisites: {step['prerequisites']}")
        print(f"  Evidence: {step['evidence']}")
        print()