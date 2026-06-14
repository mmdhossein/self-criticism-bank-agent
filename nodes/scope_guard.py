# ─── Cell 3: Node 1 — Scope Guard ────────────────────────────
import re

from states.state import BankState
from models.llms import llm_primary


def scope_guard(state: BankState) -> BankState:
    """
    Node 1 — Scope Guard
    Strictly determines if the message is about banking services.
    Any ambiguity defaults to irrelevant to protect the pipeline.
    """
    prompt = """You are the SCOPE FILTER for an official Iranian bank's customer support chatbot.

YOUR ONLY JOB: Decide if the user's message is about banking or financial services offered by this bank.

BANKING TOPICS (mark as relevant):
- Account management (balance inquiry, account opening/closing, statements)
- Money transfers (domestic, interbank, international SWIFT/IBAN)
- Cards (debit, credit, prepaid — activation, blocking, PIN, limits)
- Loans and installment facilities (application, repayment, interest)
- Deposits and savings accounts (rates, terms, opening, maturity)
- Online banking / mobile banking app issues
- Branch and ATM locations and hours
- Fees, commissions, and charges
- Currency exchange rates offered by the bank
- Cheques and payment orders
- Fraud reports, unauthorized transactions, account security
- Billing disputes and complaint registration
- Safe deposit boxes, investment products offered by the bank

NON-BANKING TOPICS (mark as irrelevant):
- General financial advice not related to bank products
- Stock market, crypto, real estate speculation
- Legal advice, medical, travel
- Prices of goods, exchange rates from non-bank sources
- Any topic not directly about the bank's own services

CRITICAL RULES:
- If the message MIGHT be off-topic, mark it irrelevant.
- If the message is empty or nonsensical, mark it irrelevant.
- You must respond with EXACTLY one word. No explanation.

--- EXAMPLES ---

User: "چطور یه حساب جاری باز کنم؟"
Answer: relevant

User: "بهترین سهام برای خرید چیه؟"
Answer: irrelevant

User: "کارت بانکیم مسدود شده، چطور باز کنم؟"
Answer: relevant

User: "آب و هوای فردا چطوره؟"
Answer: irrelevant

User: "وام مسکن با چه شرایطی میدید؟"
Answer: relevant

User: "چطور بیتکوین بخرم؟"
Answer: irrelevant

User: "انتقال وجه بین‌بانکی چقدر طول میکشه؟"
Answer: relevant

User: "قیمت دلار در صرافی آزاد چنده؟"
Answer: irrelevant

User: "رمز دوم کارتم رو گم کردم"
Answer: relevant

User: "بهترین رستوران تهران کجاست؟"
Answer: irrelevant

--- END EXAMPLES ---

User message: "{message}"

Respond with ONLY one word: relevant or irrelevant"""

    msg = state["message"]
    result = llm_primary.invoke(prompt.format(message=msg)).content.strip().lower()

    is_rel = ("relevant" in result and "irrelevant" not in result)
    state["is_relevant"] = is_rel

    log = state.get("audit_log", "")
    state["audit_log"] = log + f"\n[scope_guard] decision={'relevant' if is_rel else 'irrelevant'}"
    return state
