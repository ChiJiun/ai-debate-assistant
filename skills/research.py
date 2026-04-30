from __future__ import annotations

import json
import re
from dataclasses import dataclass

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.research_client import format_search_results, format_source_cards, search_tavily
from utils.skill_catalog import get_skill_prompt


@dataclass(frozen=True)
class SearchPlanItem:
    query: str
    max_results: int


def _clamp_result_count(value: object) -> int:
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = 3
    return max(1, min(count, 4))


def _fallback_search_plan(motion: str, side: str, user_material: str) -> list[SearchPlanItem]:
    base = motion.strip() or "辯論題目"
    material_hint = user_material.strip().splitlines()[0][:80] if user_material.strip() else ""
    queries = [
        f"{base} 正方 論點 證據",
        f"{base} 反方 論點 證據",
        f"{base} 財政 經濟 影響 研究",
    ]
    if material_hint:
        queries.append(f"{base} {side} {material_hint}")
    return [SearchPlanItem(query=query, max_results=3) for query in queries]


def _parse_search_plan(raw_plan: str, motion: str, side: str, user_material: str) -> list[SearchPlanItem]:
    json_match = re.search(r"\[[\s\S]*\]", raw_plan)
    if json_match:
        try:
            items = json.loads(json_match.group(0))
        except json.JSONDecodeError:
            items = []
        parsed_items = []
        if isinstance(items, list):
            for item in items:
                if not isinstance(item, dict):
                    continue
                query = str(item.get("query", "")).strip()
                if query:
                    parsed_items.append(SearchPlanItem(query=query, max_results=_clamp_result_count(item.get("max_results"))))
        if parsed_items:
            return parsed_items[:6]

    return _fallback_search_plan(motion, side, user_material)


def _limit_text(text: str, max_chars: int = 18000) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[內容過長，已截斷以避免超過模型限制。]"


def generate_search_queries(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "research_queries",
        motion=motion,
        side=side,
        user_material=user_material or "無",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def summarize_research(
    motion: str,
    side: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt("research_summary", source_material=source_material)
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def run_research_workflow(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
    tavily_key: str,
    time_range: str,
    search_depth: str,
) -> tuple[str, str, str, str]:
    raw_queries = generate_search_queries(
        motion,
        side,
        user_material,
        llm_config,
    )
    search_plan = _parse_search_plan(raw_queries, motion, side, user_material)

    material_parts: list[str] = []
    source_card_parts: list[str] = []
    query_display_parts: list[str] = []
    for item in search_plan:
        results = search_tavily(
        item.query,
            tavily_key,
            max_results=item.max_results,
            time_range=time_range,
            search_depth=search_depth,
        )
        query_display_parts.append(f"{item.query}（取回 {item.max_results} 筆）")
        material_parts.append(f"## 查詢：{item.query}\n{format_search_results(results)}")
        source_card_parts.append(format_source_cards(item.query, results))

    search_material = _limit_text("\n\n".join(material_parts))
    source_text = "\n\n".join(source_card_parts)
    summary = summarize_research(
        motion,
        side,
        _limit_text("\n\n".join(part for part in [user_material, search_material] if part.strip())),
        llm_config,
    )
    return "\n".join(query_display_parts), search_material, source_text, summary
