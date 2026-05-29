from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline import ComplianceEngine
from src.vector_store import VectorStoreManager

app = FastAPI(title="ComplianceOps AI Backend")
loaded_db = VectorStoreManager.load_local_vector_store("data/regulatory_faiss")
pipeline = ComplianceEngine(vector_db=loaded_db)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    status: str
    answer: str
    route: str
    time: float

@app.get("/")
def home():
    return {"status": "healthy", "message": "FastAPI Server is running!"}

@app.post("/query", response_model = QueryResponse)
def analyze_query(request: QueryRequest):
    result = pipeline.run(request.query)
    return {
        "status": "success",
        "answer": result.get("output", "No response generated"),
        "route": result.get("route_taken", "Unknown"),
        "time": float(result.get("execution_time", 0.0))
    }
    