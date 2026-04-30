from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillInfo:
    key: str
    name: str
    purpose: str
    prompt: str


SKILLS: dict[str, SkillInfo] = {
    "research_queries": SkillInfo(
        key="research_queries",
        name="查資料：搜尋關鍵字",
        purpose="分析辯題與使用者資料，產生交給 Tavily 的乾淨搜尋關鍵字。",
        prompt="""
請根據辯題與使用者資料，產生適合交給 Tavily 搜尋 API 的搜尋關鍵字。

使用者資料：
{user_material}

請自行判斷需要搜尋幾組關鍵字，通常 3 到 7 組即可。
請只輸出搜尋關鍵字。
不要輸出分析、標題、編號、Markdown、解釋或其他文字。

要求：
- 關鍵字要具體、可查證
- 同時涵蓋正反方需要的事實問題
- 可混合中文與英文
- 每行一組搜尋字串
""".strip(),
    ),
    "research_summary": SkillInfo(
        key="research_summary",
        name="查資料：整理結果",
        purpose="閱讀手動資料與 Tavily 搜尋結果，整理成正反方可用素材與資料限制。",
        prompt="""
整理以下資料，幫助使用者準備辯論。

資料：
{source_material}

請輸出：
## 資料摘要
## 正方可用資料
## 反方可用資料
## 可查證的證據方向
## 需要小心的資料限制

不要捏造資料、數據或來源。若資料不足，請明確說明不足。
""".strip(),
    ),
    "constructive_generate": SkillInfo(
        key="constructive_generate",
        name="申論：生成申論稿",
        purpose="根據辯題、立場、時間與資料生成可上台使用的申論稿。",
        prompt="""
根據以下資料，為「{side}」生成申論稿。

可用資料：
{source_material}

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
""".strip(),
    ),
    "constructive_analyze": SkillInfo(
        key="constructive_analyze",
        name="申論：分析申論稿",
        purpose="分析使用者輸入的申論稿，指出優點、弱點與改寫方向。",
        prompt="""
分析以下申論稿。

申論稿：
{speech}

可參考資料：
{source_material}

請輸出：
## 優點
## 主要問題
## 可能被對方攻擊的地方
## 如何補強
## 建議改寫版本
""".strip(),
    ),
    "questioning_generate": SkillInfo(
        key="questioning_generate",
        name="質詢：生成問題",
        purpose="找出對方申論中的弱點，輸出可直接提問的簡短質詢問題。",
        prompt="""
使用者是「{side}」，請針對「{opponent}」的申論或資料設計質詢問題。

對方申論 / 資料：
{opponent_material}

請找出對方申論中邏輯瑕疵、假設跳躍、證據不足、定義模糊、因果薄弱或較容易被攻擊的論述。
但輸出時不要寫分析說明，只輸出可直接上場使用的簡短質詢問題。

請輸出 8 到 12 題。
格式：
- 問題

要求：
- 每題只用一句話
- 問題要短、尖銳、可回答
- 優先使用封閉式或半封閉式問題
- 不要輸出預期回答、追問、攻擊目的或額外分析
""".strip(),
    ),
    "questioning_simulate": SkillInfo(
        key="questioning_simulate",
        name="質詢：模擬對方回答",
        purpose="針對使用者輸入的質詢問題，模擬對方短答並給出追問。",
        prompt="""
請模擬「{opponent}」面對質詢時可能如何回答，並幫「{user_side}」設計追問。

質詢問題：
{question}

對方可用材料：
{opponent_material}

請只輸出簡短一來一回，不要附額外分析：
- 我方問：
- 對方可能答：
- 我方追問：
""".strip(),
    ),
    "defense_generate": SkillInfo(
        key="defense_generate",
        name="答辯：生成答辯",
        purpose="針對被質詢問題，生成短答、可能追問與轉回主線的句子。",
        prompt="""
使用者是「{side}」。請針對以下被質詢問題生成答辯。

被質詢問題：
{question}

可用資料：
{source_material}

答辯以一來一回的短回答為主，不要寫成完整申論稿，也不要提供過多分析。

請輸出：
- 對方問：
- 我方答：用 2 到 4 句回答，控制在 15 到 30 秒
- 對方可能追問：
- 我方再答：用 1 到 3 句回答
- 轉回主線：
""".strip(),
    ),
    "defense_analyze": SkillInfo(
        key="defense_analyze",
        name="答辯：分析回答",
        purpose="簡短分析使用者的答辯回答，並給一版可直接使用的改寫。",
        prompt="""
分析以下答辯表現。

被質詢問題：
{question}

使用者回答：
{answer}

請簡短輸出：
## 問題
- 最多 3 點
## 建議回答
- 給一版 15 到 30 秒的改寫回答
""".strip(),
    ),
    "closing_generate": SkillInfo(
        key="closing_generate",
        name="結辯：生成結辯稿",
        purpose="綜合全場資料，生成符合時間限制的完整結辯稿。",
        prompt="""
使用者是「{side}」。請根據以下資訊生成結辯稿。

可用資訊：
{materials}

請輸出：
## 結辯稿
- 主要爭點整理
- 對方讓步或矛盾
- 我方為何勝出
- 最重要的證據或推理
- 最後結論

請符合時間限制，寫成可直接上台使用的完整結辯稿。
""".strip(),
    ),
    "closing_analyze": SkillInfo(
        key="closing_analyze",
        name="結辯：分析結辯稿",
        purpose="分析結辯稿是否掌握爭點、比較雙方並說清楚勝負理由。",
        prompt="""
分析以下結辯稿。

結辯稿：
{closing_speech}

可參考資訊：
{materials}

請輸出：
## 是否抓住主要爭點
## 是否比較雙方
## 是否說清楚我方為何勝
## 遺漏的關鍵內容
## 建議改寫版本
""".strip(),
    ),
}


def get_skill_prompt(key: str, **values: str) -> str:
    return SKILLS[key].prompt.format(**values)
