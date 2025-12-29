from typing import List

import google.generativeai as genai

from src.rag_engine.config import Config


class Embedder:
    def __init__(self):
        if not Config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")

        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = Config.EMBEDDING_MODEL

    def calculate_tokens(self, text: str) -> int:
        """
        テキストのトークン数を計算
        簡易実装: 文字数ベース（あくまで目安）
        Note: Embeddingモデルにはcount_tokensメソッドがない場合があるため、
        純粋な文字数で代替する。
        """
        return len(text)

    def calculate_cost(self, total_tokens: int) -> float:
        """Gemini API (Free Tier) なので0を返す"""
        return 0.0

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        テキストのリストをベクトル化する (Gemini API)
        """
        if not texts:
            return []

        cleaned_texts = [t.replace("\n", " ") for t in texts]

        try:
            # batch_embed_contents はまだBeta版機能の場合があるが、
            # google-generativeai では embed_content をループするか、リストを渡す。
            # 最新SDKでは embed_content(model=..., content=list) が可能。

            result = genai.embed_content(
                model=self.model,
                content=cleaned_texts,
                task_type="retrieval_document",  # 検索対象のドキュメントとして埋め込む
                title="Law Article",  # Optional
            )

            # result['embedding'] はリストのリストになっているはず
            raw_embeddings = []
            if "embedding" in result:
                raw_embeddings = [result["embedding"]]
            elif "embeddings" in result:
                raw_embeddings = result["embeddings"]
            else:
                # 構造が違う場合のフォールバック（ループ処理）
                embeddings = []
                for text in cleaned_texts:
                    res = genai.embed_content(
                        model=self.model, content=text, task_type="retrieval_document"
                    )
                    embeddings.append(res["embedding"])
                raw_embeddings = embeddings

            # Normalized Flatten
            def normalize(ems):
                # 再帰的に「数値のリスト」になるまで皮を剥ぐ
                # 目標: List[List[float]]
                if not ems:
                    return []
                # Check current dim
                if isinstance(ems, list):
                    if len(ems) == 0:
                        return []
                    first = ems[0]
                    if isinstance(first, list):
                        # さらに深い (3次元以上) か、或いはこれがベクトルの実体 (2次元) か？
                        if len(first) > 0 and isinstance(first[0], list):
                            # 要素がリスト -> 3次元確定 -> 平滑化して再チェック
                            flattened = [x for sub in ems for x in sub]
                            return normalize(flattened)
                return ems

            return normalize(raw_embeddings)

        except Exception as e:
            print(f"Error during embedding: {e}")
            raise
