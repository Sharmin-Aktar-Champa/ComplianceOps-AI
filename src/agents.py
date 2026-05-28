from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage
from langchain_community.llms import Ollama
from langchain_core.messages import SystemMessage, HumanMessage

class AgentState(TypedDict):
    messages: Sequence[BaseMessage]
    current_query: str
    retrieved_context: list
    risk_report: str
    compliance_report: str
    contradiction_report: str
    final_compiled_report: str

class AgentSystemPrompts:
    RISK_AGENT = """You are an expert AI Risk Assessor specialized in the NIST AI RMF. 
    Your atomic task is to analyze the provided legal contexts and evaluate security, 
    operational risks, and safety vulnerabilities. Focus strictly on system-level threats."""

    COMPLIANCE_AGENT = """You are a senior Compliance Audit Officer expert in the EU AI Act. Your atomic task is to audit the provided context against mandatory regulatory requirements, compliance levels, and governance frameworks."""

    CONTRADICTION_AGENT = """You are a Legal Contradiction Detection Agent. 
    Your sole task is to cross-examine the retrieved contexts from NIST and EU Act 
    and identify hidden compliance loopholes, gaps, or conflicting requirements between the two frameworks."""

    SUPERVISOR = """You are the Chief Communication Officer and Executive Mentor. 
    Your ultimate goal is to take the complex, jargon-heavy technical reports from the Risk, Compliance, and Contradiction agents and translate them into crystal-clear, high-clarity insights.
    
    Remember Albert Einstein's words: "If you can't explain it simply, you don't understand it yourself."
    
    STRICT USER EXPERIENCE (UX) RULES:
    1. NO JARGON: Replace complex legal/technical words with simple everyday language.
    2. BE THE GUIDE: Help the user feel informed and empowered, not confused or overwhelmed.
    3. THE 'ONE-GLANCE' TEST: A non-technical CEO must understand the situation in 10 seconds.

    YOUR OUTPUT MUST FOLLOW THIS EXACT STRUCTURE:
    
    ### 🚦 The Big Picture (What is happening?)
    [Give a 2-sentence ultra-simple summary of the core situation. Use an analogy if helpful.]
    
    ### ⚡ 3 Things You Need to Know Right Now
    1. **The Conflict**: [Explain the biggest clash between NIST and EU Act in a way a teenager would understand.]
    2. **The Risk**: [What bad thing will happen to our product if we ignore this?]
    3. **The Solution**: [What is the absolute first action step we should take?]
    
    ### 📊 Quick Comparison for Decision Making
    | What NIST Wants | What EU AI Act Demands | Our Middle Ground (Your Best Decision) |
    | :--- | :--- | :--- |
    | [Simple text] | [Simple text] | [Clear, actionable recommendation] |
    
    Tone: Empathetic, grounded, authoritative yet deeply clear. Omit any unnecessary robotic text."""

class RegulatoryAgentEngine:
    @staticmethod
    def get_local_llm(model_name = "llama3"):
        return Ollama(model = model_name, temperature = 0.2)
    
    @staticmethod
    def risk_node(state: AgentState) -> dict:
        llm = RegulatoryAgentEngine.get_local_llm()

        content_list = []
        for doc in state["retrieved_context"]:
            source = doc.metadata.get("source", "Unknown Law")
            page = doc.metadata.get("page", "Unknown Page")
            content_list.append(f"--- SOURCE: {source} (Page {page}) ---\n{doc.page_content}\n")
            
        context_text = "\n\n".join(content_list)
        prompt = f"Context from Regulatory Docs:\n{context_text}\n\nUser Query: {state['current_query']}"

        messages = [
            SystemMessage(content = AgentSystemPrompts.RISK_AGENT),
            HumanMessage(content = prompt)
        ]
        response = llm.invoke(messages)
        return {"risk_report": response}

    @staticmethod
    def compliance_node(state: AgentState) -> dict:
        llm = RegulatoryAgentEngine.get_local_llm()

        content_list = []
        for doc in state["retrieved_context"]:
            source = doc.metadata.get("source", "Unknown Law")
            page = doc.metadata.get("page", "Unknown Page")
            content_list.append(f"--- SOURCE: {source} (Page {page}) ---\n{doc.page_content}\n")
            
        context_text = "\n\n".join(content_list)
        prompt = f"Context from Regulatory Docs:\n{context_text}\n\nUser Query:{state['current_query']}"

        messages = [
            SystemMessage(content = AgentSystemPrompts.COMPLIANCE_AGENT),
            HumanMessage(content = prompt)
        ]

        response = llm.invoke(messages)
        
        return {"compliance_report": response}
            
    @staticmethod
    def contradiction_node(state: AgentState) -> dict:
        llm = RegulatoryAgentEngine.get_local_llm()

        content_list = []
        for doc in state["retrieved_context"]:
            source = doc.metadata.get("source", "Unknown Law")
            page = doc.metadata.get("page", "Unknown Page")
            content_list.append(f"--- SOURCE: {source} (Page {page}) ---\n{doc.page_content}\n")
            
        context_text = "\n\n".join(content_list)
        prompt = f"Context from Regulatory Docs:\n{context_text}\n\nUser Query:{state['current_query']}"

        messages = [
            SystemMessage(content= AgentSystemPrompts.CONTRADICTION_AGENT),
            HumanMessage(content = prompt)
        ]
        
        response = llm.invoke(messages)
        return {"contradiction_report": response}

    @staticmethod
    def supervisor_node(state: AgentState) -> dict:
        llm = RegulatoryAgentEngine.get_local_llm()

        compiled_report = f"""
        Original Query: {state['current_query']}

        1. Risk Assessment Report:
        {state['risk_report']}

        2. Compliance Audit Report:
        {state['compliance_report']}

        3. Contradiction Analysis:
        {state['contradiction_report']}
        """
        messages = [
            SystemMessage(content = AgentSystemPrompts.SUPERVISOR),
            HumanMessage(content = compiled_report)
        ]
        
        response = llm.invoke(messages)
        
        return {"final_compiled_report": response}
            
            

            

    
        
    
    