import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    # Gemini Embedding Model
    EMBEDDING_MODEL = "models/text-embedding-004"
    # Gemini Free Tier is free (as of now), Paid tier pricing varies
    # 仮置き: 無料なので0にするか、あるいは有料プランの単価を入れる
    # Vertex AI Pricing: $0.000025 per 1k characters (Text) or similar
    # ここではGemini API (AI Studio) の無料枠を前提として0とするが、
    # 意識付けのために概算値を入れておくのもあり。
    EMBEDDING_COST_PER_1M_TOKENS = 0.0  # Free of charge in AI Studio (within limits)

    CHROMA_DB_DIR = "chroma_db"
    COLLECTION_NAME = "welfare_laws_gemini"
