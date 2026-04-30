from __future__ import annotations

import streamlit as st


st.set_page_config(page_title="Free Google AI Studio Guide", page_icon="📘", layout="wide")

st.title("免費使用教學：Google AI Studio")
st.caption("用 Google AI Studio 建立 Gemini API key，並在 Debate Assistant 裡使用。")

st.info(
    "Google AI Studio / Gemini API 的免費額度會依帳號、專案、地區、模型和當下政策變動。"
    "最準確的可用模型與 quota，請以你自己的 AI Studio 後台和 Rate Limits 頁面為準。"
)

st.header("1. 取得 Gemini API Key")
st.markdown(
    """
    1. 前往 [Google AI Studio](https://aistudio.google.com/).
    2. 使用 Google 帳號登入。
    3. 點選 **Get API key** 或 **API keys**。
    4. 建立新的 API key。
    5. 複製 API key，回到 Debate Assistant。
    """
)

st.header("2. 在 Debate Assistant 裡使用")
st.markdown(
    """
    1. 在左側欄位選擇 **LLM provider: Gemini**。
    2. 在 **API key** 欄位貼上你的 Google AI Studio API key。
    3. 點 **Refresh available models**。
    4. 從 **Model** 下拉選單選擇可用模型。
    5. 輸入辯題後按 **Generate Debate Materials**。
    """
)

st.header("3. 建議先試的 Gemini 模型")
st.markdown(
    """
    如果你不確定要選哪個，可以先試：

    - `gemini-2.5-flash-lite`
    - `gemini-2.5-flash`
    - `gemini-2.0-flash-lite`
    - `gemini-2.0-flash`

    如果下拉選單沒有出現你想用的模型，可以選 **Custom model** 手動輸入模型名稱。
    """
)

st.header("4. 免費使用注意事項")
st.markdown(
    """
    - 免費額度不是無限，會有每分鐘、每日、token 數等限制。
    - 同一個 Google Cloud project 的 API keys 通常共享 quota。
    - 本 app 每次完整生成會呼叫多次模型，所以比單次聊天更容易碰到額度限制。
    - 不要把 API key 貼到 GitHub、公開文件或截圖裡。
    - 如果你在 Streamlit Cloud secrets 放自己的 key，代表所有使用者會共用你的 quota。
    - 如果讓使用者在側邊欄自己填 key，則會使用他們自己的 quota。
    """
)

st.header("5. 常見錯誤")
st.markdown(
    """
    **429 RESOURCE_EXHAUSTED**

    代表 quota 用完、免費額度不足，或該模型目前沒有可用免費額度。可以等一段時間、換模型，或使用自己的付費 / 其他 provider。

    **404 NOT_FOUND**

    代表模型名稱不存在，或你的 API key/project 不能用該模型。請按 **Refresh available models** 重新抓可用模型。

    **503 UNAVAILABLE**

    代表模型目前太多人使用或暫時不可用。通常稍後重試或換 `flash-lite` 類模型即可。
    """
)

st.header("6. 相關官方頁面")
st.markdown(
    """
    - [Google AI Studio](https://aistudio.google.com/)
    - [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart)
    - [Gemini API Models](https://ai.google.dev/gemini-api/docs/models/gemini)
    - [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/quota)
    - [Google AI Studio Rate Limit Dashboard](https://ai.dev/rate-limit)
    """
)
