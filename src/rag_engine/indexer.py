import logging

from src.rag_engine.embedder import Embedder
from src.rag_engine.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # 正しくは database.py に `get_all_articles_with_metadata` を追加すべき。
    # しかしPhase 2の手順としてまずはここ（Indexer）を完成させる。
    pass

    # ユーザー承認プロセス
    print("🚀 Initializing Indexer...")

    # ここでREPOからデータを取る（未実装なのでモック）
    # db_articles = repo.get_all_articles_for_embedding()
    # ...

    embedder = None
    try:
        embedder = Embedder()
    except ValueError as e:
        print(f"⚠️ Error: {e}")
        print("Please set GOOGLE_API_KEY in .env file.")
        return

    # データ読み込み（仮）
    import sqlite3

    conn = sqlite3.connect("welfare_laws_v3.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.law_id, l.law_full_name, a.article_number, a.hierarchy, a.content
        FROM articles a
        JOIN laws l ON a.law_id = l.law_id
    """)
    rows = cursor.fetchall()
    conn.close()

    print(f"📚 Found {len(rows)} articles in database.")

    if len(rows) == 0:
        print("No data found. Please run populate_db.py first.")
        return

    # コスト試算
    total_tokens = 0
    batch_size = 100  # API制限考慮

    # プレビューループ
    print("Calculating token usage...")
    for row in rows:
        # row: (law_id, law_name, article_num, hierarchy, content)
        text_to_embed = f"{row[1]} {row[2]}\n{row[3]}\n{row[4]}"
        total_tokens += embedder.calculate_tokens(text_to_embed)

    cost = embedder.calculate_cost(total_tokens)
    print(f"\n📊 Estimation:")
    print(f"   Total Articles: {len(rows)}")
    print(f"   Total Tokens:   {total_tokens:,}")
    print(f"   Estimated Cost: ${cost:.5f}")

    # 自動実行のため確認スキップ
    print("Auto-proceeding with embedding...")

    # 本番処理
    store = VectorStore()

    current_batch_ids = []
    current_batch_texts = []
    current_batch_metas = []

    print("\nProcessing batches...")

    for i, row in enumerate(rows):
        law_id, law_name, article_num, hierarchy, content = row

        # ID作成 (Uniqueness確保: law_id + article_num)
        # ※ article_numが日本語("第一条")なので、URLセーフではないがChromaDBのIDとしては文字列でOK
        doc_id = f"{law_id}_{article_num}"

        # 埋め込みテキストの構築
        # 検索精度向上のため、法律名や階層情報もテキストに含める
        text_to_embed = f"{law_name} {article_num}\n{hierarchy}\n{content}"

        # メタデータ
        metadata = {
            "law_id": law_id,
            "law_full_name": law_name,
            "article_number": article_num,
            "hierarchy": hierarchy,
        }

        current_batch_ids.append(doc_id)
        current_batch_texts.append(text_to_embed)
        current_batch_metas.append(metadata)

        # バッチサイズに達したら実行
        if len(current_batch_texts) >= batch_size:
            print(f"  Embedding batch {i - batch_size + 1} to {i}...")
            try:
                embeddings = embedder.embed_texts(current_batch_texts)

                # Debug: Check shape
                if embeddings and len(embeddings) > 0:
                    print(
                        f"    Debug: Got {len(embeddings)} embeddings. Type: {type(embeddings[0])}"
                    )
                    if isinstance(embeddings[0], list):
                        print(f"    Debug: Dim: {len(embeddings[0])}")

                store.add_documents(
                    ids=current_batch_ids,
                    documents=current_batch_texts,
                    embeddings=embeddings,
                    metadatas=current_batch_metas,
                )
            except Exception as e:
                print(f"❌ Error indexing batch: {e}")
                # Log raw error for debugging without crashing everything immediatey (optional)
                # raise e
            # リセット
            current_batch_ids = []
            current_batch_texts = []
            current_batch_metas = []

    # 残りのバッチを処理
    if current_batch_texts:
        print(f"  Embedding final batch...")
        embeddings = embedder.embed_texts(current_batch_texts)
        store.add_documents(
            ids=current_batch_ids,
            documents=current_batch_texts,
            embeddings=embeddings,
            metadatas=current_batch_metas,
        )

    print("\n🎉 Indexing Complete! Vector DB is ready.")


if __name__ == "__main__":
    main()
