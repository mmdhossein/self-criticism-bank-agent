# ─── Cell 7: Node 5 — Planner ─────────────────────────────────
from states.state import BankState
from models.llms import llm_primary

def planner(state: BankState) -> BankState:
    """
    Node 5 — Planner
    Creates a numbered, compliance-aware response plan.
    For auth-required cases, always plans the verification step first.
    """
    extra = state["extra_information"] or (
        "No live data available. Do NOT cite specific figures. "
        "Refer to official bank channels only."
    )

    auth_instruction = (
        "IMPORTANT: This request requires identity verification. "
        "Step 1 of the plan MUST instruct the user to authenticate "
        "via the bank app or in-branch before any account information is shared."
        if state["requires_auth"]
        else ""
    )

    prompt = """You are a SENIOR COMPLIANCE OFFICER and customer support specialist at an Iranian bank.

Create a numbered step-by-step response plan. This plan will be used by an agent to write a customer reply.

STRICT PLANNING RULES — violations cause regulatory and financial harm:
1. NEVER include specific figures (rates, fees, amounts) unless they appear verbatim in the Available Data section.
2. For risk=critical or risk=high, ALWAYS include: (a) an immediate protective action step, (b) an escalation step.
3. For requires_auth=true, the FIRST step must be authentication/identity verification.
4. Never plan to share account balances, transaction details, or card data in a chat response.
5. If data is unavailable, plan to direct the user to the official app, branch, or hotline — never guess.
6. Keep the plan to 5-7 steps maximum. Be specific, not generic.

{auth_instruction}

User intent   : {intent}
Category      : {category}
Risk level    : {risk}
Requires auth : {requires_auth}
Available data:
{extra}

--- EXAMPLES ---

Intent: Report an unauthorized transaction
Category: fraud | Risk: critical | Requires auth: true
Plan:
1. Express urgent empathy; treat this as a financial emergency.
2. Instruct immediate card blocking via mobile app > Cards > Block Card, or call bank hotline 24/7.
3. Ask the user to authenticate identity through the app (national ID + OTP) before proceeding.
4. Explain how to formally report the fraud: in-app dispute form or branch visit with national ID.
5. State the investigation SLA (e.g., 5-7 business days) and give a case reference process.
6. Advise changing online banking password and PIN immediately.
7. Provide escalation: Bank Ombudsman / Central Bank complaint portal if unresolved.

Intent: Inquire about short-term deposit interest rates
Category: general_inquiry | Risk: low | Requires auth: false
Plan:
1. Confirm the bank offers short-term deposits with variable terms.
2. Cite current rates from Available Data if present; otherwise direct to official website/branch.
3. Briefly explain minimum deposit amount and term options if available in data.
4. Mention how to open a deposit: via mobile app or branch visit.
5. Offer to answer follow-up questions.

Intent: Follow up on delayed fund transfer
Category: transfer | Risk: high | Requires auth: true
Plan:
1. Empathize with the delay and acknowledge the urgency.
2. Require identity verification first: authenticate via mobile app before sharing transfer status.
3. Explain standard interbank transfer timelines from Available Data.
4. Provide self-service tracking method: app > Transfers > Transfer History.
5. If still missing, instruct to call 24/7 hotline with transfer reference number.
6. Escalate path: branch visit or formal complaint registration with reference number.

--- END EXAMPLES ---

Create the plan for the current user case:"""

    state["plan"] = llm_primary.invoke(
        prompt.format(
            auth_instruction=auth_instruction,
            intent=state["intent"],
            category=state["category"],
            risk=state["risk"],
            requires_auth=state["requires_auth"],
            extra=extra
        )
    ).content.strip()

    state["audit_log"] += "\n[planner] plan generated"
    return state
