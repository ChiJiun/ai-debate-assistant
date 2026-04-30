from __future__ import annotations


def explain_error(error: Exception) -> tuple[str, str]:
    message = str(error)
    lower_message = message.lower()

    if "resource_exhausted" in lower_message or "429" in message or "quota" in lower_message:
        return (
            "配額或速率限制錯誤",
            "你的 API key 目前 quota 不足、免費額度用完，或短時間請求太多。請稍後重試、少勾一些生成項目、換較輕量模型，或改用另一組 API key/provider。",
        )

    if "not_found" in lower_message or "404" in message or "model" in lower_message and "not found" in lower_message:
        return (
            "模型不存在或不可用",
            "你選的模型名稱可能已下架、拼錯，或你的 API key/project 不支援。請按 Refresh available models 重新抓可用模型，或選 Custom model 輸入正確模型名。",
        )

    if "unavailable" in lower_message or "503" in message or "high demand" in lower_message:
        return (
            "模型暫時忙碌",
            "供應商目前流量太高或模型暫時不可用。請稍後重試，或換成 flash-lite / 較小模型，必要時改用其他 provider。",
        )

    if "unauthorized" in lower_message or "401" in message or "invalid api key" in lower_message:
        return (
            "API key 無效",
            "請確認 API key 是否貼錯、已過期，或不是所選 provider 的 key。建議重新建立 key 後再貼一次。",
        )

    if "forbidden" in lower_message or "403" in message or "permission" in lower_message:
        return (
            "權限不足",
            "你的 API key 或專案沒有權限使用這個模型/API。請換模型、檢查 provider 後台權限，或使用有權限的 API key。",
        )

    if "timeout" in lower_message or "timed out" in lower_message:
        return (
            "連線逾時",
            "模型回應太慢或網路不穩。請重試、少勾一些生成項目，或改用較快的模型。",
        )

    if "connection" in lower_message or "connect" in lower_message:
        return (
            "連線失敗",
            "請檢查網路、Base URL 是否正確。如果使用 Ollama，請確認本機 Ollama server 已啟動。",
        )

    if "missing" in lower_message and "api key" in lower_message:
        return (
            "缺少 API key",
            "請在側邊欄填入該 provider 的 API key，或在部署環境的 secrets/.env 裡設定對應 key。",
        )

    return (
        "未知生成錯誤",
        "請先確認 API key、模型名稱與網路狀態。若仍失敗，換較輕量模型或其他 provider 再試。",
    )
