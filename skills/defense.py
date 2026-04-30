from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import base_context, section_prompt
from utils.skill_templates import get_skill_template


def generate_defense_answers(
    motion: str,
    side: str,
    time_limit: str,
    output_style: str,
    llm_config: LLMConfig,
    skill_templates: dict[str, str] | None = None,
) -> str:
    context = base_context(motion, side, time_limit, output_style)
    task = get_skill_template("defense", skill_templates)
    return generate_text(section_prompt(context, task), llm_config=llm_config)
