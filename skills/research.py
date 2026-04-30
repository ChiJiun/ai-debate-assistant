from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.research_client import format_search_results, search_tavily


def generate_search_queries(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
    query_count: int = 5,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    請根據辯題與使用者資料，產生適合交給 Tavily 搜尋 API 的搜尋關鍵字。

    使用者資料：
    {user_material or "無"}

    請只輸出 {query_count} 行搜尋關鍵字。
    不要輸出分析、標題、編號、Markdown、解釋或其他文字。

    要求：
    - 關鍵字要具體、可查證
    - 同時涵蓋正反方需要的事實問題
    - 可混合中文與英文
    - 每行一組搜尋字串
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def summarize_research(
    motion: str,
    side: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    整理以下資料，幫助使用者準備辯論。

    資料：
    {source_material}

    請輸出：
    ## 資料摘要
    ## 正方可用資料
    ## 反方可用資料
    ## 可查證的證據方向
    ## 需要小心的資料限制

    不要捏造資料、數據或來源。若資料不足，請明確說明不足。
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def run_research_workflow(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
    tavily_key: str,
    query_count: int,
    max_results: int,
    time_range: str,
    search_depth: str,
) -> tuple[str, str, str, str]:
    raw_queries = generate_search_queries(
        motion,
        side,
        user_material,
        llm_config,
        query_count=query_count,
    )
    queries = [line.strip().removeprefix("-").strip() for line in raw_queries.splitlines() if line.strip()]
    queries = queries[:query_count]

    material_parts: list[str] = []
    source_lines: list[str] = []
    for query in queries:
        results = search_tavily(
            query,
            tavily_key,
            max_results=max_results,
            time_range=time_range,
            search_depth=search_depth,
        )
        material_parts.append(f"## 查詢：{query}\n{format_search_results(results)}")
        source_lines.extend(f"- [{result.title}]({result.url})" for result in results if result.url)

    search_material = "\n\n".join(material_parts)
    source_text = "\n".join(source_lines)
    summary = summarize_research(
        motion,
        side,
        "\n\n".join(part for part in [user_material, search_material] if part.strip()),
        llm_config,
    )
    return "\n".join(queries), search_material, source_text, summary
