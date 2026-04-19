# /ai_rag/rag_agent.py
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langchain_text_splitters import RecursiveCharacterTextSplitter  # ✅ Fixed: better splitter
from langchain_core.tools.retriever import create_retriever_tool
from langchain_core.messages import SystemMessage              # ✅ Added: proper message type
from langgraph.graph import MessagesState
from dotenv import load_dotenv
import os

load_dotenv()

# ✅ Removed redundant google_api_key param — load_dotenv() already sets it
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# ✅ Added error handling for file loading
try:
    loader = TextLoader("data.txt")
    documents = loader.load()
except FileNotFoundError:
    raise RuntimeError("data.txt not found. Please ensure the file exists in the project root.")

# ✅ Fixed: RecursiveCharacterTextSplitter instead of CharacterTextSplitter
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")

# ✅ Added error handling for FAISS index creation
try:
    db = FAISS.from_documents(texts, embeddings)
except Exception as e:
    raise RuntimeError(f"Failed to create FAISS index: {e}")

retriever = db.as_retriever()

info_retriever = create_retriever_tool(
    retriever,
    "hotel_information_sender",
    "Searches information about the hotel from the provided vector store and returns as accurate information as possible.",  # ✅ Fixed typo: accurare → accurate
)

tools = [info_retriever]

llm_with_tools = llm.bind_tools(tools)

# ✅ Fixed: wrapped in SystemMessage object instead of plain string
sys_msg = SystemMessage(content=(
    "You are Alexandra Hotel's virtual assistant, trained to assist customers with any queries related to the hotel. "
    "Your primary responsibility is to provide accurate, helpful, and friendly responses. "
    "You have access to a specialized tool for retrieving detailed and up-to-date information about the hotel, "
    "such as amenities, room availability, pricing, dining options, events, and policies. Use this tool effectively to provide precise answers. "
    "If a query is beyond your scope or requires external actions (e.g., booking confirmation, cancellations), "
    "politely inform the user and guide them to contact the hotel's staff for further assistance. "
    "Maintain a professional yet approachable tone at all times."
))

# Defining assistant — calls llm_with_tools with system message + last 10 messages
def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"][-10:])]}

# Defining nodes and edges of the graph
builder = StateGraph(MessagesState)
builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")
builder.add_conditional_edges("assistant", tools_condition)  # routes to tools or END
builder.add_edge("tools", "assistant")

# Graph memory
memory = MemorySaver()

# Compile the graph
agent = builder.compile(checkpointer=memory)