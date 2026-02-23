# src/graph/evidence_catalog.py
"""Evidence catalog mapping skills to portfolio projects and interview topics.

Covers all 32 skills in the prerequisite DAG (seed_skills.py).
"""

EVIDENCE_CATALOG = {
    # ── Languages ────────────────────────────────────────────────────────────
    "Python": {
        "reason": "Foundation for backend systems, data engineering, and tooling",
        "evidence": ["python-api-project", "python-interview"],
        "estimated_time_days": 7,
    },
    "JavaScript": {
        "reason": "Core language for frontend and full-stack development",
        "evidence": ["js-interactive-app", "javascript-interview"],
        "estimated_time_days": 7,
    },
    "Java": {
        "reason": "Enterprise backend and Android development",
        "evidence": ["java-crud-service", "java-interview"],
        "estimated_time_days": 10,
    },
    "Go": {
        "reason": "High-performance systems and cloud-native tooling",
        "evidence": ["go-cli-tool", "go-interview"],
        "estimated_time_days": 10,
    },
    "TypeScript": {
        "reason": "Type-safe JavaScript for production applications",
        "evidence": ["ts-fullstack-app", "typescript-interview"],
        "estimated_time_days": 7,
    },
    # ── Data ─────────────────────────────────────────────────────────────────
    "SQL": {
        "reason": "Foundation for all relational data work",
        "evidence": ["sql-analytics-queries", "sql-interview"],
        "estimated_time_days": 5,
    },
    "PostgreSQL": {
        "reason": "Production relational database management",
        "evidence": ["postgres-schema-design", "postgresql-interview"],
        "estimated_time_days": 5,
    },
    "MongoDB": {
        "reason": "Document-oriented NoSQL data modeling",
        "evidence": ["mongo-aggregation-pipeline", "mongodb-interview"],
        "estimated_time_days": 5,
    },
    "Redis": {
        "reason": "In-memory caching and real-time data structures",
        "evidence": ["redis-caching-layer", "redis-interview"],
        "estimated_time_days": 4,
    },
    "Kafka": {
        "reason": "Distributed event streaming for data pipelines",
        "evidence": ["kafka-producer-consumer", "kafka-interview"],
        "estimated_time_days": 7,
    },
    "Spark": {
        "reason": "Large-scale data processing and analytics",
        "evidence": ["spark-etl-pipeline", "spark-interview"],
        "estimated_time_days": 10,
    },
    "Airflow": {
        "reason": "Workflow orchestration for data pipelines",
        "evidence": ["airflow-dag-project", "airflow-interview"],
        "estimated_time_days": 7,
    },
    # ── Tools ────────────────────────────────────────────────────────────────
    "Git": {
        "reason": "Version control for all software projects",
        "evidence": ["git-workflow-demo", "git-interview"],
        "estimated_time_days": 3,
    },
    # ── Operations ───────────────────────────────────────────────────────────
    "Linux": {
        "reason": "Server administration and infrastructure foundation",
        "evidence": ["linux-server-setup", "linux-interview"],
        "estimated_time_days": 5,
    },
    "Nginx": {
        "reason": "Reverse proxy and web server configuration",
        "evidence": ["nginx-load-balancer", "nginx-interview"],
        "estimated_time_days": 3,
    },
    # ── Frontend ─────────────────────────────────────────────────────────────
    "HTML/CSS": {
        "reason": "Web page structure and styling fundamentals",
        "evidence": ["responsive-landing-page", "html-css-interview"],
        "estimated_time_days": 5,
    },
    "React": {
        "reason": "Component-based frontend application development",
        "evidence": ["react-dashboard-app", "react-interview"],
        "estimated_time_days": 10,
    },
    # ── Runtimes / Frameworks ────────────────────────────────────────────────
    "Node.js": {
        "reason": "Server-side JavaScript runtime for APIs and tooling",
        "evidence": ["node-rest-api", "nodejs-interview"],
        "estimated_time_days": 7,
    },
    "Django": {
        "reason": "Full-featured Python web framework",
        "evidence": ["django-web-app", "django-interview"],
        "estimated_time_days": 7,
    },
    "FastAPI": {
        "reason": "Modern async Python API framework",
        "evidence": ["fastapi-microservice", "fastapi-interview"],
        "estimated_time_days": 5,
    },
    "Spring Boot": {
        "reason": "Enterprise Java application framework",
        "evidence": ["spring-boot-api", "spring-boot-interview"],
        "estimated_time_days": 10,
    },
    # ── Architecture ─────────────────────────────────────────────────────────
    "REST APIs": {
        "reason": "Standard interface design for web services",
        "evidence": ["rest-api-design-project", "rest-api-interview"],
        "estimated_time_days": 4,
    },
    "GraphQL": {
        "reason": "Flexible query language for API consumers",
        "evidence": ["graphql-api-project", "graphql-interview"],
        "estimated_time_days": 5,
    },
    "Microservices": {
        "reason": "Distributed system architecture patterns",
        "evidence": ["microservices-demo", "microservices-interview"],
        "estimated_time_days": 10,
    },
    "System Design": {
        "reason": "End-to-end architecture for scalable systems",
        "evidence": ["system-design-document", "system-design-interview"],
        "estimated_time_days": 14,
    },
    # ── DevOps ───────────────────────────────────────────────────────────────
    "Docker": {
        "reason": "Container packaging for consistent deployments",
        "evidence": ["dockerized-api-project", "docker-debugging-interview"],
        "estimated_time_days": 5,
    },
    "Kubernetes": {
        "reason": "Production-grade container orchestration",
        "evidence": ["k8s-deployment-project", "kubernetes-interview"],
        "estimated_time_days": 7,
    },
    "CI/CD": {
        "reason": "Automated build, test, and deployment pipelines",
        "evidence": ["cicd-pipeline-project", "cicd-interview"],
        "estimated_time_days": 5,
    },
    "Terraform": {
        "reason": "Infrastructure as code for cloud provisioning",
        "evidence": ["terraform-infra-project", "terraform-interview"],
        "estimated_time_days": 7,
    },
    # ── Cloud ────────────────────────────────────────────────────────────────
    "AWS": {
        "reason": "Cloud infrastructure and managed services",
        "evidence": ["aws-serverless-project", "aws-interview"],
        "estimated_time_days": 10,
    },
    "GCP": {
        "reason": "Google Cloud platform services and tooling",
        "evidence": ["gcp-cloud-functions", "gcp-interview"],
        "estimated_time_days": 10,
    },
    "Azure": {
        "reason": "Microsoft cloud platform and enterprise services",
        "evidence": ["azure-webapp-project", "azure-interview"],
        "estimated_time_days": 10,
    },
}
