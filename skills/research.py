from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.research_client import format_search_results, format_source_cards, search_tavily
from utils.skill_catalog import get_skill_prompt


def generate_search_queries(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt("research_queries", user_material=user_material or "無")
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
    max_results: int,
    time_range: str,
    search_depth: str,
) -> tuple[str, str, str, str]:
    raw_queries = generate_search_queries(
        motion,
        side,
        user_material,
        llm_config,
    )
    queries = [line.strip().removeprefix("-").strip() for line in raw_queries.splitlines() if line.strip()]
    queries = queries[:10]

    material_parts: list[str] = []
    source_card_parts: list[str] = []
    for query in queries:
        results = search_tavily(
            query,
            tavily_key,
            max_results=max_results,
            time_range=time_range,
            search_depth=search_depth,
        )
        material_parts.append(f"## 查詢：{query}\n{format_search_results(results)}")
        source_card_parts.append(format_source_cards(query, results))

    search_material = "\n\n".join(material_parts)
    source_text = "\n\n".join(source_card_parts)
    summary = summarize_research(
        motion,
        side,
        "\n\n".join(part for part in [user_material, search_material] if part.strip()),
        llm_config,
    )
    return "\n".join(queries), search_material, source_text, summary
