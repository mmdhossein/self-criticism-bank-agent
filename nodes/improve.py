# ─── Cell 10: Node 8 — Improver ───────────────────────────────
from states.state import BankState
from models.llms import llm_primary

def improve(state: BankState) -> BankState:
    """
    Node 8 — Targeted Improver
    Receives specific failure feedback from the critic and rewrites
    the draft to fix exactly those issues — no unnecessary changes.
    """
    extra = state["extra_information"] or "No live data available."
    feedback = state.get("critic_feedback", "General quality issues detected.")

    prompt = """You are a SENIOR BANKING COMPLIANCE WRITER rewriting a rejected chatbot response.

The QA Auditor rejected the draft for the specific reasons below. Fix ONLY the identified issues.
Do not change parts of the response that were not flagged.

══════════════════════════════════════════════
REJECTION REASONS FROM AUDITOR:
{feedback}
══════════════════════════════════════════════

FIX GUIDE — address each failure code:
[C1] Remove any rate/fee/product not in Available Data. Replace with: "Please confirm at our branch or official website."
[C2] Add authentication reminder as the first action: "For your security, please verify your identity via the mobile app before proceeding."
[C3] Add: (a) immediate action (block card / freeze account / call hotline), (b) escalation (branch / ombudsman).
[C4] Remove any account numbers, balances, card numbers, or personal details from the response.
[C5] Make each step explicit and actionable. Replace vague phrases with concrete instructions.
[C6] Rewrite in warm, professional tone. Remove robotic or dismissive phrasing.
[C7] Remove any content not related to banking services.

══════════════════════════════════════════════

User message   : {message}
User intent    : {intent}
Risk level     : {risk}
Requires auth  : {requires_auth}
Available data :
{extra}

Draft to fix:
{draft}

Write the corrected response in English, fixing ONLY the flagged issues:"""

    state["draft"] = llm_primary.invoke(
        prompt.format(
            feedback=feedback,
            message=state["redacted_message"],
            intent=state["intent"],
            risk=state["risk"],
            requires_auth=state["requires_auth"],
            extra=extra,
            draft=state["draft"]
        )
    ).content.strip()

    state["audit_log"] += f"\n[improver] draft revised (loop {state['critic_count']})"
    return state
