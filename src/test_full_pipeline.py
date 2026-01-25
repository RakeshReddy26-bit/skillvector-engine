from src.pipeline.full_pipeline import SkillVectorPipeline


def test_full_pipeline():
    resume = """
    Backend Engineer with experience in Python, FastAPI, Docker.
    Built APIs and worked with relational databases.
    """

    target_job = "Senior Backend Engineer with Kubernetes and cloud-native experience"

    pipeline = SkillVectorPipeline()
    result = pipeline.run(resume, target_job)

    print("\n===== SKILLVECTOR FULL PIPELINE OUTPUT =====\n")

    print(f"Match Score: {result['match_score']}")
    print(f"Learning Priority: {result['learning_priority']}")
    print("\nMissing Skills:")
    for skill in result["missing_skills"]:
        print(f"- {skill}")

    print("\nOrdered Learning Path:")
    for step in result["learning_path"]:
        print(f"- {step['skill']} ({step['estimated_weeks']} week(s))")

    print("\nEvidence Plan:")
    for item in result["evidence"]:
        print(
            f"- {item['skill']}: {item['project']} "
            f"({item['estimated_weeks']} week(s))"
        )


if __name__ == "__main__":
    test_full_pipeline()