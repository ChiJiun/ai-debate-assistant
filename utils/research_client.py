from __future__ import annotations

import os
from dataclasses import dataclass

import requests
from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class SearchResult:
    title: str
    url: str
    content: str


def get_default_tavily_key() -> str:
    return os.getenv("TAVILY_API_KEY", "")


def search_tavily(
    query: str,
    api_key: str = "",
    max_results: int = 5,
    time_range: str = "",
    search_depth: str = "basic",
) -> list[SearchResult]:
    tavily_key = api_key.strip() or get_default_tavily_key()
    if not tavily_key:
        raise RuntimeError("Missing Tavily API key. 請在側邊欄填入 Tavily API key，或在 secrets/.env 設定 TAVILY_API_KEY。")

    payload = {
        "query": query,
        "search_depth": search_depth,
        "max_results": max_results,
        "include_answer": False,
        "include_raw_content": False,
    }
    if time_range:
        payload["time_range"] = time_range

    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Authorization": f"Bearer {tavily_key}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=45,
    )
    response.raise_for_status()
    payload = response.json()
    return [
        SearchResult(
            title=item.get("title", "Untitled"),
            url=item.get("url", ""),
            content=item.get("content", ""),
        )
        for item in payload.get("results", [])
    ]


def format_search_results(results: list[SearchResult]) -> str:
    if not results:
        return ""
    lines: list[str] = []
    for index, result in enumerate(results, start=1):
        lines.append(f"[{index}] {result.title}")
        lines.append(f"URL: {result.url}")
        lines.append(f"摘要: {result.content}")
        lines.append("")
    return "\n".join(lines).strip()
