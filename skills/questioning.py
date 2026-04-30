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

    質詢要以「一問一答」方式設計，不要寫成長篇講稿。

    請輸出 6 到 8 組，每組包含：
    - 第一問：一句清楚、封閉或半封閉的問題
    - 對方可能短答：模擬對方 1 到 3 句回答
    - 追問：根據對方短答繼續追打
    - 攻擊目的：這組問答要削弱什麼
    - 想逼出的承認：希望對方承認的關鍵點
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

    請用一來一回格式輸出：
    ## 模擬一來一回
    - 我方問：
    - 對方答：
    - 我方追問：
    - 對方可能再答：
    ## 回答中的漏洞
    ## 下一步追問策略
    ## 追問目的
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
