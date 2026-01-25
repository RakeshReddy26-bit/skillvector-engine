# src/graph/evidence_catalog.py

EVIDENCE_CATALOG = {
    "Python": {
        "reason": "Foundation for backend systems and tooling",
        "evidence": [
            "python-api-project",
            "python-interview"
        ],
        "estimated_time_days": 7,
    },
    "Docker": {
        "reason": "Required before container orchestration",
        "evidence": [
            "dockerized-api-project",
            "docker-debugging-interview"
        ],
        "estimated_time_days": 5,
    },
    "Kubernetes": {
        "reason": "Production-grade container orchestration",
        "evidence": [
            "k8s-deployment-project",
            "kubernetes-interview"
        ],
        "estimated_time_days": 7,
    },
}