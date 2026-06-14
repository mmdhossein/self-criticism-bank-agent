# ─── Cell 12: Graph Assembly ──────────────────────────────────
from langgraph.graph import StateGraph, END
from nodes.finalize import finalize
from nodes.critic import critic
from nodes.improve import improve
from nodes.info_fetcher import fetch_extra_information
from nodes.intent_and_category import detect_intent_and_category
from nodes.pii_redactor import pii_redactor
from nodes.planner import planner
from nodes.responder import responder
from nodes.scope_guard import scope_guard
from states.state import BankState



graph = StateGraph(BankState)

# Register all nodes
graph.add_node("scope_guard",            scope_guard)
graph.add_node("pii_redactor",           pii_redactor)
graph.add_node("detect_intent_category", detect_intent_and_category)
graph.add_node("fetch_extra_info",       fetch_extra_information)
graph.add_node("planner",                planner)
graph.add_node("responder",              responder)
graph.add_node("critic",                 critic)
graph.add_node("improve",                improve)
graph.add_node("finalize",               finalize)

graph.set_entry_point("scope_guard")

# ── Scope gate ────────────────────────────────────────────────
def scope_route(state: BankState):
    return "pii_redactor" if state["is_relevant"] else "finalize"

graph.add_conditional_edges(
    "scope_guard", scope_route,
    {"pii_redactor": "pii_redactor", "finalize": "finalize"}
)

# ── Main pipeline ─────────────────────────────────────────────
graph.add_edge("pii_redactor",           "detect_intent_category")
graph.add_edge("detect_intent_category", "fetch_extra_info")
graph.add_edge("fetch_extra_info",       "planner")
graph.add_edge("planner",                "responder")
graph.add_edge("responder",              "critic")

# ── Critic loop ───────────────────────────────────────────────
def critic_route(state: BankState):
    return "improve" if state["decision"] == "revise" else "finalize"

graph.add_conditional_edges(
    "critic", critic_route,
    {"improve": "improve", "finalize": "finalize"}
)

graph.add_edge("improve",  "critic")
graph.add_edge("finalize", END)

app = graph.compile()
print("Bank chatbot graph compiled successfully")
