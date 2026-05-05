from __future__ import annotations

import streamlit as st

from skills.closing import analyze_closing, generate_closing
from skills.constructive import analyze_constructive, generate_constructive
from skills.defense import generate_defense, generate_defense_followup
from skills.questioning import generate_questioning, simulate_question_answer
from skills.research import run_research_workflow
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
from utils.research_client import get_default_tavily_key
from utils.skill_catalog import SKILLS


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
    "Gemini": [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash",
    ],
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
        "search_queries": "",
        "search_material": "",
        "research_summary": "",
        "sources_text": "",
        "constructive": "",
        "constructive_analysis": "",
        "opponent_constructive": "",
        "questioning": "",
        "question_simulation": "",
        "question_dialogue": "",
        "defense": "",
        "defense_dialogue": "",
        "closing": "",
        "closing_analysis": "",
        "provider_model_options": {},
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def show_actionable_error(error: Exception, context: str) -> None:
    title, explanation, suggestion = explain_error(error)
    raw_message = " ".join(str(error).split())
    if len(raw_message) > 700:
        raw_message = raw_message[:697] + "..."

    st.error(f"{context}：{title}")
    st.markdown(f"**這是什麼錯誤：** {title}")
    st.markdown(f"**錯誤說明：** {explanation}")
    st.markdown(f"**原始錯誤訊息：** `{raw_message or '無原始錯誤訊息'}`")
    st.markdown(f"**建議處理方式：** {suggestion}")


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
        "質詢多輪紀錄": st.session_state.get("question_dialogue", ""),
        "答辯內容": st.session_state.get("defense", ""),
        "答辯多輪紀錄": st.session_state.get("defense_dialogue", ""),
    }
    return "\n\n".join(f"## {label}\n{value}" for label, value in labeled_parts.items() if value.strip())


def append_dialogue(existing: str, heading: str, content: str) -> str:
    clean_content = content.strip()
    if not clean_content:
        return existing
    block = f"## {heading}\n{clean_content}"
    return "\n\n".join(part for part in [existing.strip(), block] if part)


def display_prompt_template(prompt: str) -> str:
    return prompt.replace("{{", "{").replace("}}", "}")


def render_sources() -> None:
    if st.session_state.get("sources_text"):
        st.markdown("### 來源資料")
        for block in st.session_state.sources_text.split("\n\n## "):
            normalized_block = block if block.startswith("## ") else f"## {block}"
            lines = [line.strip() for line in normalized_block.splitlines() if line.strip()]
            if not lines:
                continue
            heading = lines[0].removeprefix("## ").strip()
            with st.expander(f"查詢：{heading}", expanded=False):
                current_title = ""
                current_url = ""
                current_summary = ""
                for line in lines[1:] + ["### END"]:
                    if line.startswith("### "):
                        if current_title:
                            st.markdown(f"**{current_title}**")
                            if current_url:
                                st.markdown(f"[開啟來源]({current_url})")
                            if current_summary:
                                st.caption(current_summary)
                            st.divider()
                        current_title = line.removeprefix("### ").strip()
                        current_url = ""
                        current_summary = ""
                    elif line.startswith("連結："):
                        current_url = line.removeprefix("連結：").strip()
                    elif line.startswith("摘要："):
                        current_summary = line.removeprefix("摘要：").strip()


initialize_state()

st.title("辯論助理")
st.caption("查資料、寫申論、設計質詢、準備答辯、生成結辯。")

