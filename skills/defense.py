from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt


def generate_defense(
    motion: str,
    side: str,
    question: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    使用者是「{side}」。請針對以下被質詢問題生成答辯。

    被質詢問題：
    {question}

    可用資料：
    {source_material or "無"}

    請輸出：
    ## 防守策略
    ## 15 到 30 秒回答
    ## 轉回己方主線的一句話
    ## 對方可能追問
    ## 追問應對
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def analyze_defense(
    motion: str,
    side: str,
    question: str,
    answer: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    分析以下答辯表現。

    被質詢問題：
    {question}

    使用者回答：
    {answer}

    請輸出：
    ## 是否正面回答問題
    ## 是否被對方框架帶走
    ## 是否回到己方標準
    ## 容易被追打的地方
    ## 建議改寫回答
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
