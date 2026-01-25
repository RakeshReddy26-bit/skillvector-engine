class RAGEngine:
    def __init__(self, retriever):
        self.retriever = retriever

    def analyze(self, job_text: str) -> str:
        """
        Returns contextual job market insights for a job description.
        """

        documents = self.retriever.retrieve(job_text)

        if not documents:
            return "No external job market context found."

        context = "\n\n".join(
            f"- {doc['chunk']}" for doc in documents
        )

        return context