from __future__ import annotations

from utils.openai_client import LLMConfig, generate_text
from utils.prompts import debate_context, section_prompt


def generate_constructive(
    motion: str,
    side: str,
    time_limit: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side, time_limit)
    task = f"""
    根據以下資料，為「{side}」生成申論稿。

    可用資料：
    {source_material or "沒有額外資料，請根據辯題本身生成。"}

    請輸出：
    ## 申論稿
    - 開場立場
    - 關鍵定義
    - 判準 / 核心標準
    - 2 到 3 個主要論點
    - 可使用的例子或證據方向
    - 影響分析
    - 預先防守

    請符合時間限制，語氣自然、可直接上台使用。
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config, temperature=0.45)


def analyze_constructive(
    motion: str,
    side: str,
    speech: str,
    source_material: str,
    llm_config: LLMConfig,
) -> str:
    context = debate_context(motion, side)
    task = f"""
    分析以下申論稿。

    申論稿：
    {speech}

    可參考資料：
    {source_material or "無"}

    請輸出：
    ## 優點
    ## 主要問題
    ## 可能被對方攻擊的地方
    ## 如何補強
    ## 建議改寫版本
    """
    return generate_text(section_prompt(context, task), llm_config=llm_config)
