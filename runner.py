# ─── Cell 13: Runner ──────────────────────────────────────────
from states.state import BankState
from graph.graph_assembly import app

def ask_bank_agent(message: str) -> dict:
    """Invoke the bank chatbot and print a formatted result."""
    initial_state: BankState = {
        "message":           message,
        "redacted_message":  "",
        "is_relevant":       True,
        "requires_auth":     False,
        "intent":            "",
        "category":          "",
        "risk":              "",
        "pii_flags":         "none",
        "extra_information": "",
        "plan":              "",
        "draft":             "",
        "critic_feedback":   "",
        "decision":          "",
        "critic_count":      0,
        "final_answer":      "",
        "audit_log":         "[session_start]",
    }

    result = app.invoke(initial_state)

    print("=" * 70)
    print(f"  User message  : {result['message']}")
    print(f"  PII detected  : {result['pii_flags']}")
    print(f"  Banking topic : {'Yes' if result['is_relevant'] else 'No'}")
    if result["is_relevant"]:
        print(f"  Intent        : {result['intent']}")
        print(f"  Category      : {result['category']}")
        print(f"  Risk          : {result['risk']}")
        print(f"  Requires auth : {result['requires_auth']}")
        print(f"  Critic loops  : {result['critic_count']}")
        print(f"  Final decision: {result['decision']}")
    print("-" * 70)
    print(f"  Final answer:\n\n{result['final_answer']}")
    print("=" * 70)
    print(f"\n  Audit log:\n{result['audit_log']}")
    print("=" * 70)
    return result
