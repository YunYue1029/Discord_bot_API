import logging
from typing import List
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)

class WebSocketManager:
    def __init__(self):
        self.connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        """接受新的 WebSocket 連線"""
        await websocket.accept()
        self.connections.append(websocket)
        
        # 發送連線成功訊息
        await self.send_personal_message(websocket, {
            "type": "connection",
            "message": "WebSocket 連線已建立",
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"WebSocket 連線已建立，當前連線數: {len(self.connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """移除斷線的 WebSocket 連線"""
        if websocket in self.connections:
            self.connections.remove(websocket)
            logger.info(f"WebSocket 連線已關閉，當前連線數: {len(self.connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """發送訊息到指定的 WebSocket 連線"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"發送個人訊息失敗: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """廣播訊息到所有 WebSocket 連線"""
        disconnected = []
        
        for websocket in self.connections:
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"WebSocket 廣播失敗: {e}")
                disconnected.append(websocket)
        
        # 移除斷線的連線
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def handle_websocket(self, websocket: WebSocket):
        """處理 WebSocket 連線的生命週期"""
        await self.connect(websocket)
        
        try:
            while True:
                # 等待客戶端訊息（可選）
                data = await websocket.receive_text()
                logger.info(f"收到 WebSocket 訊息: {data}")
                
        except WebSocketDisconnect:
            logger.info("WebSocket 客戶端斷線")
        except Exception as e:
            logger.error(f"WebSocket 錯誤: {e}")
        finally:
            self.disconnect(websocket)
    
    def get_connection_count(self) -> int:
        """取得當前連線數"""
        return len(self.connections)
