# 🛡️ ComplianceOps AI: Multi-Agent Policy Audit Platform

A production-grade, distributed reasoning system engineered to automate regulatory risk analysis and compliance auditing across complex legal frameworks (e.g., NIST AI RMF, EU AI Act). This platform bypasses standard linear RAG constraints by introducing an information-theoretic gateway and graph-based agent orchestration.

## 🏛️ System Architecture

```mermaid
graph TD
    A[Raw Regulatory Docs] --> B[FastAPI Async Ingestion Pipeline]
    B --> C[Metadata-Rich Chunking & Validation]
    C --> D[(Vector Store: Qdrant Mockup)]
    C --> E[(Knowledge Graph: Neo4j Topology)]
    
    F[User Policy Query] --> G[Uncertainty-Aware Gatekeeper Router]
    G -- High Entropy / Conflict Detected --> H[LangGraph Multi-Agent Orchestrator]
    G -- Low Entropy / Confident --> I[Fast-Path Direct GraphRAG Retrieval]
    
    H --> H1[Risk Assessment Agent]
    H --> H2[Compliance Audit Agent]
    H --> H3[Contradiction Detection Agent]
    
    H1 & H2 & H3 --> J[Supervisor Agent: Compiled Audit Report]
    I --> K[Auto-Pass Compliance Payload]
    
    J & K --> L[Streamlit Live Telemetry Dashboard]
