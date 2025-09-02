import asyncio
import logging
from typing import Optional
from datetime import datetime
from .config import DISCORD_CHANNEL_ID
from .bot import DiscordBot
import discord

logger = logging.getLogger(__name__)

class DiscordSenderTask:
    def __init__(self, message_queue: asyncio.Queue, discord_bot: DiscordBot):
        self.message_queue = message_queue
        self.discord_bot = discord_bot
        self.running = False
    
    async def start(self):
        """啟動訊息發送任務"""
        self.running = True
        logger.info("Discord 訊息發送任務已啟動")
        
        while self.running:
            try:
                # 等待訊息
                message_data = await self.message_queue.get()
                
                if self.discord_bot and self.discord_bot.is_ready_flag:
                    await self._send_message(message_data)
                else:
                    # Bot 未準備好，將訊息放回佇列
                    await asyncio.sleep(1)
                    await self.message_queue.put(message_data)
                    
            except asyncio.CancelledError:
                logger.info("Discord 發送任務已取消")
                break
            except Exception as e:
                logger.error(f"Discord 發送任務錯誤: {e}")
                await asyncio.sleep(1)
    
    async def stop(self):
        """停止訊息發送任務"""
        self.running = False
        logger.info("Discord 訊息發送任務已停止")
    
    async def _send_message(self, message_data: dict):
        """發送訊息到 Discord"""
        try:
            # 取得頻道
            channel_id = message_data.get("channel_id", DISCORD_CHANNEL_ID)
            channel = self.discord_bot.get_channel(channel_id)
            
            if not channel:
                error_msg = f"找不到頻道 ID: {channel_id}"
                logger.error(error_msg)
                await self.discord_bot.broadcast_websocket({
                    "type": "error",
                    "message": error_msg,
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            # 發送訊息
            if message_data.get("embed"):
                # 發送 Embed
                embed = discord.Embed.from_dict(message_data["embed"])
                message = await channel.send(embed=embed)
            else:
                # 發送純文字
                message = await channel.send(message_data["content"])
            
            # 廣播成功訊息
            success_msg = {
                "type": "success",
                "message": f"訊息已發送到頻道 {channel.name}",
                "message_id": message.id,
                "timestamp": datetime.now().isoformat()
            }
            await self.discord_bot.broadcast_websocket(success_msg)
            
            logger.info(f"訊息已發送: {message.id}")
            
        except Exception as e:
            error_msg = f"發送訊息失敗: {str(e)}"
            logger.error(error_msg)
            await self.discord_bot.broadcast_websocket({
                "type": "error",
                "message": error_msg,
                "timestamp": datetime.now().isoformat()
            })
