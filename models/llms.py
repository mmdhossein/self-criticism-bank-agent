# ─── Cell 2: LLM Pool (3 Models for Critic Rotation) ─────────
from langchain_openai import ChatOpenAI

# Primary LLM — used for all nodes except critic
llm_primary = ChatOpenAI(
    model="/mnt/models/gemma",   # Replace with your primary model
    temperature=0.1,             # Low temp for factual banking responses
    api_key="",
    base_url="http://192.168.3.238:8901/v1"
)

# Critic LLM 1 — used on critic_count == 1
llm_critic_1 = ChatOpenAI(
    model="/mnt/models/mistral",  # Replace with your first critic model
    temperature=0.1,
    api_key="",
    base_url="http://192.168.3.238:8901/v1"
)

# Critic LLM 2 — used on critic_count == 2
llm_critic_2 = ChatOpenAI(
    model="/mnt/models/llama3",   # Replace with your second critic model
    temperature=0.1,
    api_key="",
    base_url="http://192.168.3.238:8902/v1"
)

# Critic LLM 3 — used on critic_count == 3 (final gate)
llm_critic_3 = ChatOpenAI(
    model="/mnt/models/qwen",     # Replace with your third critic model
    temperature=0.0,              # Zero temp for strictest final gate
    api_key="",
    base_url="http://192.168.3.238:8903/v1"
)

def get_critic_llm(count: int):
    """Return the appropriate critic LLM based on loop count."""
    return {1: llm_critic_1, 2: llm_critic_2, 3: llm_critic_3}.get(count, llm_critic_3)
