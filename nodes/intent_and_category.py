# ─── Cell 5: Node 3 — Intent & Category Detector ─────────────
from states.state import BankState
from models.llms import llm_primary

def detect_intent_and_category(state: BankState) -> BankState:
    """
    Node 3 — Intent & Category Detector
    Uses the REDACTED message to extract intent, category, risk, and
    whether authentication is required before answering.
    """
    prompt = """You are a STRICT intent classification system for an Iranian bank's customer support chatbot.

Analyze the user's message and extract FOUR fields. You must be precise — errors in banking context cause harm.

FIELDS TO EXTRACT:
1. intent       — One sentence describing exactly what the user wants (English)
2. category     — Exactly ONE of: account | transfer | loan | card | complaint | fraud | general_inquiry
3. risk         — Exactly ONE of: low | medium | high | critical
4. requires_auth — true | false (does answering this require the user to be identity-verified first?)

RISK DEFINITIONS (be strict, escalate when in doubt):
- low      = General information request, no account access needed
- medium   = Service issue affecting the user's convenience, no financial risk
- high     = Financial dispute, failed transaction, blocked access to own funds
- critical = Fraud report, unauthorized transaction, account compromise, stolen card

AUTH REQUIREMENT RULES:
- requires_auth = true for: balance inquiry, transaction history, transfers, card operations, loan details
- requires_auth = false for: general product information, branch locations, general rates, how-to guides

ANTI-HALLUCINATION RULES:
- Do NOT invent categories not in the list above
- Do NOT add any text outside the exact format below
- If unsure about risk level, choose the HIGHER one

--- EXAMPLES ---

User: "چطور حساب پس‌انداز باز کنم؟"
intent: Inquire about the process and requirements to open a savings account
category: account
risk: low
requires_auth: false

User: "دیشب یه تراکنش ۵ میلیونی رو حسابم هست که من انجام ندادم"
intent: Report an unauthorized transaction of 5 million tomans from the account
category: fraud
risk: critical
requires_auth: true

User: "انتقال وجهم دو روزه نرسیده، پولم کجاست؟"
intent: Follow up on a delayed fund transfer that has not arrived after two days
category: transfer
risk: high
requires_auth: true

User: "نرخ سود سپرده کوتاه مدت چقدره؟"
intent: Inquire about the current interest rate for short-term deposit accounts
category: general_inquiry
risk: low
requires_auth: false

User: "کارتم رو گم کردم"
intent: Report a lost bank card and request immediate blocking
category: card
risk: critical
requires_auth: true

User: "وام ۲۰۰ میلیونی با چه شرایطی میدید؟"
intent: Inquire about eligibility conditions and terms for a 200 million toman loan
category: loan
risk: low
requires_auth: false

User: "یک ماهه قبض اشتباه برام صادر شده و پشتیبانی جواب نمیده"
intent: Dispute an incorrect bank statement and escalate after unresponsive support
category: complaint
risk: high
requires_auth: true

--- END EXAMPLES ---

User message: "{message}"

Respond in EXACTLY this format with NO extra text, NO explanations:
intent: ...
category: ...
risk: ...
requires_auth: ..."""

    result = llm_primary.invoke(
        prompt.format(message=state["redacted_message"])
    ).content.strip()

    parsed = {}
    for line in result.splitlines():
        if ":" in line:
            key, _, value = line.partition(":")
            parsed[key.strip().lower()] = value.strip().lower()

    state["intent"]        = parsed.get("intent", "")
    state["category"]      = parsed.get("category", "general_inquiry")
    state["risk"]          = parsed.get("risk", "medium")
    state["requires_auth"] = parsed.get("requires_auth", "false") == "true"

    log = state.get("audit_log", "")
    state["audit_log"] = (
        log +
        f"\n[intent_detector] category={state['category']} "
        f"risk={state['risk']} requires_auth={state['requires_auth']}"
    )
    return state
