from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt
from utils.skill_catalog import get_skill_prompt


def generate_constructive(
    motion: str,
    side: str,
    time_limit: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side, time_limit)
    task = get_skill_prompt(
        "constructive_generate",
        side=side,
        source_material=source_material or "沒有額外資料，請根據辯題本身生成。",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config, temperature=0.45)


def analyze_constructive(
    motion: str,
    side: str,
    speech: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = get_skill_prompt(
        "constructive_analyze",
        speech=speech,
        source_material=source_material or "無",
    )
    return generate_text(section_prompt(context, task), llm_config=llm_config)
