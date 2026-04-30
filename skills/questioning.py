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

    請找出對方申論中邏輯瑕疵、假設跳躍、證據不足、定義模糊、因果薄弱或較容易被攻擊的論述。
    但輸出時不要寫分析說明，只輸出可直接上場使用的簡短質詢問題。

    請輸出 8 到 12 題。
    格式：
    - 問題

    要求：
    - 每題只用一句話
    - 問題要短、尖銳、可回答
    - 優先使用封閉式或半封閉式問題
    - 不要輸出預期回答、追問、攻擊目的或額外分析
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

    請只輸出簡短一來一回，不要附額外分析：
    - 我方問：
    - 對方可能答：
    - 我方追問：
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
