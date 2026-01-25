class JobRetriever:
    def retrieve(self, job_text: str) -> list[dict]:
        """
        Mock retriever (Phase 3).
        Later replace with vector DB.
        """

        return [
            {
                "chunk": "Kubernetes and cloud-native deployment experience is highly valued."
            },
            {
                "chunk": "Hands-on container orchestration projects improve hiring outcomes."
            }
        ]