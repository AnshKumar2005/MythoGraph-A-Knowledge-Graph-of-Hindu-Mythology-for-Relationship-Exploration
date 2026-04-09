import re
import os
from neo4j import GraphDatabase

# ==============================
# Configuration
# ==============================

INPUT_FILE = "data/triplets_curated.txt"

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

# ==============================
# Parse triplets
# ==============================

def parse_triplets(filename):
    triplets = []
    pattern = r'{"(.*?)"\s*:\s*"(.*?)"\s*:\s*"(.*?)"}'

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            matches = re.findall(pattern, line)
            for subj, rel, obj in matches:
                triplets.append((subj.strip(), rel.strip(), obj.strip()))

    return triplets

# ==============================
# Neo4j Class
# ==============================

class KnowledgeGraph:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_triplet(self, subject, relation, obj):
        with self.driver.session() as session:
            session.execute_write(self._create_and_link_nodes, subject, relation, obj)

    @staticmethod
    def _create_and_link_nodes(tx, subject, relation, obj):
        query = (
            "MERGE (a:Entity {name: $subject}) "
            "MERGE (b:Entity {name: $object}) "
            "MERGE (a)-[r:REL {type: $relation}]->(b)"
        )
        tx.run(query, subject=subject, relation=relation, object=obj)

# ==============================
# Main
# ==============================

def main():
    print("📂 Loading triplets from local file...")

    triplets = parse_triplets(INPUT_FILE)
    print(f"✅ Loaded {len(triplets)} triplets")

    kg = KnowledgeGraph(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

    for subj, rel, obj in triplets:
        kg.create_triplet(subj, rel, obj)

    kg.close()

    print("🚀 Knowledge Graph created successfully in Neo4j")

# ==============================

if __name__ == "__main__":
    main()