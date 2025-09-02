import logging
import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
from .websocket_manager import WebSocketManager
from .commands_impl import ping_command, status_command, servers_command, channels_command

logger = logging.getLogger(__name__)

class DiscordBot(commands.Bot):
    def __init__(self, websocket_manager: WebSocketManager):
        # Discord Bot 設定
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.guild_messages = True
        intents.guild_reactions = True
        intents.members = True
        
        super().__init__(command_prefix="!", intents=intents)
        self.is_ready_flag = False
        self.websocket_manager = websocket_manager

    async def setup_hook(self):
        # 手動把命令註冊進來
        self.add_command(ping_command)
        self.add_command(status_command)
        self.add_command(servers_command)
        self.add_command(channels_command)
        logger.info("Discord Bot 設定完成，已註冊命令：ping / status / servers / channels")
    
    async def on_ready(self):
        self.is_ready_flag = True
        logger.info(f"Discord Bot 已登入: {self.user}")
        await self.broadcast_status("Bot 已準備就緒")
    
    async def on_disconnect(self):
        self.is_ready_flag = False
        logger.warning("Discord Bot 已斷線")
        await self.broadcast_status("Bot 已斷線")
    
    async def on_guild_join(self, guild):
        """Bot 加入新伺服器時"""
        logger.info(f"Bot 已加入新伺服器: {guild.name} (ID: {guild.id})")
        await self.broadcast_status(f"Bot 已加入伺服器: {guild.name}")
    
    async def on_guild_remove(self, guild):
        """Bot 離開伺服器時"""
        logger.info(f"Bot 已離開伺服器: {guild.name} (ID: {guild.id})")
        await self.broadcast_status(f"Bot 已離開伺服器: {guild.name}")
    
    async def on_guild_update(self, before, after):
        """伺服器資訊更新時"""
        if before.name != after.name:
            logger.info(f"伺服器名稱已更新: {before.name} -> {after.name}")
            await self.broadcast_status(f"伺服器名稱已更新: {before.name} -> {after.name}")
    
    async def on_member_join(self, member):
        """新成員加入伺服器時"""
        logger.info(f"新成員加入: {member.name} 在伺服器 {member.guild.name}")
        await self.broadcast_status(f"新成員 {member.name} 已加入伺服器 {member.guild.name}")
    
    async def on_member_remove(self, member):
        """成員離開伺服器時"""
        logger.info(f"成員離開: {member.name} 從伺服器 {member.guild.name}")
        await self.broadcast_status(f"成員 {member.name} 已離開伺服器 {member.guild.name}")
    
    async def on_message(self, message):
        """收到訊息時"""
        # 忽略 Bot 自己的訊息
        if message.author == self.user:
            return
        
        logger.info(f"收到訊息: {message.author.name}: {message.content} (在頻道 {message.channel.name})")
        
        # 廣播訊息到 WebSocket
        await self.broadcast_websocket({
            "type": "message",
            "guild": message.guild.name if message.guild else "DM",
            "channel": message.channel.name,
            "author": message.author.name,
            "content": message.content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 處理命令
        await self.process_commands(message)
    
    async def on_reaction_add(self, reaction, user):
        """收到反應時"""
        if user == self.user:
            return
        
        logger.info(f"收到反應: {user.name} 對訊息 {reaction.message.id} 添加了 {reaction.emoji}")
        await self.broadcast_websocket({
            "type": "reaction",
            "guild": reaction.message.guild.name if reaction.message.guild else "DM",
            "channel": reaction.message.channel.name,
            "author": user.name,
            "emoji": str(reaction.emoji),
            "message_id": reaction.message.id,
            "timestamp": datetime.now().isoformat()
        })
    
    async def on_guild_channel_create(self, channel):
        """新頻道創建時"""
        logger.info(f"新頻道已創建: {channel.name} 在伺服器 {channel.guild.name}")
        await self.broadcast_status(f"新頻道 {channel.name} 已在伺服器 {channel.guild.name} 創建")
    
    async def on_guild_channel_delete(self, channel):
        """頻道刪除時"""
        logger.info(f"頻道已刪除: {channel.name} 從伺服器 {channel.guild.name}")
        await self.broadcast_status(f"頻道 {channel.name} 已從伺服器 {channel.guild.name} 刪除")
    
    async def on_guild_channel_update(self, before, after):
        """頻道更新時"""
        if before.name != after.name:
            logger.info(f"頻道名稱已更新: {before.name} -> {after.name}")
            await self.broadcast_status(f"頻道名稱已更新: {before.name} -> {after.name}")
    
    async def on_member_update(self, before, after):
        """成員資訊更新時"""
        if before.nick != after.nick:
            logger.info(f"成員暱稱已更新: {before.nick or before.name} -> {after.nick or after.name}")
            await self.broadcast_status(f"成員暱稱已更新: {before.nick or before.name} -> {after.nick or after.name}")
    
    async def broadcast_status(self, message: str):
        """廣播狀態訊息到所有 WebSocket 連線"""
        await self.websocket_manager.broadcast({
            "type": "status",
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    
    async def broadcast_websocket(self, data: dict):
        """廣播資料到所有 WebSocket 連線"""
        await self.websocket_manager.broadcast(data)