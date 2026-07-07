from dotenv import load_dotenv

from langchain_core.messages import SystemMessage
from langchain_core.tools.retriever import create_retriever_tool

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
)

from langchain_community.vectorstores import FAISS

from langgraph.graph import START, StateGraph
from langgraph.graph import MessagesState

from langgraph.prebuilt import ToolNode
from langgraph.prebuilt import tools_condition
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
import os
load_dotenv()
google_api_key= os.getenv("GOOGLE_API_KEY")
# -----------------------------
# LLM
# -----------------------------

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    api_key=google_api_key
)
# -----------------------------
# Embeddings
# -----------------------------

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    api_key=google_api_key
)

# -----------------------------
# Load existing FAISS database
# -----------------------------

db = FAISS.load_local(
    "vector_store",
    embeddings,
    allow_dangerous_deserialization=True,
)

retriever = db.as_retriever(
    search_type="similarity",
    search_kwargs={"k":4},
)

# -----------------------------
# Retriever Tool
# -----------------------------

hotel_tool = create_retriever_tool(
    retriever,
    "hotel_information_sender",
    "Search hotel information from the knowledge base.",
)

tools = [hotel_tool]

llm_with_tools = llm.bind_tools(tools)

# -----------------------------
# System Prompt
# -----------------------------

system_message = SystemMessage(
    content="""
You are an AI customer support assistant.
Always answer using the information available in the knowledge base.
If the answer is not available, politely say you don't know.
Never make up information.
"""
)

# -----------------------------
# Assistant Node
# -----------------------------

def assistant(state: MessagesState):
    response = llm_with_tools.invoke(
        [system_message] + state["messages"][-10:]
    )

    return {
        "messages": [response]
    }

# -----------------------------
# Graph
# -----------------------------

builder = StateGraph(MessagesState)

builder.add_node("assistant", assistant)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "assistant")

builder.add_conditional_edges(
    "assistant",
    tools_condition,
)

builder.add_edge(
    "tools",
    "assistant",
)

memory = MemorySaver()

agent = builder.compile(
    checkpointer=memory
)
config = {
    "configurable": {
        "thread_id": "thread_1"
    }
}

result = {
    "messages": [
        HumanMessage(content="Who is the founded of the restaurant?")
    ]
}

response = agent.invoke(result, config=config)

print(response["messages"][-1].content)