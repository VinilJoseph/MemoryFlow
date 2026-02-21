from fastmcp import FastMCP
from datetime import datetime
import math
import requests
import os
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHAVANTAGE_API_KEY")
mcp = FastMCP("utility-server")

# -------------------------------
# 1. Time Tool
# -------------------------------
@mcp.tool()
def current_time() -> str:
    """Return current local date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# -------------------------------
# 2. Calculator Tool
# -------------------------------
@mcp.tool()
def calculate(expression: str) -> str:
    """Safely evaluate a math expression."""
    allowed_names = {
        k: getattr(math, k)
        for k in dir(math)
        if not k.startswith("_")
    }
    allowed_names["abs"] = abs
    allowed_names["round"] = round

    try:
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return str(result)
    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------
# 3. Text Analyzer
# -------------------------------
@mcp.tool()
def analyze_text(text: str) -> dict:
    """Return word, character, and sentence count."""
    words = text.split()
    sentences = text.count(".") + text.count("!") + text.count("?")

    return {
        "characters": len(text),
        "words": len(words),
        "sentences": sentences
    }


# -------------------------------
# 4. HTTP Status Checker
# -------------------------------
@mcp.tool()
def check_website(url: str) -> str:
    """Check HTTP status of a website."""
    try:
        response = requests.get(url, timeout=5)
        return f"Status Code: {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------
# 5. Unit Converter
# -------------------------------
@mcp.tool()
def convert_units(value: float, from_unit: str, to_unit: str) -> str:
    """Convert between km/m and Celsius/Fahrenheit."""
    conversions = {
        ("km", "m"): lambda x: x * 1000,
        ("m", "km"): lambda x: x / 1000,
        ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
        ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
    }

    key = (from_unit.lower(), to_unit.lower())

    if key not in conversions:
        return "Unsupported conversion"

    return str(conversions[key](value))


# -------------------------------
# 6. Stock Price Tool
# -------------------------------
@mcp.tool()
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price using Alpha Vantage.
    Example: AAPL, TSLA
    """
    if not ALPHA_VANTAGE_API_KEY:
        return {"error": "Alpha Vantage API key not set"}

    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE&symbol={symbol}"
        f"&apikey={ALPHA_VANTAGE_API_KEY}"
    )

    try:
        r = requests.get(url, timeout=10)
        data = r.json()

        if "Global Quote" not in data:
            return {"error": "Invalid response from Alpha Vantage"}

        return data["Global Quote"]

    except Exception as e:
        return {"error": str(e)}


# -------------------------------
# 7. Web Search Tool (DuckDuckGo)
# -------------------------------
@mcp.tool()
def search(query: str) -> list:
    """
    Search the web for up-to-date information.
    Returns top 5 results.

    
    """
    try:
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, region="us-en", max_results=5):
                results.append({
                    "title": r.get("title"),
                    "href": r.get("href"),
                    "body": r.get("body")
                })
        return results

    except Exception as e:
        return [{"error": str(e)}]


# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    mcp.run(transport="http")
