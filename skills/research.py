from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt


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
