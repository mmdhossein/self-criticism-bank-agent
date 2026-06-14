# ─── Cell 4: Node 2 — PII Redactor ───────────────────────────
from states.state import BankState
import re 


def pii_redactor(state: BankState) -> BankState:
    """
    Node 2 — PII Redactor
    Masks card numbers, account numbers, national IDs, and phone numbers
    before the message is sent to any LLM for processing.
    This node runs BEFORE intent detection to protect sensitive data.
    """
    msg = state["message"]
    flags = []

    # Card numbers (16 digits, optionally spaced)
    card_pattern = r'\b(\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4})\b'
    if re.search(card_pattern, msg):
        flags.append("card_number")
        msg = re.sub(card_pattern, "[CARD-REDACTED]", msg)

    # Iranian IBAN (IR + 24 digits)
    iban_pattern = r'\bIR\d{24}\b'
    if re.search(iban_pattern, msg, re.IGNORECASE):
        flags.append("iban")
        msg = re.sub(iban_pattern, "[IBAN-REDACTED]", msg, flags=re.IGNORECASE)

    # Account numbers (10-16 digits standalone)
    acct_pattern = r'\b(\d{10,16})\b'
    # Only flag if not already caught as card
    remaining_accts = re.findall(acct_pattern, msg)
    if remaining_accts:
        flags.append("account_number")
        msg = re.sub(acct_pattern, "[ACCOUNT-REDACTED]", msg)

    # Iranian national ID (10 digits)
    nid_pattern = r'\b(\d{10})\b'
    if re.search(nid_pattern, msg):
        flags.append("national_id")
        msg = re.sub(nid_pattern, "[NID-REDACTED]", msg)

    # Iranian mobile numbers
    mobile_pattern = r'\b(09\d{9}|(\+98|0098)9\d{9})\b'
    if re.search(mobile_pattern, msg):
        flags.append("phone_number")
        msg = re.sub(mobile_pattern, "[PHONE-REDACTED]", msg)

    state["redacted_message"] = msg
    state["pii_flags"] = ", ".join(flags) if flags else "none"

    log = state.get("audit_log", "")
    state["audit_log"] = log + f"\n[pii_redactor] pii_detected={state['pii_flags']}"
    return state
