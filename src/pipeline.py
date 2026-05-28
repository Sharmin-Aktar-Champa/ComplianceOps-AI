import time
from typing import Optional
from langchain_core.documents import Document
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage
from src.router import GatekeeperRouter
from src.graph import ComplianceGraphBuilder

class ComplianceEngine:
    
    def __init__(self, vector_db, fast_path_model="llama3"):
        self.vector_db = vector_db
        self.agent_app = ComplianceGraphBuilder.build_workflow()
        self.fast_path_llm = Ollama(model=fast_path_model, temperature=0.1)

    def _execute_fast_path_inference(self, best_node: Optional[Document], query) -> str:
        if not best_node:
            return "No relevant context found in the database to answer this question."
        
        source_file: str = best_node.metadata.get("source", "Unknown Law")
        page_num: str = best_node.metadata.get("page", "N/A")
        fast_prompt: str = (
            f"You are a helpful Regulatory Assistant. Provide a direct, clear, and "
            f"concise answer based strictly on the provided context.\n\n"
            f"Context (Source: {source_file}, Page: {page_num}):\n{best_node.page_content}"
        )
        messages = [
            SystemMessage(content=fast_prompt),
            HumanMessage(content=query)
        ]
        return self.fast_path_llm.invoke(messages)
            
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
                