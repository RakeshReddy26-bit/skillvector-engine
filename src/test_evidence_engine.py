# src/test_evidence_engine.py

from src.evidence.evidence_engine import EvidenceEngine


def test_evidence_engine():
    engine = EvidenceEngine()

    skills = ["Docker", "Kubernetes"]
    evidence = engine.generate_project_evidence(skills)

    print("\nGenerated Evidence:\n")

    for e in evidence:
        print(f"Skill: {e['skill']}")
        print(f"Project: {e['title']}")
        print(f"Deliverables: {', '.join(e['deliverables'])}")
        print(f"Estimated Time: {e['estimated_weeks']} week(s)")
        print("-" * 40)


if __name__ == "__main__":
    test_evidence_engine()