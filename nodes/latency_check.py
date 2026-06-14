import time

from states.state import BankState


LATENCY_BUDGET_MS = 8000   # 8 seconds

def latency_guard(state: BankState) -> BankState:
    elapsed = (time.perf_counter() - state["start_time"]) * 1000
    state["elapsed_ms"] = elapsed
    state["audit_log"].append(f"elapsed={elapsed:.0f}ms")
    return state

def route_after_latency(state: BankState) -> str:
    if state["elapsed_ms"] > LATENCY_BUDGET_MS:
        state["handoff_reason"] = "timeout"
        return "human_handoff"
    return "critic"
