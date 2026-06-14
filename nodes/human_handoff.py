import requests

from states.state import BankState   # or push to a queue

HANDOFF_WEBHOOK = "http://bank-crm/api/handoff"   # replace with real URL

def human_handoff(state: BankState) -> BankState:
    payload = {
        "session_id": state.get("session_id"),
        "reason": state.get("handoff_reason", "unknown"),
        "message": state.get("message"),
        "intent": state.get("intent"),
        "category": state.get("category"),
        "risk": state.get("risk"),
        "fraud_score": state.get("fraud_score", 0),
        "sentiment": state.get("sentiment"),
        "audit_log": state.get("audit_log", []),
        "draft": state.get("draft", ""),
    }
    try:
        requests.post(HANDOFF_WEBHOOK, json=payload, timeout=3)
    except Exception:
        pass   # fire and forget — don't block the user response

    state["final_answer"] = (
        "درخواست شما به کارشناس بانک ارجاع داده شد. "
        "به زودی با شما تماس خواهیم گرفت."
    )
    state["audit_log"].append(f"handoff_triggered reason={payload['reason']}")
    return state
