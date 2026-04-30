from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt


def plan_search_queries(
    motion: str,
    side: str,
    user_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    請先分析辯題與使用者資料，規劃適合上網查資料的搜尋關鍵字。

    使用者資料：
    {user_material or "無"}

    請輸出：
    ## 查詢重點
    - 這個辯題需要查哪些事實問題
    - 哪些資料對正方重要
    - 哪些資料對反方重要

    ## 建議搜尋關鍵字
    請列出 4 到 8 組搜尋關鍵字，每行一組。
    搜尋關鍵字要具體、可查證，並盡量包含中英文版本。

    格式範例：
    - balanced budget government benefits risks
    - 政府 平衡預算 優點 缺點
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
