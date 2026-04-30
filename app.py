from __future__ import annotations

import streamlit as st

from skills.closing import analyze_closing, generate_closing
from skills.constructive import analyze_constructive, generate_constructive
from skills.defense import analyze_defense, generate_defense
from skills.questioning import generate_questioning, simulate_question_answer
from skills.research import summarize_research
from utils.docx_exporter import build_docx
from utils.error_messages import explain_error
from utils.openai_client import (
    DEFAULT_BASE_URLS,
    DEFAULT_MODELS,
    DEFAULT_PROVIDER,
    LLMConfig,
    OpenAIConfigError,
    get_default_api_key,
    list_available_models,
)
from utils.research_client import format_search_results, get_default_tavily_key, search_tavily


st.set_page_config(page_title="辯論助理", page_icon="🎙️", layout="wide")

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] { min-width: 320px; }
    div[data-testid="stButton"] > button { min-height: 2.8rem; }
    textarea { min-height: 120px !important; }
    </style>
    """,
    unsafe_allow_html=True,
)


MODEL_OPTIONS = {
    "OpenAI": ["gpt-4.1-mini", "gpt-4.1", "gpt-4o-mini", "gpt-4o", "o4-mini", "o3"],
    "Gemini": ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
    "Claude": ["claude-3-5-haiku-latest", "claude-3-5-sonnet-latest", "claude-3-7-sonnet-latest"],
    "Grok": ["grok-4.20-reasoning", "grok-4.20", "grok-4", "grok-code-fast-1"],
    "DeepSeek": ["deepseek-v4-flash", "deepseek-v4-pro", "deepseek-chat", "deepseek-reasoner"],
    "Qwen": ["qwen-plus", "qwen3-max", "qwen3.5-flash", "qwen-turbo", "qwen-max"],
    "OpenRouter": [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "deepseek/deepseek-chat",
        "qwen/qwen3-coder:free",
    ],
    "Ollama": ["llama3.1", "llama3.2", "mistral", "qwen2.5", "gemma2"],
}

PROVIDER_LABELS = {
    "OpenAI": "OpenAI",
    "Gemini": "Gemini / Google AI Studio",
    "Claude": "Claude",
    "Grok": "Grok",
    "DeepSeek": "DeepSeek",
    "Qwen": "Qwen",
    "OpenRouter": "OpenRouter",
    "Ollama": "Ollama（不需 API key）",
}


def initialize_state() -> None:
    defaults = {
        "motion": "政府應/不應平衡其預算",
        "side": "正方",
        "manual_material": "",
        "search_material": "",
        "research_summary": "",
        "sources_text": "",
        "constructive": "",
        "constructive_analysis": "",
        "opponent_constructive": "",
        "questioning": "",
        "question_simulation": "",
        "defense": "",
        "defense_analysis": "",
        "closing": "",
        "closing_analysis": "",
        "provider_model_options": {},
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def show_actionable_error(error: Exception, context: str) -> None:
    title, suggestion = explain_error(error)
    with st.error(f"{context}：{title}"):
        st.write(suggestion)
        with st.expander("技術細節"):
            st.code(str(error))


def render_google_ai_studio_guide() -> None:
    with st.expander("Google AI Studio 免費使用教學", expanded=False):
        st.markdown(
            """
            1. 前往 [Google AI Studio](https://aistudio.google.com/) 並登入 Google 帳號。
            2. 點 **Get API key** 或 **API keys**，建立新的 Gemini API key。
            3. 回到本 app，選擇 **LLM provider: Gemini / Google AI Studio**。
            4. 將 API key 貼到側邊欄的 **API key** 欄位。
            5. 點 **Refresh available models**，從下拉選單選可用模型。
            6. 建議先試 `gemini-2.5-flash-lite`。

            常見錯誤：`429` 是額度限制、`404` 是模型不可用、`503` 是模型暫時太忙。
            """
        )


def build_llm_config(provider: str, model: str, api_key: str, base_url: str) -> LLMConfig:
    return LLMConfig(provider=provider, model=model, api_key=api_key, base_url=base_url)


def combined_research_material() -> str:
    parts = [
        st.session_state.get("manual_material", ""),
        st.session_state.get("search_material", ""),
        st.session_state.get("research_summary", ""),
    ]
    return "\n\n".join(part for part in parts if part.strip())


def combined_all_materials() -> str:
    labeled_parts = {
        "手動輸入資料": st.session_state.get("manual_material", ""),
        "查詢資料": st.session_state.get("search_material", ""),
        "資料整理": st.session_state.get("research_summary", ""),
        "我方申論": st.session_state.get("constructive", ""),
        "對方申論": st.session_state.get("opponent_constructive", ""),
        "質詢設計": st.session_state.get("questioning", ""),
        "質詢模擬": st.session_state.get("question_simulation", ""),
        "答辯內容": st.session_state.get("defense", ""),
        "答辯分析": st.session_state.get("defense_analysis", ""),
    }
    return "\n\n".join(f"## {label}\n{value}" for label, value in labeled_parts.items() if value.strip())


def render_sources() -> None:
    if st.session_state.get("sources_text"):
        with st.expander("來源資料", expanded=False):
            st.markdown(st.session_state.sources_text)


initialize_state()

st.title("辯論助理")
st.caption("查資料、寫申論、設計質詢、準備答辯、生成結辯。")
render_google_ai_studio_guide()

with st.sidebar:
    st.header("基本設定")
    motion = st.text_area("辯題", key="motion", height=90)
    side = st.radio("你的立場", ["正方", "反方"], key="side", horizontal=True)
    time_limit = st.selectbox("申論與結辯時間", ["1 分鐘", "2 分鐘", "3 分鐘"], index=2)
    st.caption("時間設定只套用在申論稿與結辯稿；質詢與答辯以一來一回的短問答為主。")

    st.header("LLM 設定")
    providers = ["OpenAI", "Gemini", "Claude", "Grok", "DeepSeek", "Qwen", "OpenRouter", "Ollama"]
    default_provider_index = providers.index(DEFAULT_PROVIDER) if DEFAULT_PROVIDER in providers else 1
    provider = st.selectbox("LLM provider", providers, index=default_provider_index, format_func=lambda x: PROVIDER_LABELS[x])

    default_key = get_default_api_key(provider)
    api_key = ""
    if provider != "Ollama":
        api_key = st.text_input("API key", type="password", placeholder="可留空使用 .env / Streamlit secrets")
        if default_key:
            st.caption("已偵測到部署環境或 .env 有預設 key。")
    else:
        st.caption("Ollama 使用本機模型，不需要 API key。")

    base_url = ""
    if provider in DEFAULT_BASE_URLS:
        base_url = st.text_input("Base URL", value=DEFAULT_BASE_URLS[provider])

    if st.button("Refresh available models", use_container_width=True):
        try:
            fetched_models = list_available_models(build_llm_config(provider, DEFAULT_MODELS.get(provider, ""), api_key, base_url))
            if fetched_models:
                st.session_state.provider_model_options[provider] = fetched_models
                st.success(f"已載入 {len(fetched_models)} 個模型。")
            else:
                st.warning("沒有取得可用模型。")
        except Exception as exc:
            show_actionable_error(exc, "刷新模型失敗")

    provider_models = st.session_state.provider_model_options.get(provider, MODEL_OPTIONS[provider])
    selected_model = st.selectbox("模型", provider_models + ["Custom model"])
    custom_model = ""
    if selected_model == "Custom model":
        custom_model = st.text_input("自訂模型名稱", value=DEFAULT_MODELS.get(provider, ""))
    model = custom_model.strip() or selected_model
    llm_config = build_llm_config(provider, model, api_key, base_url)

    st.header("查資料設定")
    tavily_key = st.text_input("Tavily API key", type="password", placeholder="上網查資料才需要")
    if get_default_tavily_key():
        st.caption("已偵測到部署環境或 .env 有 Tavily key。")

tab_research, tab_constructive, tab_questioning, tab_defense, tab_closing, tab_export = st.tabs(
    ["查詢資料", "申論", "質詢", "答辯", "結辯", "匯出"]
)

with tab_research:
    st.subheader("查詢資料")
    st.session_state.manual_material = st.text_area(
        "手動貼上資料、課本內容、新聞摘要或你已經整理好的素材",
        value=st.session_state.manual_material,
        height=180,
    )
    search_query = st.text_input("搜尋關鍵字", value=st.session_state.motion)
    max_results = st.slider("搜尋結果數量", min_value=3, max_value=10, value=5)

    col_search, col_summarize = st.columns(2)
    with col_search:
        if st.button("上網查資料（Tavily）", use_container_width=True):
            try:
                results = search_tavily(search_query, tavily_key, max_results=max_results)
                st.session_state.search_material = format_search_results(results)
                st.session_state.sources_text = "\n".join(
                    f"- [{result.title}]({result.url})" for result in results if result.url
                )
                st.success("查詢完成。")
            except Exception as exc:
                show_actionable_error(exc, "查資料失敗")

    with col_summarize:
        if st.button("整理目前資料", use_container_width=True):
            try:
                st.session_state.research_summary = summarize_research(
                    st.session_state.motion,
                    st.session_state.side,
                    combined_research_material(),
                    llm_config,
                )
                st.success("資料整理完成。")
            except Exception as exc:
                show_actionable_error(exc, "整理資料失敗")

    if st.session_state.search_material:
        st.markdown("### 查詢結果")
        st.markdown(st.session_state.search_material)
    if st.session_state.research_summary:
        st.markdown("### 資料整理")
        st.markdown(st.session_state.research_summary)
    render_sources()

with tab_constructive:
    st.subheader("申論")
    col_generate, col_analyze = st.columns(2)
    with col_generate:
        st.markdown("### 生成申論稿")
        if st.button("生成我方申論稿", use_container_width=True):
            try:
                st.session_state.constructive = generate_constructive(
                    st.session_state.motion,
                    st.session_state.side,
                    time_limit,
                    combined_research_material(),
                    llm_config,
                )
                st.success("申論稿生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "生成申論稿失敗")
        st.text_area("我方申論稿", key="constructive", height=320)

    with col_analyze:
        st.markdown("### 分析申論稿")
        speech_to_analyze = st.text_area("貼上要分析的申論稿", height=260)
        if st.button("分析申論稿", use_container_width=True):
            try:
                st.session_state.constructive_analysis = analyze_constructive(
                    st.session_state.motion,
                    st.session_state.side,
                    speech_to_analyze or st.session_state.constructive,
                    combined_research_material(),
                    llm_config,
                )
                st.success("申論分析完成。")
            except Exception as exc:
                show_actionable_error(exc, "分析申論稿失敗")
        if st.session_state.constructive_analysis:
            st.markdown(st.session_state.constructive_analysis)

with tab_questioning:
    st.subheader("質詢")
    st.session_state.opponent_constructive = st.text_area(
        "對方申論稿 / 對方資料",
        value=st.session_state.opponent_constructive,
        height=180,
    )
    col_questions, col_simulation = st.columns(2)
    with col_questions:
        if st.button("生成質詢問題", use_container_width=True):
            try:
                st.session_state.questioning = generate_questioning(
                    st.session_state.motion,
                    st.session_state.side,
                    st.session_state.opponent_constructive,
                    combined_research_material(),
                    llm_config,
                )
                st.success("質詢問題生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "生成質詢問題失敗")
        if st.session_state.questioning:
            st.markdown(st.session_state.questioning)

    with col_simulation:
        question = st.text_area("輸入你要問對方的質詢問題", height=130)
        if st.button("模擬對方回答並給追問", use_container_width=True):
            try:
                st.session_state.question_simulation = simulate_question_answer(
                    st.session_state.motion,
                    st.session_state.side,
                    question,
                    st.session_state.opponent_constructive,
                    llm_config,
                )
                st.success("質詢模擬完成。")
            except Exception as exc:
                show_actionable_error(exc, "質詢模擬失敗")
        if st.session_state.question_simulation:
            st.markdown(st.session_state.question_simulation)

with tab_defense:
    st.subheader("答辯")
    defense_question = st.text_area("輸入你被質詢的問題", height=130)
    col_defense, col_defense_analysis = st.columns(2)
    with col_defense:
        if st.button("生成答辯內容", use_container_width=True):
            try:
                st.session_state.defense = generate_defense(
                    st.session_state.motion,
                    st.session_state.side,
                    defense_question,
                    combined_research_material(),
                    llm_config,
                )
                st.success("答辯生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "生成答辯失敗")
        st.text_area("答辯內容", key="defense", height=260)

    with col_defense_analysis:
        user_answer = st.text_area("貼上你的答辯回答，讓助理分析", height=200)
        if st.button("分析答辯回答", use_container_width=True):
            try:
                st.session_state.defense_analysis = analyze_defense(
                    st.session_state.motion,
                    st.session_state.side,
                    defense_question,
                    user_answer or st.session_state.defense,
                    llm_config,
                )
                st.success("答辯分析完成。")
            except Exception as exc:
                show_actionable_error(exc, "分析答辯失敗")
        if st.session_state.defense_analysis:
            st.markdown(st.session_state.defense_analysis)

with tab_closing:
    st.subheader("結辯")
    extra_closing_material = st.text_area("補充可納入結辯的資訊", height=150)
    closing_materials = "\n\n".join(part for part in [combined_all_materials(), extra_closing_material] if part.strip())
    col_closing, col_closing_analysis = st.columns(2)
    with col_closing:
        if st.button("生成結辯稿", use_container_width=True):
            try:
                st.session_state.closing = generate_closing(
                    st.session_state.motion,
                    st.session_state.side,
                    time_limit,
                    closing_materials,
                    llm_config,
                )
                st.success("結辯稿生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "生成結辯稿失敗")
        st.text_area("結辯稿", key="closing", height=300)

    with col_closing_analysis:
        closing_to_analyze = st.text_area("貼上要分析的結辯稿", height=220)
        if st.button("分析結辯稿", use_container_width=True):
            try:
                st.session_state.closing_analysis = analyze_closing(
                    st.session_state.motion,
                    st.session_state.side,
                    closing_to_analyze or st.session_state.closing,
                    closing_materials,
                    llm_config,
                )
                st.success("結辯分析完成。")
            except Exception as exc:
                show_actionable_error(exc, "分析結辯稿失敗")
        if st.session_state.closing_analysis:
            st.markdown(st.session_state.closing_analysis)

with tab_export:
    st.subheader("匯出")
    sections = {
        "查詢資料": st.session_state.search_material,
        "資料整理": st.session_state.research_summary,
        "我方申論": st.session_state.constructive,
        "申論分析": st.session_state.constructive_analysis,
        "對方申論 / 資料": st.session_state.opponent_constructive,
        "質詢問題": st.session_state.questioning,
        "質詢模擬": st.session_state.question_simulation,
        "答辯內容": st.session_state.defense,
        "答辯分析": st.session_state.defense_analysis,
        "結辯稿": st.session_state.closing,
        "結辯分析": st.session_state.closing_analysis,
        "來源": st.session_state.sources_text,
    }
    non_empty_sections = {title: content for title, content in sections.items() if content and content.strip()}
    st.write(f"目前可匯出 {len(non_empty_sections)} 個區塊。")
    docx_file = build_docx(
        {
            "辯題": st.session_state.motion,
            "立場": st.session_state.side,
            "模型供應商": provider,
            "模型": model,
        },
        non_empty_sections,
    )
    st.download_button(
        "下載 Word 文件",
        data=docx_file,
        file_name="debate-workbench.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
