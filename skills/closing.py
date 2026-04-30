from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.skill_catalog import get_skill_prompt


def generate_closing(
    motion: str,
    side: str,
    time_limit: str,
    materials: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side, time_limit)
    task = get_skill_prompt(
        "closing_generate",
        side=side,
        materials=materials or "沒有額外資訊，請根據辯題本身生成。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config, temperature=0.45)


def analyze_closing(
    motion: str,
    side: str,
    closing_speech: str,
    materials: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "closing_analyze",
        closing_speech=closing_speech,
        materials=materials or "無",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)
