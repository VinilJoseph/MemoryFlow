# MemoryFlow 🤖🚀

MemoryFlow is a versatile AI chatbot project built using **LangGraph** and **Streamlit**. It demonstrates various advanced LLM workflows, including RAG (Retrieval-Augmented Generation), Model Context Protocol (MCP) integration, tool-calling capabilities, and persistent conversation memory.

## 🌟 Features

-   **Multi-Agent Workflows**: Powered by LangGraph for stateful, multi-step agent interactions.
-   **RAG (Retrieval-Augmented Generation)**: Upload PDFs to chat with your documents using local embeddings (`all-MiniLM-L6-v2`) and FAISS.
-   **Tool-Calling Agent**: An agent equipped with DuckDuckGo Search, Stock Price lookup (Alpha Vantage), and a Calculator.
-   **Model Context Protocol (MCP)**: Integration with MCP servers for extensible tool capabilities.
-   **Stateful Memory**: Persistent chat history across sessions using SQLite.
-   **Modern UI**: Beautiful, interactive frontends built with Streamlit, supporting streaming and real-time status updates.

## 📁 Project Structure

| File | Description |
| :--- | :--- |
| `langraph_rag_backend.py` | Backend for the RAG-enabled chatbot. |
| `streamlit_rag_frontend.py` | UI for uploading PDFs and chatting with documents. |
| `langgraph_tool_backend.py` | Backend for the tool-calling agent. |
| `streamlit_frontend_tool.py` | UI for the tool-calling agent. |
| `langgraph_mcp_backend.py` | Backend with Model Context Protocol integration. |
| `streamlit_frontend_mcp.py` | UI for the MCP-powered chatbot. |
| `mcp_server/` | Example MCP server implementations. |
| `requirements.txt` | Project dependencies. |
| `.env` | Environment variables (API Keys, etc.). |

## 🚀 Getting Started

### 1. Prerequisites

-   Python 3.10+
-   A [Groq API Key](https://console.groq.com/) (used by default for LLM inference)
-   An [Alpha Vantage API Key](https://www.alphavantage.co/support/#api-key) (optional, for stock price tools)

### 2. Installation

1.  Clone the repository:
    ```bash
    git clone <repository-url>
    cd MemoryFlow
    ```

2.  Create and activate a virtual environment:
    ```bash
    python -m venv langraph_venv
    # Windows
    .\langraph_venv\Scripts\activate
    # macOS/Linux
    source langraph_venv/bin/activate
    ```

3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

Create a `.env` file in the root directory and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key_here
ALPHAVANTAGE_API_KEY=your_alpha_vantage_key_here
```

### 4. Running the Applications

Each feature has its own frontend. Run the one you need using Streamlit:

#### To run the RAG Chatbot (PDF Chat):
```bash
streamlit run streamlit_rag_frontend.py
```

#### To run the Tool-Calling Agent:
```bash
streamlit run streamlit_frontend_tool.py
```

#### To run the MCP Chatbot:
```bash
streamlit run streamlit_frontend_mcp.py
```

## 🛠️ Built With

-   **[LangGraph](https://github.com/langchain-ai/langgraph)**: Orchestrating the agentic state machine.
-   **[Streamlit](https://streamlit.io/)**: For the interactive web interface.
-   **[LangChain](https://python.langchain.com/)**: For LLM integration and document processing.
-   **[FAISS](https://github.com/facebookresearch/faiss)**: Fast local vector search.
-   **[Hugging Face](https://huggingface.co/)**: For local embedding models.
-   **[Groq](https://groq.com/)**: High-speed LLM inference.

## 📝 License

This project is for educational purposes. Feel free to use and modify it!
