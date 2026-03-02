from dotenv import load_dotenv
load_dotenv()
import os
from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
pwd = os.getenv("NEO4J_PASSWORD")

SKILLS = [
    {"name": "Python", "level": 1, "category": "Programming"},
    {"name": "SQL", "level": 1, "category": "Data"},
    {"name": "Statistics", "level": 1, "category": "Data Science"},
    {"name": "Git", "level": 1, "category": "DevOps"},
    {"name": "Docker", "level": 2, "category": "DevOps"},
    {"name": "FastAPI", "level": 2, "category": "Backend"},
    {"name": "Pandas", "level": 2, "category": "Data"},
    {"name": "Scikit-learn", "level": 2, "category": "ML"},
    {"name": "PyTorch", "level": 3, "category": "Deep Learning"},
    {"name": "TensorFlow", "level": 3, "category": "Deep Learning"},
    {"name": "MLOps", "level": 3, "category": "ML Engineering"},
    {"name": "Kubeflow", "level": 4, "category": "ML Engineering"},
    {"name": "LLMOps", "level": 4, "category": "AI Engineering"},
    {"name": "RAG", "level": 3, "category": "AI Engineering"},
    {"name": "RLHF", "level": 5, "category": "AI Research"},
    {"name": "Feature Stores", "level": 4, "category": "ML Engineering"},
    {"name": "Distributed Systems", "level": 4, "category": "Systems"},
    {"name": "System Design", "level": 4, "category": "Architecture"},
    {"name": "Spark", "level": 3, "category": "Data Engineering"},
    {"name": "Kafka", "level": 4, "category": "Data Engineering"},
    {"name": "Ray", "level": 4, "category": "Distributed ML"},
    {"name": "Embeddings", "level": 3, "category": "AI Engineering"},
    {"name": "Pinecone", "level": 3, "category": "AI Engineering"},
    {"name": "LangChain", "level": 3, "category": "AI Engineering"},
    {"name": "Prompt Engineering", "level": 2, "category": "AI Engineering"},
]

PREREQUISITES = [
    ("Python", "FastAPI"),
    ("Python", "Pandas"),
    ("Python", "Scikit-learn"),
    ("Python", "MLOps"),
    ("Python", "Prompt Engineering"),
    ("Git", "Docker"),
    ("Docker", "MLOps"),
    ("Docker", "Kubeflow"),
    ("MLOps", "Kubeflow"),
    ("MLOps", "Feature Stores"),
    ("MLOps", "LLMOps"),
    ("Scikit-learn", "PyTorch"),
    ("Scikit-learn", "TensorFlow"),
    ("PyTorch", "RLHF"),
    ("PyTorch", "Ray"),
    ("SQL", "Spark"),
    ("Spark", "Kafka"),
    ("Spark", "Feature Stores"),
    ("FastAPI", "System Design"),
    ("Distributed Systems", "System Design"),
    ("Distributed Systems", "Ray"),
    ("Embeddings", "RAG"),
    ("Embeddings", "Pinecone"),
    ("Prompt Engineering", "LangChain"),
    ("LangChain", "RAG"),
    ("LangChain", "LLMOps"),
    ("RAG", "RLHF"),
    ("Statistics", "Scikit-learn"),
    ("Statistics", "RLHF"),
]


def seed():
    driver = GraphDatabase.driver(uri, auth=(user, pwd))
    
    with driver.session() as session:
        # Clear existing
        session.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing data")
        
        # Create skill nodes
        for skill in SKILLS:
            session.run(
                "CREATE (s:Skill {name: $name, level: $level, category: $category})",
                name=skill["name"],
                level=skill["level"],
                category=skill["category"]
            )
        print(f"Created {len(SKILLS)} skill nodes")
        
        # Create prerequisite relationships
        for prereq, skill in PREREQUISITES:
            session.run(
                """
                MATCH (a:Skill {name: $prereq})
                MATCH (b:Skill {name: $skill})
                CREATE (a)-[:PREREQUISITE_FOR]->(b)
                """,
                prereq=prereq,
                skill=skill
            )
        print(f"Created {len(PREREQUISITES)} prerequisite relationships")
        
        # Verify
        result = session.run("MATCH (n:Skill) RETURN count(n) as count")
        count = result.single()["count"]
        print(f"Verified: {count} skills in Neo4j")
    
    driver.close()
    print("Neo4j skill graph seeded successfully")


if __name__ == "__main__":
    seed()