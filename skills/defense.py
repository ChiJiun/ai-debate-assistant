from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.skill_catalog import get_skill_prompt


def generate_defense(
    motion: str,
    side: str,
    question: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "defense_generate",
        side=side,
        question=question,
        source_material=source_material or "無",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)


def analyze_defense(
    motion: str,
    side: str,
    question: str,
    answer: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt("defense_analyze", question=question, answer=answer)
    return generate_text(section_prompt(context, task), llm_config=llm_config)
