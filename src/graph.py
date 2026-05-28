from langgraph.graph import StateGraph, END
from src.agents import AgentState, RegulatoryAgentEngine

class ComplianceGraphBuilder:
    @staticmethod
    def _orchestrator_node(state: AgentState) -> dict:
        return {}

    @classmethod
    def build_workflow(cls) -> StateGraph:
        workflow = StateGraph(AgentState)

        workflow.add_node("orchestrator", cls._orchestrator_node)
        workflow.add_node("risk_assessor", RegulatoryAgentEngine.risk_node)
        workflow.add_node("compliance_auditor", RegulatoryAgentEngine.compliance_node)
        workflow.add_node("contradiction_detector", RegulatoryAgentEngine.contradiction_node)
        workflow.add_node("supervisor", RegulatoryAgentEngine.supervisor_node)

        workflow.set_entry_point("orchestrator")

        workflow.add_edge("orchestrator", "risk_assessor")
        workflow.add_edge("orchestrator", "compliance_auditor")
        workflow.add_edge("orchestrator", "contradiction_detector")

        workflow.add_edge("risk_assessor", "supervisor")
        workflow.add_edge("compliance_auditor", "supervisor")
        workflow.add_edge("contradiction_detector", "supervisor")

        workflow.add_edge("supervisor", END)
        app = workflow.compile()

        return app
        
        



        