from __future__ import annotations

import streamlit as st

from skills.argument_generation import generate_arguments
from skills.closing import generate_closing_speeches
from skills.constructive_speech import generate_constructive_speeches
from skills.cross_examination import generate_cross_examination
from skills.defense import generate_defense_answers
from skills.motion_analysis import generate_motion_analysis
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
from utils.skill_templates import DEFAULT_SKILL_TEMPLATES, templates_from_json, templates_to_json


st.set_page_config(page_title="Debate Assistant", page_icon="🎙️", layout="wide")

st.markdown(
    """
    <style>
    section[data-testid="stSidebar"] {
        min-width: 320px;
    }
    div[data-testid="stButton"] > button {
        min-height: 2.8rem;
    }
    div[data-testid="stCheckbox"] label {
        min-height: 2.4rem;
        align-items: center;
    }
    textarea {
        min-height: 120px !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


SECTION_LABELS = {
    "motion_analysis": "辯題分析",
    "arguments": "正反方論點素材",
    "constructive": "立論稿",
    "cross_examination": "交叉質詢",
    "defense": "防守回答",
    "closing": "結辯稿",
}

SECTION_ORDER = list(SECTION_LABELS)

MODEL_OPTIONS = {
    "OpenAI": [
        "gpt-4.1-mini",
        "gpt-4.1",
        "gpt-4o-mini",
        "gpt-4o",
        "o4-mini",
        "o3",
    ],
    "Gemini": [
        "gemini-2.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-2.5-pro",
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
    ],
    "Claude": [
        "claude-3-5-haiku-latest",
        "claude-3-5-sonnet-latest",
        "claude-3-7-sonnet-latest",
        "claude-3-opus-latest",
    ],
    "Grok": [
        "grok-4.20-reasoning",
        "grok-4.20",
        "grok-4",
        "grok-code-fast-1",
    ],
    "DeepSeek": [
        "deepseek-v4-flash",
        "deepseek-v4-pro",
        "deepseek-chat",
        "deepseek-reasoner",
    ],
    "Qwen": [
        "qwen-plus",
        "qwen3-max",
        "qwen3.5-flash",
        "qwen-turbo",
        "qwen-max",
    ],
    "OpenRouter": [
        "meta-llama/llama-3.1-8b-instruct:free",
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "deepseek/deepseek-chat",
        "qwen/qwen3-coder:free",
        "x-ai/grok-4",
    ],
    "Ollama": ["llama3.1", "llama3.2", "mistral", "qwen2.5", "gemma2"],
}

PROVIDER_HELP = {
    "OpenAI": "OpenAI official API.",
    "Gemini": "Google Gemini API.",
    "Claude": "Anthropic Claude API.",
    "Grok": "xAI Grok API.",
    "DeepSeek": "DeepSeek official OpenAI-compatible API.",
    "Qwen": "Alibaba Cloud DashScope / Model Studio OpenAI-compatible API.",
    "OpenRouter": "Aggregator for many hosted models, including free-tagged open models.",
    "Ollama": "Local open-source models running on your computer. No API key is required.",
}

PROVIDER_LABELS = {
    "OpenAI": "OpenAI",
    "Gemini": "Gemini",
    "Claude": "Claude",
    "Grok": "Grok",
    "DeepSeek": "DeepSeek",
    "Qwen": "Qwen",
    "OpenRouter": "OpenRouter",
    "Ollama": "Ollama (no API key)",
}


def initialize_state() -> None:
    st.session_state.setdefault("generated_sections", {})
    st.session_state.setdefault("last_settings", {})
    st.session_state.setdefault("provider_model_options", {})
    st.session_state.setdefault("selected_sections", SECTION_ORDER.copy())
    for key, value in DEFAULT_SKILL_TEMPLATES.items():
        st.session_state.setdefault(f"skill_template_{key}", value)


def generate_all(
    motion: str,
    side: str,
    time_limit: str,
    output_style: str,
    llm_config: LLMConfig,
    skill_templates: dict[str, str],
    selected_sections: list[str],
) -> dict[str, str]:
    sections: dict[str, str] = {}
    total_steps = len(selected_sections)
    current_step = 0

    def update_progress(text: str) -> None:
        nonlocal current_step
        current_step += 1
        progress.progress(int((current_step - 1) / total_steps * 100), text=text)

    progress = st.progress(0, text="Analyzing motion...")

    if "motion_analysis" in selected_sections:
        update_progress("Analyzing motion...")
        sections["motion_analysis"] = generate_motion_analysis(
            motion,
            side,
            time_limit,
            output_style,
            llm_config,
            skill_templates,
        )

    if "arguments" in selected_sections:
        update_progress("Building arguments...")
        sections["arguments"] = generate_arguments(motion, side, time_limit, output_style, llm_config, skill_templates)

    if "constructive" in selected_sections:
        update_progress("Writing constructive speeches...")
        sections["constructive"] = generate_constructive_speeches(
            motion,
            side,
            time_limit,
            output_style,
            llm_config,
            skill_templates,
        )

    if "cross_examination" in selected_sections:
        update_progress("Preparing cross-examination...")
        sections["cross_examination"] = generate_cross_examination(
            motion,
            side,
            time_limit,
            output_style,
            llm_config,
            skill_templates,
        )

    if "defense" in selected_sections:
        update_progress("Drafting defense answers...")
        sections["defense"] = generate_defense_answers(
            motion,
            side,
            time_limit,
            output_style,
            llm_config,
            skill_templates,
        )

    if "closing" in selected_sections:
        update_progress("Writing closing speeches...")
        previous_materials = "\n\n".join(sections.values()) or "No previous sections were selected."
        sections["closing"] = generate_closing_speeches(
            motion,
            side,
            time_limit,
            output_style,
            previous_materials,
            llm_config,
            skill_templates,
        )

    progress.progress(100, text="Done.")
    return sections


def render_sections(sections: dict[str, str]) -> None:
    for key in SECTION_ORDER:
        if key not in sections:
            continue
        with st.expander(SECTION_LABELS[key], expanded=True):
            st.markdown(sections[key])


def get_current_skill_templates() -> dict[str, str]:
    return {
        key: st.session_state.get(f"skill_template_{key}", value)
        for key, value in DEFAULT_SKILL_TEMPLATES.items()
    }


def render_google_ai_studio_guide() -> None:
    with st.expander("Google AI Studio 免費使用教學", expanded=False):
        st.markdown(
            """
            1. 前往 [Google AI Studio](https://aistudio.google.com/) 並登入 Google 帳號。
            2. 點 **Get API key** 或 **API keys**，建立新的 Gemini API key。
            3. 回到本 app，選擇 **LLM provider: Gemini**。
            4. 將 API key 貼到側邊欄的 **API key** 欄位。
            5. 點 **Refresh available models**，從下拉選單選可用模型。
            6. 建議先試 `gemini-2.5-flash-lite` 或 `gemini-2.5-flash`。

            常見錯誤：

            - `429`: 免費額度或速率限制用完。少勾生成項目、稍後重試或換 key/provider。
            - `404`: 模型名稱不可用。按 Refresh available models 重新抓模型。
            - `503`: 模型太忙。系統會自動重試，仍失敗時請稍後再試或換輕量模型。

            官方連結：
            [Gemini API Quickstart](https://ai.google.dev/gemini-api/docs/quickstart) |
            [Models](https://ai.google.dev/gemini-api/docs/models/gemini) |
            [Rate Limits](https://ai.google.dev/gemini-api/docs/quota)
            """
        )


def show_actionable_error(error: Exception, context: str) -> None:
    title, suggestion = explain_error(error)
    with st.error(f"{context}: {title}"):
        st.write(suggestion)
        with st.expander("Technical details"):
            st.code(str(error))


initialize_state()

st.title("Debate Assistant")
st.caption("快速產生辯題分析、攻防素材、質詢題、結辯稿，並匯出 Word 文件。")

st.info("第一次使用 Gemini / Google AI Studio？展開下方免費使用教學。")
render_google_ai_studio_guide()

with st.sidebar:
    st.caption("Google AI Studio 教學在主畫面上方。")

    st.header("Settings")
    side = st.radio("Side option", ["正方", "反方", "雙方"], index=2)
    time_limit = st.selectbox("Time limit", ["1 分鐘", "2 分鐘", "3 分鐘"], index=1)
    output_style = "辯論助理"
    st.caption("輸出風格固定為辯論助理：清楚、實用，適合準備攻防與講稿。")
    research_mode = st.selectbox("Research mode", ["快速生成，不上網查資料", "保留功能：上網查資料"])
    st.caption("目前不會自動上網查資料；模型只會根據辯題與 prompt 產生準備方向。")

    st.header("LLM")
    providers = ["OpenAI", "Gemini", "Claude", "Grok", "DeepSeek", "Qwen", "OpenRouter", "Ollama"]
    default_provider_index = providers.index(DEFAULT_PROVIDER) if DEFAULT_PROVIDER in providers else providers.index("Gemini")
    provider = st.selectbox(
        "LLM provider",
        providers,
        index=default_provider_index,
        format_func=lambda value: PROVIDER_LABELS[value],
        help="先選 LLM 供應商，再選該供應商可用的模型。",
    )
    st.caption(PROVIDER_HELP[provider])

    default_key = get_default_api_key(provider)
    api_key = ""
    if provider != "Ollama":
        api_key = st.text_input(
            "API key",
            value="",
            type="password",
            placeholder="Paste key here, or leave blank to use .env",
        )
        if default_key:
            st.caption("A default key is available from `.env`; this field can override it.")
    else:
        st.caption("No API key required. Make sure Ollama is running locally before generating.")

    base_url = ""
    if provider in DEFAULT_BASE_URLS:
        base_url = st.text_input("Base URL", value=DEFAULT_BASE_URLS[provider])

    refresh_models = st.button("Refresh available models", use_container_width=True)
    if refresh_models:
        try:
            fetched_models = list_available_models(
                LLMConfig(
                    provider=provider,
                    model=DEFAULT_MODELS.get(provider, ""),
                    api_key=api_key,
                    base_url=base_url,
                )
            )
            if fetched_models:
                st.session_state.provider_model_options[provider] = fetched_models
                st.success(f"Loaded {len(fetched_models)} models for {provider}.")
            else:
                st.warning("No compatible text-generation models were returned.")
        except Exception as exc:
            show_actionable_error(exc, "Could not refresh models")

    provider_models = st.session_state.provider_model_options.get(provider, MODEL_OPTIONS[provider])
    model_choices = provider_models + ["Custom model"]
    selected_model = st.selectbox("Model", model_choices)
    custom_model = ""
    if selected_model == "Custom model":
        custom_model = st.text_input("Custom model name", value=DEFAULT_MODELS.get(provider, ""))
    model = custom_model.strip() or selected_model

    st.header("Skills")
    uploaded_skill_file = st.file_uploader("Import skill JSON", type=["json"])
    if uploaded_skill_file is not None:
        try:
            imported_templates = templates_from_json(uploaded_skill_file.getvalue().decode("utf-8"))
            for key, value in imported_templates.items():
                st.session_state[f"skill_template_{key}"] = value
            st.success("Skill templates imported.")
        except Exception as exc:
            st.error(f"Import failed: {exc}")

    if st.button("Reset skills to default", use_container_width=True):
        for key, value in DEFAULT_SKILL_TEMPLATES.items():
            st.session_state[f"skill_template_{key}"] = value
        st.rerun()

    with st.expander("Customize generation skills"):
        for key, title in SECTION_LABELS.items():
            st.text_area(
                title,
                key=f"skill_template_{key}",
                height=180,
                help="Edit the instruction used for this generated section.",
            )
        st.caption("Closing skill can use `{previous_materials}` to insert earlier generated sections.")

    st.download_button(
        "Download skill JSON",
        data=templates_to_json(get_current_skill_templates()),
        file_name="debate-assistant-skills.json",
        mime="application/json",
        use_container_width=True,
    )

st.subheader("選擇要生成的內容")
st.caption("只勾需要的段落，可以省 API 額度並降低等待時間。")
selected_sections = []
section_columns = st.columns(3)
for index, key in enumerate(SECTION_ORDER):
    with section_columns[index % 3]:
        checked = st.checkbox(
            SECTION_LABELS[key],
            value=key in st.session_state.selected_sections,
            key=f"select_section_{key}",
        )
        if checked:
            selected_sections.append(key)
st.session_state.selected_sections = selected_sections

motion = st.text_area(
    "Debate motion",
    placeholder="例如：本院認為高中應禁止學生使用智慧型手機",
    height=110,
)

generate_clicked = st.button("Generate Debate Materials", type="primary", use_container_width=True)

if research_mode != "快速生成，不上網查資料":
    st.info("上網查資料模式目前尚未實作；這次仍會用快速生成，不會真的連網搜尋資料。")

if generate_clicked:
    if not motion.strip():
        st.warning("Please enter a debate motion first.")
    elif not selected_sections:
        st.warning("Please select at least one material to generate.")
    else:
        settings = {
            "Motion": motion.strip(),
            "Side": side,
            "Time Limit": time_limit,
            "Output Style": "辯論助理",
            "Research Mode": research_mode,
            "LLM Provider": provider,
            "Model": model,
            "Generated Materials": ", ".join(SECTION_LABELS[key] for key in selected_sections),
            "Skill Template": "Customizable JSON",
        }
        llm_config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
        )
        try:
            with st.spinner("Generating debate materials..."):
                st.session_state.generated_sections = generate_all(
                    motion.strip(),
                    side,
                    time_limit,
                    output_style,
                    llm_config,
                    get_current_skill_templates(),
                    selected_sections,
                )
                st.session_state.last_settings = settings
            st.success("Debate materials generated.")
        except OpenAIConfigError as exc:
            show_actionable_error(exc, "Generation failed")
        except Exception as exc:
            show_actionable_error(exc, "Generation failed")

if st.session_state.generated_sections:
    render_sections(st.session_state.generated_sections)

    docx_sections = {
        SECTION_LABELS[key]: value
        for key, value in st.session_state.generated_sections.items()
    }
    docx_file = build_docx(st.session_state.last_settings, docx_sections)
    st.download_button(
        "Download DOCX",
        data=docx_file,
        file_name="debate-preparation.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )
else:
    st.markdown(
        """
        Enter a motion, choose the preparation settings, and generate a complete debate pack.
        The DOCX export appears after generation.
        """
    )
