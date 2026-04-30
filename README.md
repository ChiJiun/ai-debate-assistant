# 辯論助理

這是一個用 Streamlit 製作的中文辯論準備工具。使用者可以輸入辯題、選擇正方或反方，進行查資料、申論、質詢、答辯與結辯準備，最後匯出 Word 文件。

預設辯題：

```text
政府應/不應平衡其預算
```

## 功能說明

### 1. 查詢資料

- 手動貼上資料、新聞摘要、課本內容或自己整理的素材
- 一鍵自動查資料：LLM 產生乾淨搜尋關鍵字，Tavily 依照關鍵字上網查資料，LLM 再整理結果
- 整理資料摘要
- 區分正方可用資料、反方可用資料與可查證的證據方向
- 保留來源連結，匯出時可一起放入 Word 文件

### 2. 申論

- 根據辯題、手動資料或查詢資料生成申論稿
- 可選正方或反方
- 可自行輸入申論與結辯時間，預設 3 分鐘
- 可貼上自己的申論稿，讓助理分析：
  - 優點
  - 主要問題
  - 可能被攻擊的地方
  - 如何補強
  - 建議改寫版本

### 3. 質詢

- 根據對方申論稿、資料或辯題生成質詢問題
- 質詢與答辯以一來一回的短問答為主
- 質詢會優先找出對方申論中的邏輯瑕疵、證據不足、定義模糊或較弱論述
- 輸出簡短、單一、可直接提問的問題，不附過多分析
- 可輸入質詢問題，模擬對方可能如何回答，並產生追問建議

### 4. 答辯

- 輸入被質詢的問題，生成答辯內容
- 產生：
  - 一來一回答辯
  - 15 到 30 秒短回答
- 輸出精簡的對方問、我方答、可能追問、我方再答與轉回主線
- 可貼上自己的答辯回答，分析是否正面回答、是否被對方框架帶走，以及如何改寫

### 5. 結辯

- 綜合資料、申論、質詢與答辯生成結辯稿
- 結辯套用側邊欄的講稿時間設定
- 可貼上結辯稿進行分析
- 分析內容包含：
  - 是否抓住主要爭點
  - 是否比較雙方
  - 是否說清楚我方為何勝
  - 遺漏的關鍵內容
  - 建議改寫版本

### 6. 匯出

- 將目前已產生的資料匯出成 Word DOCX
- 會包含辯題、立場、模型設定、查詢資料、申論、質詢、答辯、結辯與來源

## 支援的 LLM

- Gemini / Google AI Studio
- OpenAI
- Claude
- Grok
- DeepSeek
- Qwen
- OpenRouter
- Ollama

預設使用：

```text
Gemini / Google AI Studio
gemini-2.5-flash-lite
```

Ollama 是本機模型，不需要 API key。其他線上 provider 通常需要使用者自行提供 API key。

## 上網查資料

目前查資料功能使用 Tavily API。

Tavily 不是 LLM，也不是 Google 本身。它的角色類似「給 AI app 使用的網路搜尋工具」：負責把關鍵字送去搜尋，回傳標題、摘要與來源連結。LLM 則負責分析辯題、規劃搜尋關鍵字，並閱讀 Tavily 回傳的搜尋結果後進行整理、分析與總結。

使用方式：

1. 到 Tavily 建立 API key
2. 在側邊欄填入 `Tavily API key`
3. 到「查詢資料」分頁設定 LLM 要產生幾組搜尋關鍵字
4. 自行輸入每組關鍵字搜尋結果數量，最少可設為 1，最多 20
5. 選擇資料時間範圍：不限、過去一天、過去一週、過去一個月、過去一年
6. 選擇搜尋深度：快速、標準、進階
7. 點擊「自動查資料並整理」
8. 系統會顯示 LLM 實際交給 Tavily 的搜尋關鍵字、搜尋結果、來源與整理摘要

Tavily 官方文件：

```text
https://docs.tavily.com/api-reference/endpoint/search
```

## Google AI Studio 免費使用

1. 前往 Google AI Studio
2. 建立 Gemini API key
3. 在 app 側邊欄選擇 `Gemini / Google AI Studio`
4. 貼上 API key
5. 點 `Refresh available models`
6. 選擇可用模型

常見錯誤：

- `429`：額度或速率限制，請少產生一些內容、稍後重試，或換 API key/provider
- `404`：模型名稱不可用，請刷新模型清單或改選模型
- `503`：模型暫時太忙，系統會自動重試，仍失敗時請稍後再試或換輕量模型

## 安裝

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

可在 `.env` 設定預設 key：

```text
OPENAI_API_KEY=your_openai_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
XAI_API_KEY=your_xai_grok_api_key_here
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DASHSCOPE_API_KEY=your_qwen_dashscope_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

DEFAULT_PROVIDER=Gemini
DEFAULT_MODEL=gemini-2.5-flash-lite
```

也可以不設定 `.env`，直接在 app 側邊欄貼 API key。

## 執行

```bash
streamlit run app.py
```

## 專案結構

```text
ai-debate-assistant/
  app.py
  requirements.txt
  .env.example
  README.md

  skills/
    research.py
    constructive.py
    questioning.py
    defense.py
    closing.py

  utils/
    openai_client.py
    research_client.py
    docx_exporter.py
    error_messages.py
    prompts.py
```
