# ─── Cell 6: Node 4 — Info Fetcher ───────────────────────────
import requests
from bs4 import BeautifulSoup
from states.state import BankState


def fetch_extra_information(state: BankState) -> BankState:
    """
    Node 4 — Information Fetcher
    Pulls live rates, fees, and policy data from the bank's internal API.
    Only called for categories that benefit from live data.
    Fails gracefully — never blocks the pipeline.
    """
    state["extra_information"] = ""

    LIVE_DATA_CATEGORIES = {"loan", "general_inquiry", "account", "transfer"}
    if state.get("category") not in LIVE_DATA_CATEGORIES:
        state["audit_log"] += f"\n[info_fetcher] skipped (category={state['category']})"
        return state

    # ── Replace with your bank's actual internal API endpoint ──
    BANK_API_URL = "http://internal-bank-api/rates-and-policies"

    try:
        headers = {"User-Agent": "BankChatbot/1.0", "Accept-Language": "fa-IR,fa;q=0.9"}
        response = requests.get(BANK_API_URL, headers=headers, timeout=6)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "meta"]):
            tag.decompose()

        text  = soup.get_text(separator="\n", strip=True)
        lines = [l for l in text.splitlines() if l.strip()]
        clean = "\n".join(lines[:250])  # ~3500 chars — keep context window safe

        state["extra_information"] = clean
        state["audit_log"] += "\n[info_fetcher] live data fetched successfully"

    except Exception as e:
        state["extra_information"] = (
            "[BANK API UNAVAILABLE — Do NOT cite specific rates or fees. "
            f"Advise user to contact branch or check official website. Error: {e}]"
        )
        state["audit_log"] += f"\n[info_fetcher] API error: {e}"

    return state
