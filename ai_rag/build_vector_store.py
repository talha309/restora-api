from dotenv import load_dotenv
import os

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()

VECTOR_STORE = "vector_store"
google_api_key = os.getenv("GOOGLE_API_KEY")
# Create embeddings model
embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    api_key=google_api_key
)

print("Loading documents...")

loader = TextLoader("data.txt")
documents = loader.load()

print("Splitting documents...")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=80,
)

docs = splitter.split_documents(documents)

print("Generating embeddings...")

db = FAISS.from_documents(
    docs,
    embeddings,
)

print("Saving vector store...")

db.save_local(VECTOR_STORE)

print("✅ Vector store created successfully!")