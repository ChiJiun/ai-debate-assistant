# 辯論助理

這是一個用 Streamlit 製作的中文辯論準備工具。使用者可以輸入辯題、選擇正方或反方，進行查資料、申論、質詢、答辯與結辯準備，最後匯出 Word 文件。

預設辯題：

```text
政府應/不應平衡其預算
```

## 功能說明

側邊欄提供 `Skills` 區塊，可以查看每個功能目前使用的 prompt，以及該 skill 的主要功用。
各 skill prompt 依照 Google Prompting 101 的角色、任務、背景、格式四要素設計，並加入避免捏造資料、資料不足需明確說明等共同規則。

### 1. 一鍵流程

- 參考 multi-agent coordinator 的做法，把辯論準備拆成可選步驟
- 可選擇要執行的 agent：查詢資料、生成申論、分析申論、生成質詢、生成答辯、生成結辯、分析結辯
- 每一步會寫入共用辯論記憶，後續 agent 會讀取前面結果
- 會顯示流程追蹤，包含開始、完成、失敗與錯誤訊息
- 完成後自動把結果回填到各分頁，也可匯出到 Word

### 2. 查詢資料

- 手動貼上資料、新聞摘要、課本內容或自己整理的素材
- 一鍵自動查資料：LLM 產生搜尋關鍵字與取回筆數，Tavily 上網查資料，LLM 再整理結果
- 整理資料摘要
- 區分正方可用資料、反方可用資料與可查證的證據方向
- 保留來源連結，匯出時可一起放入 Word 文件

### 3. 申論

- 根據辯題、手動資料或查詢資料生成申論稿
- 可選正方或反方
- 可自行輸入申論與結辯時間，預設 3 分鐘
- 可貼上自己的申論稿，讓助理分析：
  - 優點
  - 主要問題
  - 可能被攻擊的地方
  - 如何補強
  - 建議改寫版本

### 4. 質詢

- 根據對方申論稿、資料或辯題生成質詢問題
- 質詢與答辯支援多輪一來一回練習
- 質詢會優先找出對方申論中的邏輯瑕疵、證據不足、定義模糊或較弱論述
- 輸出簡短、單一、可直接提問的問題，不附過多分析
- 可輸入質詢問題，模擬對方可能如何回答，並保留前文繼續追問

### 5. 答辯

- 輸入被質詢的問題，生成答辯內容
- 產生：
  - 一來一回答辯
  - 15 到 30 秒短回答
- 輸出精簡的對方問、我方答、可能追問與轉回主線
- 可輸入自己的答辯回答，讓系統根據前文模擬對方下一輪追問

### 6. 結辯

- 綜合資料、申論、質詢與答辯生成結辯稿
- 結辯套用側邊欄的講稿時間設定
- 可貼上結辯稿進行分析
- 分析內容包含：
  - 是否抓住主要爭點
  - 是否比較雙方
  - 是否說清楚我方為何勝
  - 遺漏的關鍵內容
  - 建議改寫版本

### 7. 匯出

- 將目前已產生的資料匯出成 Word DOCX
- 會包含辯題、立場、模型設定、一鍵流程紀錄、查詢資料、申論、質詢、答辯、結辯與來源

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
3. 到「查詢資料」分頁選擇資料時間範圍：不限、過去一天、過去一週、過去一個月、過去一年
4. 選擇搜尋深度：快速、標準、進階
5. 點擊「自動查資料並整理」
6. 系統會讓 LLM 自行判斷需要搜尋哪些關鍵字與每組取回幾筆結果，並顯示實際交給 Tavily 的搜尋關鍵字、搜尋結果、來源與整理摘要

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
