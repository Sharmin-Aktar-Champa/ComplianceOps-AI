import numpy as np
from scipy.stats import entropy
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from src.utils import Utility

class GatekeeperRouter:

    @classmethod
    def _classify_intent(cls, query: str) -> str:
        ROUTER_PROMPT = ChatPromptTemplate.from_messages([
            ("system", """You are an elite Traffic Router Engine. Analyze the user's query and classify it into exactly ONE of two categories:
            - 'FAST_PATH': If the user is asking for definitions, simple explanations, facts, or basic questions about a single framework (e.g., 'What is NIST?', 'Explain EU AI Act risk levels').
            - 'DEEP_AUDIT': If the user is asking to compare, contrast, find conflicts, analyze overlaps, or run a deep regulatory audit between multiple frameworks (e.g., 'How does NIST contradict EU AI Act?').
            
            STRICT RULE: Respond with ONLY ONE WORD, either 'FAST_PATH' or 'DEEP_AUDIT'. Do not write anything else."""),
            ("human", "User Query: {query}\nCategory:")
        ])

        response = Utility.generate_response(ROUTER_PROMPT, {"query": query}).strip().upper()
        if "DEEP_AUDIT" in response:
            return "DEEP_AUDIT"
        return "FAST_PATH"

    @classmethod
    def calculate_uncertainty_route(cls, query: str, vector_db) -> dict:
        intent = cls._classify_intent(query)

        if intent == "FAST_PATH":
            docs_with_scores = vector_db.similarity_search_with_relevance_scores(query, k=1)
            docs = [doc for doc, score in docs_with_scores]
            
            return {
                "entropy": 0.0, # ফাস্ট পাথে এনট্রপি মাপার কোনো দরকারই নেই, ডিরেক্ট হার্ডকোডেড ০
                "selected_route": "Fast-Path (Direct Knowledge Retrieval)",
                "action_code": "LOW_ENTROPY_FAST_PATH",
                "context_nodes": docs
            }
        
        docs_with_scores = vector_db.similarity_search_with_relevance_scores(query, k=3)
        docs = [doc for doc, score in docs_with_scores]

        scores = [score for doc, score in docs_with_scores]
        exp_scores = np.exp(scores - np.max(scores))
        probs = exp_scores / np.sum(exp_scores)
        entropy = -np.sum(probs * np.log2(probs + 1e-9))
        
        return {
            "entropy": round(entropy, 4),
            "selected_route": "LangGraph Multi-Agent (Deep Legal Cross-Check)",
            "action_code": "CONFLICT_DETECTED_DEEP_AUDIT",
            "context_nodes": docs
        }
        
    @staticmethod
    def calculate_uncertainty_route1(query: str,
                                   vector_db: FAISS,
                                   entropy_threshold: float = 0.85) -> dict:
        results_with_scores = vector_db.similarity_search_with_score(query, 
                                                                     k = 3)
        raw_scores = []
        scaling_factor = 40.0
        for _, score in results_with_scores:
            normalized_score = np.exp(-score * scaling_factor)
            raw_scores.append(normalized_score)
        
        total_score = sum(raw_scores)
        probabilities = [s / total_score for s in raw_scores]
        
        query_entropy = entropy(probabilities, base = 2)
        
        if query_entropy > entropy_threshold:
            route = "Multi-Agent Orchestrator (LangGraph)"
            action = "CONFLICT_DETECTED_DEEP_AUDIT"
        else:
            route = "Fast-Path Direct Retrieval"
            action = "AUTO_PASS_COMPLIANCE"
        
        return {
            "query": query,
            "entropy": round(float(query_entropy), 4),
            "probabilities": [round(p, 4) for p in probabilities], 
            "selected_route": route,
            "action_code": action,
            "context_nodes": [doc for doc, _ in results_with_scores]
        
        }