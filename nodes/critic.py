# ─── Cell 9: Node 7 — Critic (Rotates 3 LLMs) ────────────────
from states.state import BankState
from models.llms import llm_primary, get_critic_llm

def critic(state: BankState) -> BankState:
    """
    Node 7 — Multi-LLM Quality & Compliance Critic
    Each loop uses a DIFFERENT LLM for independent review.
    Returns specific failure reasons to guide the Improver.
    Auto-approves after 3 loops (safety cap).
    """
    if state.get("critic_count", 0) >= 3:
        state["decision"]       = "approve"
        state["critic_feedback"] = "Max loops reached. Auto-approved."
        state["audit_log"]      += "\n[critic] max loops reached — auto-approved"
        return state

    state["critic_count"] = state.get("critic_count", 0) + 1
    active_llm = get_critic_llm(state["critic_count"])

    prompt = """You are an INDEPENDENT BANKING COMPLIANCE AUDITOR reviewing a chatbot draft response.

Your job is to catch errors that could cause financial harm, regulatory violations, or customer distrust.

══════════════════════════════════════════════
EVALUATION CHECKLIST (check ALL — one failure = revise):
══════════════════════════════════════════════

[C1] ACCURACY      — Does the response cite ONLY facts present in Available Data?
                     Any invented rate, fee, product name, or code = FAIL.

[C2] AUTH SAFETY   — If requires_auth=true, does the response require identity
                     verification BEFORE sharing any account-specific information? = FAIL if missing.

[C3] ESCALATION    — For risk=high or risk=critical, are BOTH an immediate action
                     AND an escalation path (hotline/branch/ombudsman) present? = FAIL if missing.

[C4] PII SAFETY    — Does the response repeat or expose any account number, card
                     number, balance, or personal data? = FAIL if yes.

[C5] COMPLETENESS  — Are all plan steps addressed? Is the response actionable?
                     Vague answers like "contact support" with no details = FAIL.

[C6] TONE          — Professional and empathetic? No robotic or dismissive language? = FAIL if poor.

[C7] SCOPE         — Does the response stay strictly within banking topics? = FAIL if off-topic.

══════════════════════════════════════════════

User message     : {message}
User intent      : {intent}
Risk level       : {risk}
Requires auth    : {requires_auth}
Critic loop      : {critic_count} / 3
Available data   : {extra}

Draft response:
{draft}

══════════════════════════════════════════════
OUTPUT FORMAT — You MUST follow this exactly:
══════════════════════════════════════════════
decision: approve   OR   decision: revise
feedback: [If revise: list each failed check by ID and reason. If approve: write "All checks passed."]

Example of revise output:
decision: revise
feedback: [C1] Cited an interest rate of 22% not found in Available Data. [C3] No escalation path provided for high-risk transfer dispute.

Example of approve output:
decision: approve
feedback: All checks passed."""

    result = active_llm.invoke(
        prompt.format(
            message=state["redacted_message"],
            intent=state["intent"],
            risk=state["risk"],
            requires_auth=state["requires_auth"],
            critic_count=state["critic_count"],
            extra=state["extra_information"] or "No live data.",
            draft=state["draft"]
        )
    ).content.strip()

    # Parse decision and feedback
    decision = "revise"
    feedback = ""
    for line in result.splitlines():
        if line.lower().startswith("decision:"):
            decision = "approve" if "approve" in line.lower() else "revise"
        if line.lower().startswith("feedback:"):
            feedback = line.partition(":")[2].strip()

    state["decision"]        = decision
    state["critic_feedback"] = feedback

    model_name = ["", "mistral", "llama3", "qwen"][state["critic_count"]]
    state["audit_log"] += (
        f"\n[critic_{state['critic_count']}|{model_name}] "
        f"decision={decision} feedback={feedback[:120]}"
    )
    return state
