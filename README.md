# Debate Assistant Agent MVP

A simple Streamlit web app that helps users prepare debate materials quickly and export them as a Word document.

## Features

- Debate motion input
- Side options: 正方, 反方, 雙方
- Time limits: 1 分鐘, 2 分鐘, 3 分鐘
- Output styles: 正式辯論, 課堂報告, 簡短口語
- Fast generation mode
- Motion analysis
- Arguments for both sides
- Constructive speeches
- Cross-examination questions
- Defense answers
- Closing speeches
- DOCX export
- User-selectable LLM provider and model
- User-entered API key in the app sidebar
- Customizable generation skills
- Skill JSON import and download

## Supported LLM Providers

- OpenAI
- Gemini
- Claude
- OpenRouter, including open-source and free-tagged hosted models
- Ollama for local open-source models

OpenRouter and Ollama also expose a Base URL field in the sidebar. For Ollama, start the local server first and use a local model name such as `llama3.1`, `mistral`, or `qwen2.5`.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Edit `.env` if you want default keys and model settings:

```text
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
DEFAULT_PROVIDER=OpenAI
DEFAULT_MODEL=gpt-4.1-mini
```

You can also leave `.env` empty and paste the API key directly into the app sidebar. API keys entered in the UI are not included in the DOCX export.

## Custom Skills

The app sidebar includes a Skills section where users can edit the generation instructions for:

- Motion analysis
- Argument generation
- Constructive speeches
- Cross-examination
- Defense answers
- Closing speeches

Users can download the current skill set as `debate-assistant-skills.json` and import it later. This makes it easy to create templates for different debate formats, classes, languages, or judging styles.

The closing speech skill can include `{previous_materials}` where earlier generated sections should be inserted.

## Run

```bash
streamlit run app.py
```

Then open the local URL shown by Streamlit.

## Project Structure

```text
debate-assistant/
  app.py
  requirements.txt
  .env.example
  README.md

  skills/
    motion_analysis.py
    argument_generation.py
    constructive_speech.py
    cross_examination.py
    defense.py
    closing.py

  utils/
    openai_client.py
    docx_exporter.py
    prompts.py
```
