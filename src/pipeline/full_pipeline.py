from src.engine.skill_gap_engine import SkillGapEngine
from src.graph.skill_planner import SkillPlanner
from src.evidence.evidence_engine import EvidenceEngine


class SkillVectorPipeline:
    def __init__(self):
        self.skill_engine = SkillGapEngine()
        self.skill_planner = SkillPlanner()
        self.evidence_engine = EvidenceEngine()

    def run(self, resume: str, target_job: str) -> dict:
        # 1️⃣ Skill gap analysis
        gap_result = self.skill_engine.analyze(resume, target_job)

        match_score = gap_result["match_score"]
        missing_skills = gap_result["missing_skills"]

        # 2️⃣ Priority logic (simple + deterministic)
        if match_score < 50:
            learning_priority = "High"
        elif match_score < 75:
            learning_priority = "Medium"
        else:
            learning_priority = "Low"

        # 3️⃣ Learning path planning
        learning_path = self.skill_planner.plan(missing_skills)

        # 4️⃣ Evidence generation
        evidence = self.evidence_engine.generate(learning_path)

        # ✅ FINAL, CONTRACT-LOCKED OUTPUT
        return {
            "match_score": match_score,
            "learning_priority": learning_priority,
            "missing_skills": missing_skills,
            "learning_path": learning_path,
            "evidence": evidence,
        }