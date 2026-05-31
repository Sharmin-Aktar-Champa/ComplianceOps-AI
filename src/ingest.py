from src.utils import Utility
from src.vector_store import VectorStoreManager
from langchain_community.vectorstores import FAISS

DB_FAISS_PATH = "data/regulatory_faiss"

def build_vector_db() -> FAISS:
    nist_url = "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
    eu_url = "https://spiderhub.cedia.edu.ec/en/documents/284/export-pdf"
    
    nist_local_path = Utility.download_regulatory_pdf(nist_url, "NIST_AI_RMF.pdf")
    eu_local_path = Utility.download_regulatory_pdf(eu_url, "EU_AI_Act.pdf")
    
    nist_nodes = Utility.extract_metadata_chunks(nist_local_path, "NIST_AI_RMF.pdf")
    eu_nodes = Utility.extract_metadata_chunks(eu_local_path, "EU_AI_Act.pdf")
    
    all_regulatory_nodes = nist_nodes + eu_nodes
    vector_db = VectorStoreManager.create_local_vector_store(all_regulatory_nodes, DB_FAISS_PATH)

    return vector_db
