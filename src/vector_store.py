import os
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

class VectorStoreManager:
    @staticmethod
    def create_local_vector_store(chunks: list,
                                  store_path: str = "data/faiss_index") -> FAISS:
        
        embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
        texts = [item["text"] for item in chunks]
        metadatas = [item["metadata"] for item in chunks]
        db = FAISS.from_texts(texts, 
                              embeddings, 
                              metadatas = metadatas)
        db.save_local(store_path)
        return db

    @staticmethod
    def load_local_vector_store(store_path: str = "data/faiss_index") -> FAISS:
        embeddings = HuggingFaceEmbeddings(model_name = "all-MiniLM-L6-v2")
        db = FAISS.load_local(store_path,
                             embeddings,
                             allow_dangerous_deserialization = True)
        return db
        
        
        