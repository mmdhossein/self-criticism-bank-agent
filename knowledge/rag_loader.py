# rag_loader.py  — run once to build the DB
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

DOCS_DIR = "./bank_docs"        # drop .txt / .pdf files here
CHROMA_DIR = "./chroma_db"

loader = DirectoryLoader(DOCS_DIR, glob="**/*.txt", loader_cls=TextLoader)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
db = Chroma.from_documents(chunks, embeddings, persist_directory=CHROMA_DIR)
db.persist()
print(f"Loaded {len(chunks)} chunks into ChromaDB")
