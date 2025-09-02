import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Discord Bot 配置
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_CHANNEL_ID = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
API_AUTH_TOKEN = os.getenv("API_AUTH_TOKEN")

# 伺服器配置
HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", "8000"))

# 驗證配置
def validate_config():
    """驗證必要的環境變數"""
    if not DISCORD_TOKEN:
        raise ValueError("DISCORD_TOKEN 環境變數必須設定")
    if not DISCORD_CHANNEL_ID:
        raise ValueError("DISCORD_CHANNEL_ID 環境變數必須設定")
    
    return True
