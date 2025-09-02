# Discord Bot API 專案

這是一個使用 FastAPI + Discord.py 的 Discord Bot API 專案，支援 HTTP API 接收訊息並轉發到 Discord，以及 WebSocket 即時回饋。

## 專案結構

```
project/
│── __init__.py           # 專案初始化
│── app.py                # FastAPI 主應用程式
│── bot.py                # Discord Bot 類別與事件處理
│── config.py             # 環境變數與設定
│── models.py             # Pydantic 資料模型
│── routes.py             # FastAPI API 路由
│── websocket_manager.py  # WebSocket 管理
│── tasks.py              # 背景任務（queue → Discord）
│── main.py               # 主啟動腳本
│── README.md             # 專案說明
```

## 功能特色

- **HTTP API**: 接收訊息並轉發到 Discord 頻道
- **WebSocket**: 即時接收伺服器回饋（轉送結果、錯誤、狀態）
- **Discord Bot**: 監聽伺服器事件（成員加入/離開、頻道變更等）
- **訊息佇列**: 非阻塞的訊息處理機制
- **認證**: 可選的 Bearer Token 認證
- **CORS**: 支援跨域請求

## 環境變數

創建 `.env` 檔案：

```env
# Discord Bot 配置
DISCORD_TOKEN=your_discord_bot_token_here
DISCORD_CHANNEL_ID=1234567890123456789

# API 認證（可選）
API_AUTH_TOKEN=your_api_auth_token_here

# 伺服器配置
PORT=8000
```

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 啟動方式

### 使用 uvicorn 直接啟動

```bash
uvicorn project.app:app --host 0.0.0.0 --port 8000
```

## API 端點

### 發送訊息
```
POST /api/v1/send-message
Content-Type: application/json
Authorization: Bearer <token> (可選)

{
  "content": "Hello Discord!",
  "channel_id": 1234567890123456789,  // 可選，不指定則使用預設頻道
  "embed": { ... }  // 可選，Discord Embed 物件
}
```

### 查詢狀態
```
GET /api/v1/status          # Bot 狀態
GET /api/v1/servers         # 所有伺服器
GET /api/v1/health          # 健康檢查
```

### WebSocket
```
WS /api/v1/ws               # WebSocket 連線
```

## Discord Bot 命令

- `!ping` - 測試 Bot 延遲
- `!status` - 顯示 Bot 狀態
- `!servers` - 列出所有伺服器
- `!channels` - 列出當前伺服器頻道

## WebSocket 訊息類型

- `connection` - 連線建立
- `status` - Bot 狀態更新
- `message` - 收到 Discord 訊息
- `reaction` - 收到 Discord 反應
- `success` - 訊息發送成功
- `error` - 錯誤訊息

## 開發說明

- 使用 `lifespan` 事件處理器管理應用程式生命週期
- 背景任務處理訊息佇列，避免阻塞 HTTP 請求
- WebSocket 管理器處理多個連線
- 模組化設計，易於維護和擴展
