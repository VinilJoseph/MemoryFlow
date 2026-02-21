from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool, BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv
import aiosqlite
import requests
import asyncio
import threading
import os

load_dotenv()

# Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")


# Dedicated async loop for backend tasks
_ASYNC_LOOP = asyncio.new_event_loop()
_ASYNC_THREAD = threading.Thread(target=_ASYNC_LOOP.run_forever, daemon=True)
_ASYNC_THREAD.start()


def _submit_async(coro):
    return asyncio.run_coroutine_threadsafe(coro, _ASYNC_LOOP)


def run_async(coro):
    return _submit_async(coro).result()


def submit_async_task(coro):
    """Schedule a coroutine on the backend event loop."""
    return _submit_async(coro)


# -------------------
# 1. LLM
# -------------------
llm = ChatGroq(
    model="moonshotai/kimi-k2-instruct-0905",
    temperature=0,
    streaming=True
)

# -------------------
# 2. Tools
# -------------------
# Tools
# ddg = DuckDuckGoSearchRun(region="us-en")

# @tool
# def search(query: str) -> str:
#     """
#     Search the web for up-to-date information.
#     Always pass a single string argument called 'query'.
#     """
#     return ddg.run(query)


# @tool
# def get_stock_price(symbol: str) -> dict:
#     """
#     Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
#     using Alpha Vantage with API key in the URL.
#     """
#     url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
#     r = requests.get(url)
#     return r.json()


# MCP Client
client = MultiServerMCPClient(
        {
            "local": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

# Load MCP Tools
def load_mcp_tools() -> list[BaseTool]:
    try:
        return run_async(client.get_tools())
    except Exception:
        return []


mcp_tools = load_mcp_tools()

tools = [*mcp_tools]
llm_with_tools = llm.bind_tools(tools) if tools else llm

# -------------------
# 3. State
# -------------------
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# -------------------
# 4. Nodes
# -------------------
from langchain_core.messages import SystemMessage
from datetime import datetime

async def chat_node(state: ChatState):
    """LLM node that may answer or request a tool call."""
    messages = state["messages"]
    
    # 1. Add/Update System Message with current date to prevent date-confusion loops
    current_date = datetime.now().strftime("%Y-%m-%d")
    system_prompt = (
        f"You are a helpful assistant. The current date is {current_date}. "
        "When answering questions, especially about news, provide a summary based on the initial search results. "
        "Do not repeatedly search for details on every topic unless the user explicitly asks for deep dives. "
        "Synthesize the information you have and provide a concise answer."
    )
    system_message = SystemMessage(content=system_prompt)
    
    # Ensure system message is present and at the beginning
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [system_message] + messages
    else:
        # Update existing system message if it's there
        messages[0] = system_message

    # 2. Sanitize messages for Groq: ensure ToolMessages have non-empty content
    sanitized_messages = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            # Groq specifically rejects empty strings or empty lists for tool content
            if not msg.content:
                 new_msg = ToolMessage(
                     tool_call_id=msg.tool_call_id,
                     content="[No output from tool]",
                     name=getattr(msg, "name", None),
                     status=getattr(msg, "status", None),
                     artifact=getattr(msg, "artifact", None)
                 )
                 sanitized_messages.append(new_msg)
            else:
                sanitized_messages.append(msg)
        else:
            sanitized_messages.append(msg)
            
    response = await llm_with_tools.ainvoke(sanitized_messages)
    return {"messages": [response]}


tool_node = ToolNode(tools) if tools else None

# -------------------
# 5. Checkpointer
# -------------------

async def _init_checkpointer():
    conn = await aiosqlite.connect(database="chatbot.db")
    return AsyncSqliteSaver(conn)


checkpointer = run_async(_init_checkpointer())

# -------------------
# 6. Graph
# -------------------

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")
else:
    graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

# -------------------
# 7. Helper
# -------------------
async def _alist_threads():
    all_threads = set()
    async for checkpoint in checkpointer.alist(None):
        all_threads.add(checkpoint.config["configurable"]["thread_id"])
    return list(all_threads)


def retrieve_all_threads():
    return run_async(_alist_threads())