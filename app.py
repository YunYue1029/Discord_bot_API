import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import validate_config, HOST, PORT, DISCORD_TOKEN
from .websocket_manager import WebSocketManager
from .bot import DiscordBot
from .tasks import DiscordSenderTask
from .routes import router, set_globals

# 配置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 全域變數
discord_bot: DiscordBot = None
message_queue: asyncio.Queue = None
websocket_manager: WebSocketManager = None
sender_task: DiscordSenderTask = None
bot_task: asyncio.Task = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """應用程式生命週期管理"""
    global discord_bot, message_queue, websocket_manager, sender_task, bot_task
    
    # 啟動事件
    logger.info("正在啟動 Discord Bot...")
    
    # 驗證配置
    validate_config()
    
    # 初始化組件
    message_queue = asyncio.Queue()
    websocket_manager = WebSocketManager()
    
    # 創建 Discord Bot 實例
    discord_bot = DiscordBot(websocket_manager)
    
    # 設定路由的全域變數
    set_globals(message_queue, discord_bot, websocket_manager)
    
    # 啟動 Bot 連線（背景執行）
    bot_task = asyncio.create_task(discord_bot.start(DISCORD_TOKEN))
    
    # 創建並啟動訊息發送任務
    sender_task = DiscordSenderTask(message_queue, discord_bot)
    asyncio.create_task(sender_task.start())
    
    logger.info("Discord Bot 啟動任務已建立")
    
    yield  # 應用程式運行期間
    
    # 關閉事件
    logger.info("正在關閉 Discord Bot...")
    
    # 停止訊息發送任務
    if sender_task:
        await sender_task.stop()
    
    # 取消 Bot 任務
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    
    # 關閉 Discord Bot 連線
    if discord_bot:
        await discord_bot.close()
    
    logger.info("Discord Bot 已關閉")

# 創建 FastAPI 應用
app = FastAPI(
    title="Discord Bot API", 
    version="1.0.0", 
    lifespan=lifespan,
    description="Discord Bot API 與 WebSocket 服務"
)

# CORS 中間件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 包含路由
app.include_router(router, prefix="/api/v1")

# 根路徑
@app.get("/")
async def root():
    return {
        "message": "Discord Bot API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "project.app:app",
        host=HOST,
        port=PORT,
        reload=False,
        log_level="info"
    )
