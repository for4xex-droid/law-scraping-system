import json
import os
import sys

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.rag_engine.vector_store import VectorStore

# Initialize VectorStore (this connects to Chroma)
print("Initializing VectorStore...")
try:
    vs = VectorStore()
except Exception as e:
    print(f"Failed to load VectorStore: {e}")
    sys.exit(1)

print("Fetching all data from Chroma...")
# Fetch all embeddings and metadata
# We use a limit that is definitely larger than the dataset (e.g. 10000)
# calculate total count first?
count = vs.collection.count()
print(f"Total documents found: {count}")

results = vs.collection.get(include=["embeddings", "documents", "metadatas"])

ids = results["ids"]
documents = results["documents"]
metadatas = results["metadatas"]
embeddings = results["embeddings"]

if not ids:
    print("No data found.")
    sys.exit(0)

print(f"Exporting {len(ids)} items...")

export_data = []

for i in range(len(ids)):
    item = {
        "id": ids[i] or str(i),
        "text": documents[i] or "",
        "metadata": metadatas[i] or {},
        "embedding": embeddings[i] or [],
    }
    export_data.append(item)

output_path = os.path.join("backend", "data", "index.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(export_data, f, ensure_ascii=False)

print(f"Successfully exported to {output_path}")
