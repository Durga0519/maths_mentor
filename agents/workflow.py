from typing import TypedDict, Optional
from langgraph.graph import StateGraph

from agents.parser_agent   import parser_agent
from agents.router_agent   import router_agent
from agents.solver_agent   import solver_agent
from agents.verifier_agent import verifier_agent
from agents.explainer_agent import explainer_agent
from rag.retriever         import retrieve


class AgentState(TypedDict, total=False):
    question:    str
    parsed:      dict
    routing:     dict
    rag_result:  dict      # {context, sources, chunks}
    solution:    str
    verification: dict
    explanation: str
    needs_hitl:  bool


# ── Parser ──
def parser_node(state: AgentState):
    parsed = parser_agent(state["question"])
    state["parsed"]     = parsed
    state["needs_hitl"] = parsed.get("needs_clarification", False)
    return state


# ── Router ──
def router_node(state: AgentState):
    problem = state["parsed"].get("problem_text", state["question"])
    routing = router_agent(problem)
    # Merge topic from parser if router missed it
    if not routing.get("topic") or routing["topic"] == "other":
        routing["topic"] = state["parsed"].get("topic", "algebra")
    state["routing"] = routing
    return state


# ── RAG Retriever ──
def retriever_node(state: AgentState):
    problem    = state["parsed"].get("problem_text", state["question"])
    rag_result = retrieve(problem, k=2)
    state["rag_result"] = rag_result
    return state


# ── Solver ──
def solver_node(state: AgentState):
    problem  = state["parsed"].get("problem_text", state["question"])
    context  = state.get("rag_result", {}).get("context", "")
    solution = solver_agent(problem, context)
    state["solution"] = solution
    return state


# ── Verifier ──
def verifier_node(state: AgentState):
    problem      = state["parsed"].get("problem_text", state["question"])
    solution     = state["solution"]
    verification = verifier_agent(problem, solution)
    state["verification"] = verification
    # Flag HITL if confidence is low
    if verification.get("confidence", 1.0) < 0.6:
        state["needs_hitl"] = True
    return state


# ── Explainer ──
def explainer_node(state: AgentState):
    problem     = state["parsed"].get("problem_text", state["question"])
    solution    = state["solution"]
    explanation = explainer_agent(problem, solution)
    state["explanation"] = explanation
    return state


# ── Build graph ──
workflow = StateGraph(AgentState)
workflow.add_node("parser",    parser_node)
workflow.add_node("router",    router_node)
workflow.add_node("retriever", retriever_node)
workflow.add_node("solver",    solver_node)
workflow.add_node("verifier",  verifier_node)
workflow.add_node("explainer", explainer_node)

workflow.set_entry_point("parser")
workflow.add_edge("parser",    "router")
workflow.add_edge("router",    "retriever")
workflow.add_edge("retriever", "solver")
workflow.add_edge("solver",    "verifier")
workflow.add_edge("verifier",  "explainer")

graph = workflow.compile()