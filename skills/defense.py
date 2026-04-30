from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.skill_catalog import get_skill_prompt


def generate_defense(
    motion: str,
    side: str,
    question: str,
    source_material: str,
    dialogue_history: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "defense_generate",
        side=side,
        question=question,
        source_material=source_material or "無",
        dialogue_history=dialogue_history or "尚未開始答辯。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def generate_defense_followup(
    motion: str,
    side: str,
    question: str,
    answer: str,
    source_material: str,
    dialogue_history: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "defense_followup",
        side=side,
        question=question,
        answer=answer,
        source_material=source_material or "無",
        dialogue_history=dialogue_history or "尚未開始答辯。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)
