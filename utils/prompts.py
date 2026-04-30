from __future__ import annotations

from textwrap import dedent


STYLE_GUIDE = {
    "正式辯論": "Use a structured, persuasive formal debate tone.",
    "課堂報告": "Use a clear classroom presentation tone with accessible explanations.",
    "簡短口語": "Use concise, natural spoken language that is easy to deliver.",
}


def base_context(motion: str, side: str, time_limit: str, output_style: str) -> str:
    style_instruction = STYLE_GUIDE.get(output_style, STYLE_GUIDE["正式辯論"])
    return dedent(
        f"""
        You are an expert debate coach helping students prepare quickly.
        Reply in Traditional Chinese unless the debate motion strongly requires English terms.

        Debate motion: {motion}
        Requested side option: {side}
        Speech time limit: {time_limit}
        Output style: {output_style}
        Style guidance: {style_instruction}

        Requirements:
        - Be concrete and beginner-friendly.
        - Do not invent exact statistics, citations, laws, or named studies.
        - When evidence is needed, describe credible evidence directions users can research.
        - Use clear Markdown headings and bullet points.
        - Keep the output practical for preparing a real debate.
        """
    ).strip()


def section_prompt(context: str, task: str) -> str:
    return f"{context}\n\nTask:\n{task.strip()}"
