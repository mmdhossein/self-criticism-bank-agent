# ─── Cell 8: Node 6 — Responder ──────────────────────────────
from states.state import BankState
from models.llms import llm_primary

def responder(state: BankState) -> BankState:
    """
    Node 6 — Responder
    Generates the first-draft English response strictly following the plan.
    Hard-coded anti-hallucination and compliance rules are injected directly.
    """
    extra = state["extra_information"] or "No live data available."

    prompt = """You are a CERTIFIED BANKING CUSTOMER SUPPORT AGENT at an Iranian bank.

Write a professional, compliant, and helpful response in English, following the plan exactly.

══════════════════════════════════════════════
ABSOLUTE RULES — Any violation will cause regulatory harm:
══════════════════════════════════════════════
[R1] NEVER state specific interest rates, fees, or exchange rates unless they appear
     WORD-FOR-WORD in the Available Data section below. If unavailable, say:
     "Please check our official website or visit a branch for current rates."

[R2] NEVER reveal or repeat any account number, card number, balance, or transaction
     detail in your response — even if the user mentioned one.

[R3] For risk=critical or risk=high: ALWAYS include the emergency hotline instruction
     and at least one escalation path.

[R4] For requires_auth=true: ALWAYS remind the user that identity verification is
     required before account-specific information can be shared.

[R5] NEVER invent product names, branch names, form names, or USSD codes not
     present in the Available Data.

[R6] If you are unsure about any fact, write: "Please confirm this with our
     official hotline or branch" — do NOT guess.

[R7] Tone must be professional, empathetic for complaints, and factual for inquiries.
══════════════════════════════════════════════

Response plan   : {plan}
User message    : {message}
Risk level      : {risk}
Requires auth   : {requires_auth}
Available data  :
{extra}

Write the draft response in English, following the plan step by step:"""

    state["draft"] = llm_primary.invoke(
        prompt.format(
            plan=state["plan"],
            message=state["redacted_message"],
            risk=state["risk"],
            requires_auth=state["requires_auth"],
            extra=extra
        )
    ).content.strip()

    state["audit_log"] += "\n[responder] draft generated"
    return state
