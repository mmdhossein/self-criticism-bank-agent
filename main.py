from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from states.state import BankState

_embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
_vectordb = Chroma(persist_directory="./chroma_db", embedding_function=_embeddings)

def fetch_extra_information(state: BankState) -> BankState:
    # RAG query first
    results = _vectordb.similarity_search(state["redacted_message"], k=3)
    rag_context = "\n---\n".join([doc.page_content for doc in results])

    # then your existing API fetch logic
    # ...

    state["extra_information"] = f"[RAG]\n{rag_context}\n\n[API]\n{api_data}"
    return state
