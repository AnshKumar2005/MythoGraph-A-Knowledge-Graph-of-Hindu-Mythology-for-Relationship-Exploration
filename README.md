# Hindu Mythology Knowledge Graph

## 📌 Description
This project presents a structured knowledge graph of Hindu mythology
constructed from textual sources using automated triplet extraction
and ontology modeling.

The dataset is derived from:
*A Classical Dictionary of Hindu Mythology and Religion* by John Dowson.

It provides a reusable ontology and dataset for:
- Knowledge graph research  
- NLP tasks  
- Computational analysis of mythological narratives

---

## ✨ Features
- Automated triplet extraction using LLMs  
- RDF ontology generation (Turtle format)  
- Curated relationship dataset  
- Neo4j graph integration  
- Scalable pipeline for other mythological corpora  

---

## 📂 Dataset Description

### 1. RDF Ontology
- `triplets_formatted.ttl`  
  Main structured ontology in Turtle (RDF) format.

### 2. Curated Dataset
- `triplets_curated.txt`  
  Refined set of relationships used for knowledge graph construction.

### 3. Raw Extracted Data
- `triplets_raw.txt`  
  Automatically extracted triplets from source text.

---

## ⚙️ Methodology
1. Text preprocessing of source corpus  
2. Automated triplet extraction using language models  
3. Post-processing and formatting into RDF (TTL)  
4. Selective curation of relationships  
5. Graph construction using Neo4j  

---

## 🚀 Usage Pipeline

1. Install dependencies
pip install -r requirements.txt

2. Extract triplets
export OPENAI_API_KEY=your_api_key
python scripts/triplet_extraction.py

3. Convert to RDF (TTL)
python scripts/ttl_converter.py

4. Import into Neo4j
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=your_password

python scripts/neo4j_import.py

---

## 📊 Knowledge Graph

![Knowledge Graph](images/graph_visualization.jpeg)

---

## 🔍 Example Triplets
{"Arjuna" : "Husband Of" : "Subhadra"}
{"Arjuna" : "Father Of" : "Abhimanyu"}
{"Arjuna" : "Friend" : "Krishna"}
{"Arjuna" : "Killed" : "Karna"}

---

## 🔎 Example Queries
MATCH (n {name: "Arjuna"})-[r]->(m)
RETURN n, r, m;
MATCH (n)-[r]->(m)
RETURN n, r, m;

--

## 🧪 Usage
- TTL file can be used in RDF tools  
- CSV/JSON can be imported into Neo4j  
- Triplets can be reused for NLP/Graph tasks  

---

## 📚 Source Text

Dowson, John. *A Classical Dictionary of Hindu Mythology and Religion*

Available at:
https://archive.org/stream/dowson-1913-classical-dictionary-hindu-mythology/Dowson_1913_Classical_Dictionary_Hindu_Mythology_djvu.txt

---

## 👨‍💻 Contributors

- Ansh Kumar (Co-author)
- Your Friend Name (Co-author)

---

## 📜 License
MIT License
