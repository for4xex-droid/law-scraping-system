import chromadb
from chromadb.config import Settings


def inspect_exact_names():
    client = chromadb.Client(
        Settings(chroma_db_impl="duckdb+parquet", persist_directory="chroma_db")
    )

    collection = client.get_collection("welfare_laws_gemini")

    # 全件取得は重いので、metadataだけ全件なめることはできないか？
    # collection.get() はlimitなしだと全件...ではなくデフォルトがあるかも。
    # とりあえず多めに取得してsetにする。

    result = collection.get(limit=10000, include=["metadatas"])
    metadatas = result["metadatas"]

    law_names = set()
    for m in metadatas:
        if m and "law_full_name" in m:
            law_names.add(m["law_full_name"])

    print("\n=== Exact Law Names in ChromaDB ===")
    with open("exact_names_utf8.txt", "w", encoding="utf-8") as f:
        for name in sorted(list(law_names)):
            print(f"'{name}'")
            f.write(f"'{name}'\n")


inspect_exact_names()
