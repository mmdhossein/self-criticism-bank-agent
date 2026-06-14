from states.state import BankState
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_analyzer = SentimentIntensityAnalyzer()

def sentiment_escalator(state: BankState) -> BankState:
    scores = _analyzer.polarity_scores(state["message"])
    compound = scores["compound"]
    
    if compound <= -0.6:
        sentiment = "distressed"
    elif compound <= -0.2:
        sentiment = "negative"
    elif compound >= 0.2:
        sentiment = "positive"
    else:
        sentiment = "neutral"

    state["sentiment"] = sentiment
    state["sentiment_score"] = compound
    state["audit_log"].append(f"sentiment={sentiment} ({compound:.2f})")
    return state

def route_after_sentiment(state: BankState) -> str:
    if state["sentiment"] == "distressed":
        state["handoff_reason"] = "distressed"
        return "human_handoff"
    return "latency_guard"     # ← not "critic"
