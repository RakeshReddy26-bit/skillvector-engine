# src/evidence/project_templates.py

PROJECT_TEMPLATES = {
    "Docker": {
        "title": "Dockerize a FastAPI Application",
        "description": (
            "Create a production-ready Docker setup for a FastAPI service "
            "including environment configuration and health checks."
        ),
        "deliverables": [
            "Dockerfile",
            "docker-compose.yml",
            "README.md"
        ],
        "learning_outcomes": [
            "Understand Docker images and containers",
            "Write efficient Dockerfiles",
            "Run multi-service apps with docker-compose"
        ],
        "estimated_weeks": 1
    },
    "Kubernetes": {
        "title": "Deploy a Service to Kubernetes",
        "description": (
            "Deploy a containerized FastAPI application to Kubernetes "
            "using manifests for Deployment and Service."
        ),
        "deliverables": [
            "deployment.yaml",
            "service.yaml",
            "README.md"
        ],
        "learning_outcomes": [
            "Understand Kubernetes pods and services",
            "Write deployment manifests",
            "Expose services correctly"
        ],
        "estimated_weeks": 2
    }
}