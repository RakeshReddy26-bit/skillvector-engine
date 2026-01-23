class SkillGapEngine:
    """
    Core engine responsible for analyzing the gap between
    a user's resume and a target job description.
    """

    def __init__(self):
        pass

    def analyze(self, user_resume_text: str, target_job_description: str):
        if not user_resume_text or not user_resume_text.strip():
            raise ValueError("Resume text cannot be empty.")

        if not target_job_description or not target_job_description.strip():
            raise ValueError("Job description cannot be empty.")

        return {
            "status": "validated",
            "message": "Inputs are valid."
        }