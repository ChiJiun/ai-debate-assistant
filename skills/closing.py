from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import base_context, section_prompt
from utils.skill_templates import get_skill_template


def generate_closing_speeches(
    motion: str,
    side: str,
    time_limit: str,
    output_style: str,
    previous_materials: str,
    llm_config: LLMConfig,
    skill_templates: dict[str, str] | None = None,
) -> str:
    context = base_context(motion, side, time_limit, output_style)
    task = get_skill_template("closing", skill_templates).replace("{previous_materials}", previous_materials)
    return generate_text(section_prompt(context, task), llm_config=llm_config, temperature=0.45)
