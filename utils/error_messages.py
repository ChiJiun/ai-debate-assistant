from __future__ import annotations


def _short_message(message: str, max_length: int = 360) -> str:
    compact = " ".join(message.split())
    if len(compact) <= max_length:
        return compact
    return compact[: max_length - 3] + "..."


def explain_error(error: Exception) -> tuple[str, str, str]:
    message = str(error)
    lower_message = message.lower()

    if "resource_exhausted" in lower_message or "429" in message or "quota" in lower_message:
        return (
            "配額或速率限制錯誤",
            "這通常代表 API key 的免費額度用完、每分鐘請求太多，或這個模型目前沒有可用 quota。Gemini 免費層特別容易遇到這個問題。",
            "請稍後重試、換較輕量模型、改用其他 provider，或使用另一組有額度的 API key。查資料時也可以降低每組搜尋結果數量。",
        )

    if "not_found" in lower_message or "404" in message or "model" in lower_message and "not found" in lower_message:
        return (
            "模型不存在或不可用",
            "你選的模型名稱可能已下架、拼錯，或你的 API key/project 不支援該模型。",
            "請按 Refresh available models 重新抓可用模型，或改選其他模型。若使用 Custom model，請確認模型名稱完全正確。",
        )

    if "unavailable" in lower_message or "503" in message or "high demand" in lower_message:
        return (
            "模型暫時忙碌",
            "供應商目前流量太高或模型暫時不可用。系統已經會自動重試：第一次等 2 秒，第二次等 4 秒；如果仍失敗才會顯示這個錯誤。",
            "請稍後再試，或換成 flash-lite / 較小模型。若 Gemini 持續 high demand，可以暫時改用 OpenRouter、DeepSeek、Qwen 或其他 provider。",
        )

    if "unauthorized" in lower_message or "401" in message or "invalid api key" in lower_message:
        return (
            "API key 無效",
            "API key 可能貼錯、過期、被撤銷，或不是目前選擇的 provider 的 key。",
            "請重新複製 key，確認 provider 選對；必要時到 provider 後台重新建立 API key。",
        )

    if "forbidden" in lower_message or "403" in message or "permission" in lower_message:
        return (
            "權限不足",
            "你的 API key 或專案沒有權限使用這個模型/API，或 billing / access 尚未啟用。",
            "請換模型、檢查 provider 後台權限與 billing 設定，或使用有權限的 API key。",
        )

    if "timeout" in lower_message or "timed out" in lower_message:
        return (
            "連線逾時",
            "模型或搜尋服務回應太慢，也可能是網路不穩。",
            "請重試、改用較快模型，或降低搜尋結果數量。若使用 Ollama，請確認本機模型已載入完成。",
        )

    if "connection" in lower_message or "connect" in lower_message:
        return (
            "連線失敗",
            "app 無法連到 provider、Tavily 或本機 Ollama server。",
            "請檢查網路、Base URL 是否正確。如果使用 Ollama，請確認 Ollama 已啟動且 Base URL 通常是 http://localhost:11434。",
        )

    if "missing" in lower_message and "api key" in lower_message:
        return (
            "缺少 API key",
            "目前選擇的功能需要 API key，但 app 沒有收到 key。",
            "請在側邊欄填入該 provider 的 API key，或在 Streamlit secrets / .env 裡設定對應 key。Tavily 查資料也需要 Tavily API key。",
        )

    return (
        "未知生成錯誤",
        "目前無法判斷是哪一類錯誤，可能和 API key、模型、網路、provider 暫時狀態或輸入內容有關。",
        f"請先確認 API key、模型名稱與網路狀態，必要時換較輕量模型或其他 provider。錯誤摘要：{_short_message(message)}",
    )
