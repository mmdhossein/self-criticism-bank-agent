# memory.py
from pymongo import MongoClient
from datetime import datetime

_client = MongoClient("mongodb://localhost:27017/")
_db = _client["bank_chatbot"]
_sessions = _db["sessions"]

def load_history(session_id: str) -> list[dict]:
    doc = _sessions.find_one({"session_id": session_id})
    if not doc:
        return []
    return doc.get("messages", [])[-10:]    # last 10

def save_turn(session_id: str, user_msg: str, bot_reply: str, meta: dict):
    turn = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_msg,
        "bot": bot_reply,
        "intent": meta.get("intent"),
        "category": meta.get("category"),
        "risk": meta.get("risk"),
        "fraud_score": meta.get("fraud_score"),
        "sentiment": meta.get("sentiment"),
    }
    _sessions.update_one(
        {"session_id": session_id},
        {
            "$push": {"messages": {"$each": [turn], "$slice": -10}},
            "$set": {"last_active": datetime.utcnow().isoformat()},
            "$setOnInsert": {"created_at": datetime.utcnow().isoformat()}
        },
        upsert=True
    )
