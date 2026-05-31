import os
from typing import AsyncIterator
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from src.pipeline import ComplianceEngine
from src.vector_store import VectorStoreManager
from src.ingest import build_vector_db, DB_FAISS_PATH

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    if not os.path.exists(DB_FAISS_PATH):
        loaded_db = build_vector_db()
    else:
        loaded_db = VectorStoreManager.load_local_vector_store(DB_FAISS_PATH)
    pipeline = ComplianceEngine(vector_db = loaded_db)
    app.state.pipeline = pipeline
    yield
    
app = FastAPI(title="ComplianceOps AI Backend", lifespan = lifespan)

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
    result = app.state.pipeline.run(request.query)
    return {
        "status": "success",
        "answer": result.get("output", "No response generated"),
        "route": result.get("route_taken", "Unknown"),
        "time": float(result.get("execution_time", 0.0))
    }
    