with st.sidebar:
    st.header("基本設定")
    motion = st.text_area("辯題", key="motion", height=90)
    side = st.radio("你的立場", ["正方", "反方"], key="side", horizontal=True)
    speech_minutes = st.number_input(
        "申論與結辯時間（分鐘）",
        min_value=0.5,
        max_value=10.0,
        value=3.0,
        step=0.5,
        help="可自行輸入或用步進調整。時間設定只套用在申論稿與結辯稿。",
    )
    time_limit = f"{speech_minutes:g} 分鐘"
    st.caption("時間設定只套用在申論稿與結辯稿；質詢與答辯以一來一回的短問答為主。")

    st.header("LLM 設定")
    providers = ["OpenAI", "Gemini", "Claude", "Grok", "DeepSeek", "Qwen", "OpenRouter", "Ollama"]
    default_provider_index = providers.index(DEFAULT_PROVIDER) if DEFAULT_PROVIDER in providers else 1
    provider = st.selectbox("LLM provider", providers, index=default_provider_index, format_func=lambda x: PROVIDER_LABELS[x])
    if provider == "Gemini":
        with st.expander("Google AI Studio API key 教學", expanded=False):
            st.markdown(
                """
                1. 開啟 [Google AI Studio](https://aistudio.google.com/)。
                2. 點 **Get API key**，建立 Gemini API key。
                3. 回到這裡，把 key 貼到下方 **API key** 欄位。
                4. 模型建議先選 `gemini-2.5-flash-lite`。
                """
            )

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
    st.markdown("[取得 Tavily API key](https://app.tavily.com/) ｜ [Tavily Search API 文件](https://docs.tavily.com/api-reference/endpoint/search)")
    with st.expander("Tavily 使用教學", expanded=False):
        st.markdown(
            """
            1. 到 Tavily 註冊並建立 API key。
            2. 將 key 貼到上方欄位。
            3. 到「查詢資料」分頁調整資料時間範圍與搜尋深度。
            4. 點 **自動查資料並整理**。
            5. 系統會讓 LLM 決定搜尋關鍵字與每組取回筆數，交給 Tavily 搜尋，再由 LLM 整理正反方素材。

            Tavily 負責搜尋網路，LLM 負責整理、分析與生成辯論內容。
            """
        )
    if get_default_tavily_key():
        st.caption("已偵測到部署環境或 .env 有 Tavily key。")

    st.header("Skills")
    st.caption("這裡顯示各功能目前使用的 prompt 與主要用途。")
    st.info("可以把下方 prompt 複製到 ChatGPT、Gemini、Claude 或其他 AI 工具中使用；如果你有更好的模型，也不一定要透過 API。")
    with st.expander("Prompt 變數說明", expanded=False):
        st.markdown(
            """
            `{motion}`：辯題  
            `{side}`：你的立場  
            `{user_material}`：你在「貼上資料」欄位輸入的資料  
            `{source_material}`：貼上資料、Tavily 查詢結果、LLM 資料整理；申論、答辯等功能會用這包資料  
            `{opponent_material}`：對方申論或對方資料  
            `{question}`：質詢問題或被質詢問題  
            `{answer}`：你的答辯回答  
            `{dialogue_history}`：多輪質詢或答辯紀錄  
            `{materials}`：結辯用的整合資料，包含貼上資料、查詢資料、資料整理、我方申論、對方申論、質詢問題、質詢紀錄、答辯內容與答辯紀錄
            """
        )
    for skill in SKILLS.values():
        with st.expander(skill.name, expanded=False):
            st.markdown(f"**主要功用：** {skill.purpose}")
            st.markdown("**Prompt：**")
            st.code(display_prompt_template(skill.prompt), language="text")

tab_research, tab_constructive, tab_questioning, tab_defense, tab_closing, tab_export = st.tabs(
    ["查詢資料", "申論", "質詢", "答辯", "結辯", "匯出"]
)

