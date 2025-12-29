import chromadb
from chromadb.config import Settings
from src.rag_engine.config import Config


def inspect_content():
    print("🔍 Inspecting Data Content...")
    try:
        client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet", persist_directory=Config.CHROMA_DB_DIR
            )
        )
        collection = client.get_collection(name=Config.COLLECTION_NAME)

        with open("content_report.txt", "w", encoding="utf-8") as f:
            # 1. 児童福祉法
            f.write("\n--- 児童福祉法 (Sample) ---\n")
            results_cw = collection.get(
                where={"law_full_name": "児童福祉法"},
                limit=3,
                include=["documents", "metadatas"],
            )
            for i, doc in enumerate(results_cw["documents"]):
                f.write(f"[{i}] {results_cw['metadatas'][i]}\n")
                f.write(f"TEXT: {doc}\n\n")

            # 2. 生活困窮者自立支援法
            f.write("\n--- 生活困窮者自立支援法 (Sample) ---\n")
            results_sk = collection.get(
                where={"law_full_name": "生活困窮者自立支援法"},
                limit=3,
                include=["documents", "metadatas"],
            )
            if not results_sk["documents"]:
                f.write("❌ No documents found for 生活困窮者自立支援法!\n")
            else:
                for i, doc in enumerate(results_sk["documents"]):
                    f.write(f"[{i}] {results_sk['metadatas'][i]}\n")
                    f.write(f"TEXT: {doc}\n\n")
        print("✅ Report written to content_report.txt")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    inspect_content()
