import os
from pathlib import Path

from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv(Path(__file__).resolve().parents[2] / ".env")


def search_tavily(query: str, source_type: str = "general"):
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "status": "unavailable",
            "message": "External information could not be verified because the TAVILY_API_KEY is not set.",
        }
    try:
        client = TavilyClient(api_key)
        result = client.search(query=query, max_results=3)
        return {
            "status": "ok",
            "source_type": source_type,
            "results": result.get("results", []),
        }
    except Exception as exc:
        return {
            "status": "error",
            "source_type": source_type,
            "message": f"External information could not be verified: {exc}",
        }
