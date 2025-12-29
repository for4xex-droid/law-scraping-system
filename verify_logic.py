import chromadb
from chromadb.config import Settings
from src.rag_engine.config import Config


def verify_logic():
    print("🧪 Verifying Search Logic...")

    # DB接続確認
    try:
        client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet", persist_directory=Config.CHROMA_DB_DIR
            )
        )
        collection = client.get_collection(name=Config.COLLECTION_NAME)
        print("✅ DB Connection OK")
    except Exception as e:
        print(f"❌ DB Connection Failed: {e}")
        return

    # テストケース: "生活困窮者自立支援法"
    query = "生活困窮者自立支援法"
    print(f"\n🔍 Test Query: '{query}'")

    detected_law = "生活困窮者自立支援法"  # ロジック上はこうなるはず

    try:
        # app.py で実装したのと同じメソッドを実行
        raw_results = collection.get(
            where={"law_full_name": detected_law},
            limit=20,
            include=["documents", "metadatas"],
        )

        doc_count = len(raw_results["documents"]) if raw_results["documents"] else 0
        print(f"📊 Direct Fetch Result Count: {doc_count}")

        if doc_count > 0:
            print(f"✅ Success! First Metadata: {raw_results['metadatas'][0]}")
        else:
            print("⚠️ Direct fetch returned 0 documents! (Why?)")

            # 念のため全件メタデータから探す
            print("   Listing all available law names in DB...")
            all_meta = collection.get(include=["metadatas"])["metadatas"]
            seen_laws = set(m.get("law_full_name") for m in all_meta)
            print(f"   Available Laws: {seen_laws}")

    except Exception as e:
        print(f"❌ Direct Fetch Error: {e}")


if __name__ == "__main__":
    verify_logic()
