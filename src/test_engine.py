from src.engine.skill_gap_engine import SkillGapEngine

engine = SkillGapEngine()

result = engine.analyze(
    user_resume_text="I am a Python developer.",
    target_job_description="Looking for a backend engineer with Python experience."
)

print(result)