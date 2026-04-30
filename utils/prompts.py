from __future__ import annotations

from textwrap import dedent


STYLE_GUIDE = {
    "辯論助理": "Use a clear, practical debate-coach tone for preparation, speeches, attacks, defense, and judging strategy.",
    "正式辯論": "Use a structured, persuasive formal debate tone.",
    "課堂報告": "Use a clear classroom presentation tone with accessible explanations.",
    "簡短口語": "Use concise, natural spoken language that is easy to deliver.",
}


def base_context(motion: str, side: str, time_limit: str, output_style: str) -> str:
    style_instruction = STYLE_GUIDE.get(output_style, STYLE_GUIDE["辯論助理"])
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


def opponent_side(side: str) -> str:
    if side == "正方":
        return "反方"
    if side == "反方":
        return "正方"
    return "對方"


def debate_context(motion: str, side: str, time_limit: str | None = None) -> str:
    time_text = f"\n        發言時間限制：{time_limit}" if time_limit else ""
    return dedent(
        f"""
        你是專業辯論教練，正在協助使用者準備辯論。
        請使用繁體中文，語氣清楚、具體、實用。

        辯題：{motion}
        使用者立場：{side}{time_text}

        原則：
        - 區分事實、推論與策略建議。
        - 不要捏造數據、研究、法條或來源。
        - 若資料不足，請明確說明，並提出可查證方向。
        - 內容要能直接幫助使用者練習申論、質詢、答辯與結辯。
        """
    ).strip()
