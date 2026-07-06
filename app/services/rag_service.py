import chromadb
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from app.core.config import CHROMA_PATH, CHROMA_COLLECTION

embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = chroma_client.get_or_create_collection(CHROMA_COLLECTION)

def retrieve_rag(query: str, top_k: int = 3) -> str:
    query_embedding = embed_model.get_text_embedding(query)
    results = collection.query(query_embeddings=[query_embedding], n_results=top_k)
    chunks = results["documents"][0] if results["documents"] else []
    
    return "\n\n".join(chunks)