try:
    import pydantic

    print(f"Pydantic version: {pydantic.VERSION}")
except ImportError:
    print("Pydantic not found")

try:
    import chromadb

    print(f"ChromaDB version: {chromadb.__version__}")
except Exception as e:
    print(f"ChromaDB error: {e}")
