import re
from typing import Literal

from langgraph.graph import END, START, StateGraph

from app.agents.complaint_agent import run_complaint_agent
from app.agents.handoff import run_handoff
from app.agents.order_agent import run_order_agent
from app.agents.policy_agent import run_policy_agent
from app.agents.triage import triage_node
from app.graph.state import CustomerSupportState


def _route_after_triage(state):
    if state.get("escalation_status"):
        return "human_handoff"
    intent = state.get("intent", "other")
    if intent in {"order_status", "shipment_tracking"}:
        return "order_agent"
    if intent in {"return", "policy_question", "refund", "exchange", "warranty"}:
        return "policy_agent"
    if intent == "complaint":
        return "complaint_agent"
    return "complaint_agent"


def _route_after_policy(state):
    if state.get("intent") == "return":
        if state.get("policy_eligible"):
            return "order_agent"
        return END
    return END


def build_graph():
    graph = StateGraph(CustomerSupportState)
    graph.add_node("triage", triage_node)
    graph.add_node("order_agent", run_order_agent)
    graph.add_node("policy_agent", run_policy_agent)
    graph.add_node("complaint_agent", run_complaint_agent)
    graph.add_node("human_handoff", run_handoff)
    graph.add_edge(START, "triage")
    graph.add_conditional_edges("triage", _route_after_triage, {
        "human_handoff": "human_handoff",
        "order_agent": "order_agent",
        "policy_agent": "policy_agent",
        "complaint_agent": "complaint_agent",
    })
    graph.add_conditional_edges("policy_agent", _route_after_policy, {
        "order_agent": "order_agent",
        END: END,
    })
    graph.add_edge("order_agent", END)
    graph.add_edge("complaint_agent", END)
    graph.add_edge("human_handoff", END)
    return graph.compile()


def run_customer_support(customer_id: str, message: str):
    initial_state: CustomerSupportState = {
        "customer_id": customer_id,
        "user_message": message,
        "order_id": None,
        "intent": "other",
        "sentiment": "neutral",
        "escalation_status": False,
        "policy_eligible": None,
        "actions_taken": [],
        "retrieved_policy_info": [],
        "order_information": None,
        "shipment_information": None,
        "final_response": "",
        "handoff_summary": "",
        "complaint_context": None,
        "issue": message,
        "history": [message],
        "explicit_human_request": False,
        "repeated_complaint": False,
        "manager_request": False,
    }
    app = build_graph()
    return app.invoke(initial_state)
