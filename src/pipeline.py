import time
from typing import Optional
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from src.router import GatekeeperRouter
from src.graph import ComplianceGraphBuilder
from src.utils import Utility

class ComplianceEngine:
    
    def __init__(self, vector_db):
        self.vector_db = vector_db
        self.agent_app = ComplianceGraphBuilder.build_workflow()

    def _execute_fast_path_inference(self, best_node: Optional[Document], query) -> str:
        if not best_node:
            return "No relevant context found in the database to answer this question."
        
        source_file: str = best_node.metadata.get("source", "Unknown Law")
        page_num: str = best_node.metadata.get("page", "N/A")

        FAST_PATH_PROMPT = ChatPromptTemplate.from_messages([
            ("system", "You are a helpful Regulatory Assistant. Provide a direct, clear, and "
                       "concise answer based strictly on the provided context.\n\n"
                       "Context (Source: {source_file}, Page: {page_num}):\n{context}"),
            ("human", "{query}")
        ])
        
        inputs = {
            "source_file": source_file,
            "page_num": page_num,
            "context": best_node.page_content,
            "query": query
        }
        
        return Utility.generate_response(FAST_PATH_PROMPT, inputs)
            
    def run(self, query: str) -> dict:
        start_time = time.time()
        
        telemetry = GatekeeperRouter.calculate_uncertainty_route(query, self.vector_db)

        response_data = {
            "query": query,
            "route_taken": telemetry["selected_route"],
            "entropy": telemetry["entropy"],
            "execution_time": 0.0,
            "output": ""
        }

        if telemetry["action_code"] == "CONFLICT_DETECTED_DEEP_AUDIT":
            initial_state = {
                "current_query": query,
                "retrieved_context": telemetry["context_nodes"],
                "risk_report": "",
                "compliance_report": "",
                "contradiction_report": "",
                "final_compiled_report": ""
            }
            
            final_state = self.agent_app.invoke(initial_state)
            response_data["output"] = final_state["final_compiled_report"]
        else:
            best_node = telemetry["context_nodes"][0] if telemetry["context_nodes"] else None
            response_data["output"] = self._execute_fast_path_inference(best_node, query)
        
        end_time = time.time()
        response_data["execution_time"] = round(end_time - start_time, 2)
        return response_data
                