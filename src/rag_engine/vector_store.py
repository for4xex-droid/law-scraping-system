import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from src.rag_engine.config import Config


class VectorStore:
    def __init__(self):
        # ChromaDB < 0.4.0 API
        self.client = chromadb.Client(
            Settings(
                chroma_db_impl="duckdb+parquet", persist_directory=Config.CHROMA_DB_DIR
            )
        )

        # コレクションの取得または作成
        self.collection = self.client.get_or_create_collection(
            name=Config.COLLECTION_NAME,
            metadata={"description": "Japanese Welfare Laws"},
            # embedding_function=Noneだと search 時に query_texts を渡そうとするとエラーになる。
            # 今回は query_embeddings を渡すので None でも良いはずだが、
            # Chromaのバージョンによっては None だとデフォルトを使おうとする場合がある。
        )

    def add_documents(
        self,
        ids: List[str],
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
    ):
        """
        ドキュメントをベクトルDBに追加
        ids: 一意のID（例: law_id + article_num）
        documents: 元のテキスト（条文）
        embeddings: ベクトル
        metadatas: 検索用のメタ情報（法律名、重要度など）
        """
        self.collection.upsert(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        filter_dict: Optional[Dict] = None,
    ) -> Dict:
        """
        ベクトル検索を実行
        filter_dict: メタデータによる絞り込み（例: {"law_full_name": "生活保護法"}）
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=filter_dict,  # Noneの場合は無視される
        )
        return results