with tab_research:
    st.subheader("查詢資料 / 貼上資料")
    st.caption("這裡可以手動貼資料，也可以用 Tavily 上網查資料；後續申論、質詢、答辯與結辯會使用這裡的資料。")
    st.session_state.manual_material = st.text_area(
        "貼上資料（課本內容、新聞摘要、網站文字、你已整理好的素材）",
        value=st.session_state.manual_material,
        height=180,
        help="即使不使用 Tavily 查資料，這裡貼上的內容也會被後續生成申論、質詢、答辯與結辯時納入上下文。",
    )
    st.caption("自動查資料流程：LLM 決定搜尋關鍵字與每組取回筆數 → Tavily 搜尋 → LLM 整理查詢結果。")
    time_range_options = ["不限", "過去一天", "過去一週", "過去一個月", "過去一年"]
    time_range_label = st.selectbox("資料時間範圍", time_range_options, index=0)
    time_range_map = {
        "不限": "",
        "過去一天": "day",
        "過去一週": "week",
        "過去一個月": "month",
        "過去一年": "year",
    }
    search_depth_options = ["快速", "標準", "進階"]
    search_depth_label = st.selectbox(
        "搜尋深度",
        search_depth_options,
        index=1,
        help="進階搜尋通常更完整，但可能較慢且消耗較多 Tavily 額度。",
    )
    search_depth_map = {"快速": "fast", "標準": "basic", "進階": "advanced"}

    if st.button("自動查資料並整理", use_container_width=True, type="primary"):
        try:
            with st.spinner("正在產生搜尋關鍵字、查詢資料並整理結果..."):
                queries, search_material, sources_text, summary = run_research_workflow(
                    st.session_state.motion,
                    st.session_state.side,
                    st.session_state.manual_material,
                    llm_config,
                    tavily_key,
                    time_range=time_range_map[time_range_label],
                    search_depth=search_depth_map[search_depth_label],
                )
                st.session_state.search_queries = queries
                st.session_state.search_material = search_material
                st.session_state.sources_text = sources_text
                st.session_state.research_summary = summary
            st.success("自動查資料與整理完成。")
        except Exception as exc:
            show_actionable_error(exc, "自動查資料失敗")

    if st.session_state.search_queries:
        with st.expander("LLM 提供給 Tavily 的搜尋計畫", expanded=False):
            st.code(st.session_state.search_queries)
    if st.session_state.search_material:
        render_sources()
    if st.session_state.research_summary:
        st.markdown("### 資料整理")
        st.markdown(st.session_state.research_summary)

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
    st.caption("左邊生成可用問題，右邊進行多輪質詢練習。")
    st.session_state.opponent_constructive = st.text_area(
        "對方申論稿 / 對方資料",
        value=st.session_state.opponent_constructive,
        height=180,
    )
    col_questions, col_simulation = st.columns(2)
    with col_questions:
        st.markdown("### 生成質詢素材")
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
        st.text_area("質詢問題", key="questioning", height=260)

    with col_simulation:
        st.markdown("### 多輪質詢練習")
        question = st.text_area("輸入你要問對方的質詢問題 / 下一輪追問", height=130)
        if st.button("送出本輪質詢", use_container_width=True):
            try:
                simulation = simulate_question_answer(
                    st.session_state.motion,
                    st.session_state.side,
                    question,
                    "\n\n".join(
                        part
                        for part in [combined_all_materials(), st.session_state.opponent_constructive]
                        if part.strip()
                    ),
                    st.session_state.question_dialogue,
                    llm_config,
                )
                round_number = st.session_state.question_dialogue.count("## 第") + 1
                st.session_state.question_simulation = simulation
                st.session_state.question_dialogue = append_dialogue(
                    st.session_state.question_dialogue,
                    f"第 {round_number} 輪質詢",
                    simulation,
                )
                st.success("質詢模擬完成。")
            except Exception as exc:
                show_actionable_error(exc, "質詢模擬失敗")
        if st.button("清空質詢紀錄", use_container_width=True):
            st.session_state.question_dialogue = ""
            st.session_state.question_simulation = ""
        if st.session_state.question_dialogue:
            st.markdown("### 質詢多輪紀錄")
            st.markdown(st.session_state.question_dialogue)

with tab_defense:
    st.subheader("答辯")
    st.caption("左邊生成可用答辯，右邊進行多輪答辯練習。")
    defense_question = st.text_area("輸入你被質詢的問題", height=130)
    col_defense, col_followup = st.columns(2)
    with col_defense:
        st.markdown("### 生成答辯素材")
        if st.button("生成答辯內容", use_container_width=True):
            try:
                st.session_state.defense = generate_defense(
                    st.session_state.motion,
                    st.session_state.side,
                    defense_question,
                    combined_all_materials(),
                    st.session_state.defense_dialogue,
                    llm_config,
                )
                st.success("答辯生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "生成答辯失敗")
        st.text_area("答辯內容", key="defense", height=260)

    with col_followup:
        st.markdown("### 多輪答辯練習")
        user_answer = st.text_area("輸入你剛剛實際回答的內容，讓對方繼續追問", height=200)
        if st.button("產生對方下一輪追問", use_container_width=True):
            try:
                answer_for_followup = user_answer or st.session_state.defense
                followup = generate_defense_followup(
                    st.session_state.motion,
                    st.session_state.side,
                    defense_question,
                    answer_for_followup,
                    combined_all_materials(),
                    st.session_state.defense_dialogue,
                    llm_config,
                )
                round_number = st.session_state.defense_dialogue.count("## 第") + 1
                st.session_state.defense_dialogue = append_dialogue(
                    st.session_state.defense_dialogue,
                    f"第 {round_number} 輪答辯",
                    "\n".join(
                        part
                        for part in [
                            f"- 我方本輪回答：{answer_for_followup}",
                            followup,
                        ]
                        if part.strip()
                    ),
                )
                st.success("對方追問生成完成。")
            except Exception as exc:
                show_actionable_error(exc, "產生對方追問失敗")
        if st.button("清空答辯紀錄", use_container_width=True):
            st.session_state.defense_dialogue = ""
            st.session_state.defense = ""

    if st.session_state.defense_dialogue:
        st.markdown("### 答辯多輪紀錄")
        st.markdown(st.session_state.defense_dialogue)

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
        "質詢多輪紀錄": st.session_state.question_dialogue,
        "答辯內容": st.session_state.defense,
        "答辯多輪紀錄": st.session_state.defense_dialogue,
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
