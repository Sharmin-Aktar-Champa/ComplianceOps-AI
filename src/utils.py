import os
import urllib.request
from pypdf import PdfReader
import io
from dotenv import load_dotenv
from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq

load_dotenv()

class Utility:
    _SHARED_LLM_INSTANCE = None

    @classmethod
    def get_llm(cls) -> object:
        if cls._SHARED_LLM_INSTANCE is not None:
            return cls._SHARED_LLM_INSTANCE
            
        provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()

        if provider == "groq":
            try:
                cls._SHARED_LLM_INSTANCE = ChatGroq(
                    temperature = 0,
                    model_name = "llama3-70b-8192",
                    groq_api_key = os.getenv("GROQ_API_KEY")
                )
            except Exception:
                cls._SHARED_LLM_INSTANCE = OllamaLLM(
                    model = "llama3",
                    temperature = 0
                )
        else:
            cls._SHARED_LLM_INSTANCE = OllamaLLM(
                model = "llama3",
                temperature = 0
            )
        return cls._SHARED_LLM_INSTANCE

    @staticmethod
    def generate_response(prompt_template, inputs: dict) -> str:
        llm = Utility.get_llm()
        chain = prompt_template | llm
        response = chain.invoke(inputs)

        if hasattr(response, 'content'):
            return response.content
        
        return str(response)
        
    @staticmethod
    def download_regulatory_pdf(url: str, save_name: str) -> str:
        target_dir = "data"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
    
        save_path = os.path.join(target_dir, save_name)
    
        if not os.path.exists(save_path):
            headers = {
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            }
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request) as response:
                    with open(save_path, 'wb') as out_file:
                        out_file.write(response.read())    
        return save_path
    
    @staticmethod
    def extract_metadata_chunks(file_path: str, 
                                source_name: str,
                                chunk_size: int = 1200) -> list:
        chunks_with_metadata = []
        reader = PdfReader(file_path)
        for page_idx, page in enumerate(reader.pages):
            page_num = page_idx + 1
            raw_text = page.extract_text()
            
            if not raw_text or len(raw_text.strip()) == 0:
                continue
            
            start = 0
            while start < len(raw_text):
                end = start + chunk_size
                chunk_text = raw_text[start:end].strip()
                payload = {
                    "text": chunk_text,
                    "metadata": {
                        "source": source_name,
                        "page": page_num,
                        "chunk_length": len(chunk_text)
                    }
                }
                chunks_with_metadata.append(payload)
                start = end
        return chunks_with_metadata
                
                
                
            
        