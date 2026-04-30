from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt


def generate_closing(
    motion: str,
    side: str,
    time_limit: str,
    materials: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side, time_limit)
    task = f"""
    使用者是「{side}」。請根據以下資訊生成結辯稿。

    可用資訊：
    {materials or "沒有額外資訊，請根據辯題本身生成。"}

    請輸出：
    ## 結辯稿
    - 主要爭點整理
    - 對方讓步或矛盾
    - 我方為何勝出
    - 最重要的證據或推理
    - 最後結論

    請符合時間限制，寫成可直接上台使用的完整結辯稿。
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config, temperature=0.45)


def analyze_closing(
    motion: str,
    side: str,
    closing_speech: str,
    materials: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    分析以下結辯稿。

    結辯稿：
    {closing_speech}

    可參考資訊：
    {materials or "無"}

    請輸出：
    ## 是否抓住主要爭點
    ## 是否比較雙方
    ## 是否說清楚我方為何勝
    ## 遺漏的關鍵內容
    ## 建議改寫版本
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
