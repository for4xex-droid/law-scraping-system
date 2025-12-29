import chromadb
from chromadb.config import Settings
from src.rag_engine.config import Config
import logging


def check_chroma_laws():
    # ChromaDBクライアント
    client = chromadb.Client(
        Settings(
            chroma_db_impl="duckdb+parquet", persist_directory=Config.CHROMA_DB_DIR
        )
    )
    collection = client.get_collection(name=Config.COLLECTION_NAME)

    # 全件取得（メタデータのみ）
    # getメソッドで全件取れるが、件数が多いと重いので注意。
    # しかし現在そこまで多くないので大丈夫なはず。
    results = collection.get(include=["metadatas"])
    metadatas = results["metadatas"]

    unique_laws = set()
    for meta in metadatas:
        if "law_full_name" in meta:
            unique_laws.add(meta["law_full_name"])

    with open("db_laws_utf8.txt", "w", encoding="utf-8") as f:
        f.write("========== DB LAWS ==========\n")
        for law in sorted(list(unique_laws)):
            f.write(f'"{law}",\n')
        f.write("=============================\n")
    print("Done. Check db_laws_utf8.txt")


if __name__ == "__main__":
    check_chroma_laws()
