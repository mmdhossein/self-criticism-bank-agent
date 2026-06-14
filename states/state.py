# ─── Cell 1: State Definition ────────────────────────────────
from typing import TypedDict, Optional

class BankState(TypedDict):
    message: str                # User's original message
    redacted_message: str       # PII-masked version for LLM processing
    is_relevant: bool           # Is the question banking-related?
    requires_auth: bool         # Does this need identity verification?
    intent: str                 # Extracted intent (English)
    category: str               # account | transfer | loan | card | complaint | fraud | general_inquiry
    risk: str                   # low | medium | high | critical
    pii_flags: str              # Comma-separated list of detected PII types
    extra_information: str      # Live data from bank internal API (rates, policies)
    plan: str                   # Structured response plan (English)
    draft: str                  # Working draft answer (English)
    critic_feedback: str        # Specific failure reasons from last critic pass
    decision: str               # approve | revise
    critic_count: int           # Safety counter — max 3 critique loops
    final_answer: str           # Final compliant answer (Persian)
    audit_log: str              # Append-only node execution trail
