# LINE 智能聊天機器人

一個功能完整的 LINE 聊天機器人，整合多種 AI 服務，具備智能回應和自動備援機制。

## 功能特色

- **多重 AI 整合**: OpenAI GPT-4o、Google Gemini、Hugging Face
- **智能備援系統**: 自動切換可用的 AI 服務
- **LINE 官方 API**: 完整支援 LINE Messaging API
- **網頁管理介面**: 監控面板和測試功能
- **容錯設計**: 確保服務穩定運行

## 快速部署

### Vercel 部署

1. Fork 此專案到你的 GitHub
2. 在 Vercel 連接 GitHub 倉庫
3. 設置環境變數:
   - `LINE_CHANNEL_ACCESS_TOKEN`
   - `LINE_CHANNEL_SECRET`
   - `OPENAI_API_KEY` (可選)
   - `GEMINI_API_KEY` (可選)
   - `HUGGINGFACE_TOKEN` (可選)
   - `SESSION_SECRET`

4. 部署完成後，將 webhook URL 設置為: `https://你的vercel網址.vercel.app/webhook`

### 本地開發

```bash
pip install -r requirements_vercel.txt
python main.py
```

## 環境變數設置

| 變數名稱 | 描述 | 必要性 |
|---------|------|-------|
| LINE_CHANNEL_ACCESS_TOKEN | LINE Bot 存取權杖 | 必要 |
| LINE_CHANNEL_SECRET | LINE Bot 頻道密鑰 | 必要 |
| OPENAI_API_KEY | OpenAI API 金鑰 | 可選 |
| GEMINI_API_KEY | Google Gemini API 金鑰 | 可選 |
| HUGGINGFACE_TOKEN | Hugging Face API 權杖 | 可選 |
| SESSION_SECRET | Flask 會話密鑰 | 建議 |

## LINE Bot 設置

1. 前往 [LINE Developers Console](https://developers.line.biz/)
2. 建立 Messaging API 頻道
3. 取得 Channel Access Token 和 Channel Secret
4. 設置 Webhook URL: `https://你的網址/webhook`
5. 啟用 Webhook 功能

## API 金鑰取得

### OpenAI API
- 網址: https://platform.openai.com/api-keys
- 費用: 按使用量計費

### Google Gemini API  
- 網址: https://makersuite.google.com/app/apikey
- 費用: 大量免費額度

### Hugging Face API
- 網址: https://huggingface.co/settings/tokens
- 費用: 免費

## 專案結構

```
├── main.py              # 應用程式入口
├── app.py               # Flask 應用主檔
├── line_bot.py          # LINE Bot 服務
├── openai_service.py    # AI 服務整合
├── templates/           # 網頁模板
├── static/             # 靜態檔案
├── vercel.json         # Vercel 配置
└── requirements_vercel.txt # 依賴套件
```

## 使用說明

部署完成後，用戶可以透過 LINE 與機器人對話。系統會自動選擇可用的 AI 服務提供回應。

訪問 `/` 查看狀態頁面
訪問 `/dashboard` 查看監控面板

## 技術支援

如有問題，請檢查:
1. 環境變數是否正確設置
2. LINE webhook 是否正確配置
3. API 金鑰是否有效且有足夠額度