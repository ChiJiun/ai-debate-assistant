from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, opponent_side, section_prompt


def generate_questioning(
    motion: str,
    side: str,
    opponent_constructive: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    opponent = opponent_side(side)
    task = f"""
    使用者是「{side}」，請針對「{opponent}」的申論或資料設計質詢問題。

    對方申論 / 資料：
    {opponent_constructive or source_material or "沒有額外資料，請根據辯題推測對方可能論點。"}

    請輸出 6 到 8 題，每題包含：
    - 質詢問題
    - 預期對方回答
    - 追問
    - 攻擊目的
    - 想逼出的承認
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def simulate_question_answer(
    motion: str,
    user_side: str,
    question: str,
    opponent_material: str,
    llm_config: LLMConfig,
) -> str:
    opponent = opponent_side(user_side)
    context = debate_context(motion, opponent)
    task = f"""
    請模擬「{opponent}」面對質詢時可能如何回答，並幫「{user_side}」設計追問。

    質詢問題：
    {question}

    對方可用材料：
    {opponent_material or "無"}

    請輸出：
    ## 對方可能回答
    ## 回答中的漏洞
    ## 建議追問
    ## 追問目的
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
