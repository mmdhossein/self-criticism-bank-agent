from states.state import BankState


def route_after_fraud_score(state: BankState) -> str:
    if state.get("fraud_score", 0) >= 80:
        state["handoff_reason"] = "fraud"
        return "human_handoff"
    return "fetch_extra_info"
