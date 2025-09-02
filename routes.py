import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, WebSocket, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from .models import MessagePayload, MessageResponse
from .config import DISCORD_CHANNEL_ID, API_AUTH_TOKEN
from .websocket_manager import WebSocketManager

logger = logging.getLogger(__name__)

# 路由器
router = APIRouter()

# 認證
security = HTTPBearer(auto_error=False)

# 全域變數（將由主應用程式注入）
message_queue = None
discord_bot = None
websocket_manager = None

def set_globals(queue, bot, ws_manager):
    """設定全域變數（由主應用程式調用）"""
    global message_queue, discord_bot, websocket_manager
    message_queue = queue
    discord_bot = bot
    websocket_manager = ws_manager

# 認證依賴
async def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    if API_AUTH_TOKEN:
        if not credentials or credentials.credentials != API_AUTH_TOKEN:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="無效的認證令牌",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return True

@router.post("/send-message", response_model=MessageResponse, dependencies=[Depends(verify_token)])
async def send_message(payload: MessagePayload):
    """發送訊息到 Discord"""
    global message_queue
    
    if not message_queue:
        raise HTTPException(status_code=503, detail="訊息佇列未初始化")
    
    try:
        # 準備訊息資料
        message_data = {
            "content": payload.content,
            "channel_id": payload.channel_id or DISCORD_CHANNEL_ID,
            "embed": payload.embed
        }
        
        # 將訊息加入佇列
        await message_queue.put(message_data)
        
        return MessageResponse(
            success=True,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"處理訊息請求失敗: {e}")
        raise HTTPException(status_code=500, detail=f"內部伺服器錯誤: {str(e)}")

@router.get("/status")
async def get_status():
    """取得 Bot 狀態"""
    global discord_bot
    
    if discord_bot and discord_bot.is_ready_flag:
        return {
            "status": "online",
            "bot_name": discord_bot.user.name if discord_bot.user else None,
            "timestamp": datetime.now().isoformat()
        }
    else:
        return {
            "status": "offline",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/servers")
async def get_servers():
    """取得所有伺服器資訊"""
    global discord_bot
    
    if not discord_bot or not discord_bot.is_ready_flag:
        raise HTTPException(status_code=503, detail="Bot 未連線")
    
    servers = []
    for guild in discord_bot.guilds:
        server_info = {
            "id": guild.id,
            "name": guild.name,
            "member_count": guild.member_count,
            "channel_count": len(guild.channels),
            "owner_id": guild.owner_id,
            "created_at": guild.created_at.isoformat() if guild.created_at else None
        }
        servers.append(server_info)
    
    return {
        "servers": servers,
        "total_count": len(servers),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/servers/{guild_id}/channels")
async def get_guild_channels(guild_id: int):
    """取得指定伺服器的頻道資訊"""
    global discord_bot
    
    if not discord_bot or not discord_bot.is_ready_flag:
        raise HTTPException(status_code=503, detail="Bot 未連線")
    
    guild = discord_bot.get_guild(guild_id)
    if not guild:
        raise HTTPException(status_code=404, detail="找不到指定的伺服器")
    
    channels = []
    for channel in guild.channels:
        channel_info = {
            "id": channel.id,
            "name": channel.name,
            "type": str(channel.type),
            "position": channel.position
        }
        channels.append(channel_info)
    
    return {
        "guild_name": guild.name,
        "guild_id": guild.id,
        "channels": channels,
        "total_count": len(channels),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/websocket/connections")
async def get_websocket_connections():
    """取得 WebSocket 連線數"""
    global websocket_manager
    
    if not websocket_manager:
        return {"connections": 0}
    
    return {
        "connections": websocket_manager.get_connection_count(),
        "timestamp": datetime.now().isoformat()
    }

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端點"""
    global websocket_manager
    
    if not websocket_manager:
        await websocket.close(code=status.WS_1011_INTERNAL_ERROR)
        return
    
    await websocket_manager.handle_websocket(websocket)

@router.get("/health")
async def health_check():
    """健康檢查端點"""
    return {
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "bot_status": "online" if (discord_bot and discord_bot.is_ready_flag) else "offline",
        "websocket_connections": websocket_manager.get_connection_count() if websocket_manager else 0
    }
