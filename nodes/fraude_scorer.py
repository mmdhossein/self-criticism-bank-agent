from states.state import BankState


def fraud_scorer(state: BankState) -> BankState:
    score = 0
    flags = []

    if state["risk"] in ("high", "critical"):
        score += 40
        flags.append("high_risk_intent")
    if state["requires_auth"] and state["critic_count"] == 0:
        score += 20
        flags.append("auth_required_first_attempt")
    if any(f in state["pii_flags"] for f in ["card_number", "iban"]):
        score += 30
        flags.append("sensitive_pii_present")
    if state["category"] == "fraud":
        score += 40
        flags.append("fraud_category")

    score = min(score, 100)
    state["fraud_score"] = score
    state["fraud_flags"] = flags
    state["audit_log"].append(f"fraud_score={score}, flags={flags}")
    return state
