from fastmcp import FastMCP
from datetime import datetime
import math
import requests

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
    """
    Safely evaluate a basic math expression.
    Example: '2 + 3 * 4'
    """
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
    """
    Return word count, character count, and sentence count.
    """
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
    """
    Check HTTP status of a website.
    """
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
    """
    Convert between basic units (km/m, m/km, celsius/fahrenheit).
    """
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
# Run Server
# -------------------------------
# if __name__ == "__main__":
#     mcp.run(host="0.0.0.0", port=8000)


if __name__ == "__main__":
    mcp.run(transport="http")