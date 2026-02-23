// SkillVector Engine — Full Prerequisite DAG (32 skills, 30 edges)
// Run with: cypher-shell < first_skill_graph.cypher
// Or seed programmatically via: python -m src.graph.seed_skills

// ── Create skill nodes (idempotent) ─────────────────────────────────────────

// Languages
MERGE (python:Skill {name: "Python"})       SET python.category = "language",      python.estimated_days = 7;
MERGE (js:Skill {name: "JavaScript"})        SET js.category = "language",          js.estimated_days = 7;
MERGE (java:Skill {name: "Java"})            SET java.category = "language",        java.estimated_days = 10;
MERGE (go:Skill {name: "Go"})                SET go.category = "language",          go.estimated_days = 10;
MERGE (ts:Skill {name: "TypeScript"})        SET ts.category = "language",          ts.estimated_days = 7;

// Data
MERGE (sql:Skill {name: "SQL"})              SET sql.category = "data",             sql.estimated_days = 5;
MERGE (pg:Skill {name: "PostgreSQL"})        SET pg.category = "data",              pg.estimated_days = 5;
MERGE (mongo:Skill {name: "MongoDB"})        SET mongo.category = "data",           mongo.estimated_days = 5;
MERGE (redis:Skill {name: "Redis"})          SET redis.category = "data",           redis.estimated_days = 4;
MERGE (kafka:Skill {name: "Kafka"})          SET kafka.category = "data",           kafka.estimated_days = 7;
MERGE (spark:Skill {name: "Spark"})          SET spark.category = "data",           spark.estimated_days = 10;
MERGE (airflow:Skill {name: "Airflow"})      SET airflow.category = "data",         airflow.estimated_days = 7;

// Tools
MERGE (git:Skill {name: "Git"})              SET git.category = "tool",             git.estimated_days = 3;

// Operations
MERGE (linux:Skill {name: "Linux"})          SET linux.category = "operations",     linux.estimated_days = 5;
MERGE (nginx:Skill {name: "Nginx"})          SET nginx.category = "operations",     nginx.estimated_days = 3;

// Frontend
MERGE (html:Skill {name: "HTML/CSS"})        SET html.category = "frontend",        html.estimated_days = 5;
MERGE (react:Skill {name: "React"})          SET react.category = "frontend",       react.estimated_days = 10;

// Runtimes / Frameworks
MERGE (node:Skill {name: "Node.js"})         SET node.category = "runtime",         node.estimated_days = 7;
MERGE (django:Skill {name: "Django"})        SET django.category = "framework",     django.estimated_days = 7;
MERGE (fastapi:Skill {name: "FastAPI"})      SET fastapi.category = "framework",    fastapi.estimated_days = 5;
MERGE (spring:Skill {name: "Spring Boot"})   SET spring.category = "framework",     spring.estimated_days = 10;

// Architecture
MERGE (rest:Skill {name: "REST APIs"})       SET rest.category = "architecture",    rest.estimated_days = 4;
MERGE (gql:Skill {name: "GraphQL"})          SET gql.category = "architecture",     gql.estimated_days = 5;
MERGE (micro:Skill {name: "Microservices"})  SET micro.category = "architecture",   micro.estimated_days = 10;
MERGE (sysdes:Skill {name: "System Design"}) SET sysdes.category = "architecture",  sysdes.estimated_days = 14;

// DevOps
MERGE (docker:Skill {name: "Docker"})        SET docker.category = "devops",        docker.estimated_days = 5;
MERGE (k8s:Skill {name: "Kubernetes"})       SET k8s.category = "devops",           k8s.estimated_days = 7;
MERGE (cicd:Skill {name: "CI/CD"})           SET cicd.category = "devops",          cicd.estimated_days = 5;
MERGE (tf:Skill {name: "Terraform"})         SET tf.category = "devops",            tf.estimated_days = 7;

// Cloud
MERGE (aws:Skill {name: "AWS"})              SET aws.category = "cloud",            aws.estimated_days = 10;
MERGE (gcp:Skill {name: "GCP"})              SET gcp.category = "cloud",            gcp.estimated_days = 10;
MERGE (azure:Skill {name: "Azure"})          SET azure.category = "cloud",          azure.estimated_days = 10;


// ── Create prerequisite edges (idempotent) ──────────────────────────────────

// Language -> Framework chains
MATCH (a:Skill {name: "JavaScript"}), (b:Skill {name: "TypeScript"})   MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "JavaScript"}), (b:Skill {name: "React"})        MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "JavaScript"}), (b:Skill {name: "Node.js"})      MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "HTML/CSS"}),    (b:Skill {name: "React"})        MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Python"}),      (b:Skill {name: "Django"})       MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Python"}),      (b:Skill {name: "FastAPI"})      MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Java"}),        (b:Skill {name: "Spring Boot"})  MERGE (a)-[:PREREQUISITE_OF]->(b);

// SQL -> Database chains
MATCH (a:Skill {name: "SQL"}), (b:Skill {name: "PostgreSQL"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "SQL"}), (b:Skill {name: "MongoDB"})    MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "SQL"}), (b:Skill {name: "Redis"})      MERGE (a)-[:PREREQUISITE_OF]->(b);

// API layer
MATCH (a:Skill {name: "REST APIs"}), (b:Skill {name: "FastAPI"})       MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "REST APIs"}), (b:Skill {name: "GraphQL"})       MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "REST APIs"}), (b:Skill {name: "Microservices"}) MERGE (a)-[:PREREQUISITE_OF]->(b);

// Linux -> Infrastructure
MATCH (a:Skill {name: "Linux"}), (b:Skill {name: "Docker"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Linux"}), (b:Skill {name: "AWS"})    MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Linux"}), (b:Skill {name: "GCP"})    MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Linux"}), (b:Skill {name: "Azure"})  MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Linux"}), (b:Skill {name: "Nginx"})  MERGE (a)-[:PREREQUISITE_OF]->(b);

// DevOps chains
MATCH (a:Skill {name: "Docker"}), (b:Skill {name: "Kubernetes"})   MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Docker"}), (b:Skill {name: "CI/CD"})        MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Docker"}), (b:Skill {name: "Microservices"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Git"}),    (b:Skill {name: "CI/CD"})        MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "AWS"}),    (b:Skill {name: "Terraform"})    MERGE (a)-[:PREREQUISITE_OF]->(b);

// Data engineering
MATCH (a:Skill {name: "Python"}), (b:Skill {name: "Spark"})   MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "SQL"}),    (b:Skill {name: "Spark"})   MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Python"}), (b:Skill {name: "Airflow"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "SQL"}),    (b:Skill {name: "Airflow"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "Python"}), (b:Skill {name: "Kafka"})   MERGE (a)-[:PREREQUISITE_OF]->(b);

// Advanced patterns
MATCH (a:Skill {name: "Microservices"}), (b:Skill {name: "System Design"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
MATCH (a:Skill {name: "SQL"}),           (b:Skill {name: "System Design"}) MERGE (a)-[:PREREQUISITE_OF]->(b);
