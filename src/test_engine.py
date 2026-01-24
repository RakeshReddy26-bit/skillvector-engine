from dotenv import load_dotenv
load_dotenv()  # 🔥 THIS LINE IS THE KEY

from src.engine.skill_gap_engine import SkillGapEngine

engine = SkillGapEngine()

result = engine.analyze(
    user_resume_text="I am a Python backend developer with Django experience.",
    target_job_description="Looking for a backend engineer with Python, Docker, and REST API experience."
)

print(result)