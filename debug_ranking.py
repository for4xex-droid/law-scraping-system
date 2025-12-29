import chromadb
from chromadb.config import Settings
from src.rag_engine.config import Config
from src.rag_engine.embedder import Embedder


def debug_search(query):
    print(f"🔍 Debug Search Query: '{query}'")

    # Init Components
    embedder = Embedder()
    client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet", persist_directory=Config.CHROMA_DB_DIR
        )
    )
    collection = client.get_collection(name=Config.COLLECTION_NAME)

    # Embed
    query_vecs = embedder.embed_texts([query])

    # Search
    results = collection.query(
        query_embeddings=query_vecs,
        n_results=10,  # Top 10を見る
        include=["documents", "metadatas", "distances"],
    )

    print("\n🏆 Top 10 Results:")
    print("-" * 60)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]

    for i, (doc, meta, dist) in enumerate(zip(docs, metas, dists)):
        law_name = meta.get("law_full_name", "Unknown")
        article_num = meta.get("article_number", "?")
        print(f"{i + 1}. [{dist:.4f}] {law_name} {article_num}")
        print(f"   Sample: {doc[:50]}...")
    print("-" * 60)


if __name__ == "__main__":
    debug_search("生活困窮")
