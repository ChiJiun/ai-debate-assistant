from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, opponent_side, section_prompt
from utils.skill_catalog import get_skill_prompt


def generate_questioning(
    motion: str,
    side: str,
    opponent_constructive: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    opponent = opponent_side(side)
    task = get_skill_prompt(
        "questioning_generate",
        side=side,
        opponent=opponent,
        opponent_material=opponent_constructive or source_material or "沒有額外資料，請根據辯題推測對方可能論點。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def simulate_question_answer(
    motion: str,
    user_side: str,
    question: str,
    opponent_material: str,
    dialogue_history: str,
    llm_config: LLMConfig,
) -> str:
    opponent = opponent_side(user_side)
    context = debate_context(motion, user_side)
    task = get_skill_prompt(
        "questioning_simulate",
        opponent=opponent,
        user_side=user_side,
        question=question,
        opponent_material=opponent_material or "無",
        dialogue_history=dialogue_history or "尚未開始質詢。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)
