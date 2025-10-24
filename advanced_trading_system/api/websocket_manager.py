"""
WebSocket Manager for Real-time Updates
Manages WebSocket connections and broadcasts
"""
from fastapi import WebSocket
from typing import List, Dict, Any
import json
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class WebSocketManager:
    """
    WebSocket connection manager for real-time updates
    
    Features:
    - Connection management
    - Broadcast messaging
    - Channel subscriptions
    - Connection health monitoring
    - Message queuing
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.connection_info: Dict[WebSocket, Dict] = {}
        self.subscriptions: Dict[str, List[WebSocket]] = {}
        self.message_queue: Dict[WebSocket, List[Dict]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections.append(websocket)
            
            # Store connection info
            self.connection_info[websocket] = {
                'client_id': client_id or f"client_{len(self.active_connections)}",
                'connected_at': datetime.now().isoformat(),
                'subscriptions': [],
                'message_count': 0
            }
            
            # Initialize message queue
            self.message_queue[websocket] = []
            
            logger.info(f"WebSocket connected: {self.connection_info[websocket]['client_id']}")
            
            # Send welcome message
            await self.send_personal_message({
                "type": "connection_established",
                "data": {
                    "client_id": self.connection_info[websocket]['client_id'],
                    "timestamp": datetime.now().isoformat(),
                    "message": "WebSocket connection established"
                }
            }, websocket)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {e}")
            await self.disconnect(websocket)
    
    async def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        try:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
                
                # Remove from subscriptions
                client_info = self.connection_info.get(websocket, {})
                for channel in client_info.get('subscriptions', []):
                    if channel in self.subscriptions:
                        if websocket in self.subscriptions[channel]:
                            self.subscriptions[channel].remove(websocket)
                
                # Clean up
                if websocket in self.connection_info:
                    del self.connection_info[websocket]
                if websocket in self.message_queue:
                    del self.message_queue[websocket]
                
                logger.info(f"WebSocket disconnected: {client_info.get('client_id', 'unknown')}")
                
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {e}")
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now().isoformat()
            
            await websocket.send_text(json.dumps(message))
            
            # Update message count
            if websocket in self.connection_info:
                self.connection_info[websocket]['message_count'] += 1
                
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            await self.disconnect(websocket)
    
    async def broadcast(self, message: Dict[str, Any], channel: str = None):
        """Broadcast a message to all connected clients or specific channel"""
        try:
            # Add timestamp if not present
            if 'timestamp' not in message:
                message['timestamp'] = datetime.now().isoformat()
            
            message_text = json.dumps(message)
            
            # Determine target connections
            if channel and channel in self.subscriptions:
                target_connections = self.subscriptions[channel]
            else:
                target_connections = self.active_connections.copy()
            
            # Send to all target connections
            disconnected_connections = []
            
            for connection in target_connections:
                try:
                    await connection.send_text(message_text)
                    
                    # Update message count
                    if connection in self.connection_info:
                        self.connection_info[connection]['message_count'] += 1
                        
                except Exception as e:
                    logger.error(f"Error broadcasting to connection: {e}")
                    disconnected_connections.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected_connections:
                await self.disconnect(connection)
                
            logger.debug(f"Broadcast message to {len(target_connections)} connections")
            
        except Exception as e:
            logger.error(f"Error broadcasting message: {e}")
    
    async def subscribe_to_channel(self, websocket: WebSocket, channel: str):
        """Subscribe a WebSocket to a specific channel"""
        try:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = []
            
            if websocket not in self.subscriptions[channel]:
                self.subscriptions[channel].append(websocket)
                
                # Update connection info
                if websocket in self.connection_info:
                    if 'subscriptions' not in self.connection_info[websocket]:
                        self.connection_info[websocket]['subscriptions'] = []
                    self.connection_info[websocket]['subscriptions'].append(channel)
                
                logger.info(f"Client subscribed to channel: {channel}")
                
                # Send confirmation
                await self.send_personal_message({
                    "type": "subscription_confirmed",
                    "data": {
                        "channel": channel,
                        "message": f"Subscribed to {channel}"
                    }
                }, websocket)
                
        except Exception as e:
            logger.error(f"Error subscribing to channel: {e}")
    
    async def unsubscribe_from_channel(self, websocket: WebSocket, channel: str):
        """Unsubscribe a WebSocket from a specific channel"""
        try:
            if channel in self.subscriptions and websocket in self.subscriptions[channel]:
                self.subscriptions[channel].remove(websocket)
                
                # Update connection info
                if websocket in self.connection_info:
                    subscriptions = self.connection_info[websocket].get('subscriptions', [])
                    if channel in subscriptions:
                        subscriptions.remove(channel)
                
                logger.info(f"Client unsubscribed from channel: {channel}")
                
                # Send confirmation
                await self.send_personal_message({
                    "type": "unsubscription_confirmed",
                    "data": {
                        "channel": channel,
                        "message": f"Unsubscribed from {channel}"
                    }
                }, websocket)
                
        except Exception as e:
            logger.error(f"Error unsubscribing from channel: {e}")
    
    async def broadcast_trade_update(self, trade_data: Dict):
        """Broadcast trade-related updates"""
        message = {
            "type": "trade_update",
            "data": trade_data
        }
        await self.broadcast(message, channel="trades")
    
    async def broadcast_market_data(self, market_data: Dict):
        """Broadcast market data updates"""
        message = {
            "type": "market_data",
            "data": market_data
        }
        await self.broadcast(message, channel="market_data")
    
    async def broadcast_system_status(self, status_data: Dict):
        """Broadcast system status updates"""
        message = {
            "type": "system_status",
            "data": status_data
        }
        await self.broadcast(message, channel="system")
    
    async def broadcast_ai_prediction(self, prediction_data: Dict):
        """Broadcast AI prediction updates"""
        message = {
            "type": "ai_prediction",
            "data": prediction_data
        }
        await self.broadcast(message, channel="predictions")
    
    async def handle_client_message(self, websocket: WebSocket, message: Dict):
        """Handle incoming messages from clients"""
        try:
            message_type = message.get("type")
            data = message.get("data", {})
            
            if message_type == "subscribe":
                channels = data.get("channels", [])
                for channel in channels:
                    await self.subscribe_to_channel(websocket, channel)
                    
            elif message_type == "unsubscribe":
                channels = data.get("channels", [])
                for channel in channels:
                    await self.unsubscribe_from_channel(websocket, channel)
                    
            elif message_type == "ping":
                await self.send_personal_message({
                    "type": "pong",
                    "data": {"message": "pong"}
                }, websocket)
                
            elif message_type == "get_status":
                await self.send_connection_status(websocket)
                
            else:
                await self.send_personal_message({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {message_type}"}
                }, websocket)
                
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await self.send_personal_message({
                "type": "error",
                "data": {"message": "Error processing message"}
            }, websocket)
    
    async def send_connection_status(self, websocket: WebSocket):
        """Send connection status to client"""
        try:
            client_info = self.connection_info.get(websocket, {})
            
            status = {
                "type": "connection_status",
                "data": {
                    "client_id": client_info.get('client_id'),
                    "connected_at": client_info.get('connected_at'),
                    "subscriptions": client_info.get('subscriptions', []),
                    "message_count": client_info.get('message_count', 0),
                    "total_connections": len(self.active_connections)
                }
            }
            
            await self.send_personal_message(status, websocket)
            
        except Exception as e:
            logger.error(f"Error sending connection status: {e}")
    
    def get_connection_stats(self) -> Dict:
        """Get WebSocket connection statistics"""
        return {
            "total_connections": len(self.active_connections),
            "channels": {
                channel: len(connections) 
                for channel, connections in self.subscriptions.items()
            },
            "total_messages_sent": sum(
                info.get('message_count', 0) 
                for info in self.connection_info.values()
            )
        }
    
    async def health_check(self) -> Dict:
        """Perform health check on WebSocket connections"""
        healthy_connections = 0
        unhealthy_connections = []
        
        for websocket in self.active_connections.copy():
            try:
                # Send ping to check connection health
                await websocket.send_text(json.dumps({
                    "type": "health_ping",
                    "timestamp": datetime.now().isoformat()
                }))
                healthy_connections += 1
                
            except Exception as e:
                logger.warning(f"Unhealthy WebSocket connection detected: {e}")
                unhealthy_connections.append(websocket)
        
        # Clean up unhealthy connections
        for websocket in unhealthy_connections:
            await self.disconnect(websocket)
        
        return {
            "healthy_connections": healthy_connections,
            "unhealthy_connections": len(unhealthy_connections),
            "total_connections": len(self.active_connections),
            "channels": list(self.subscriptions.keys())
        }
    
    async def start_periodic_tasks(self):
        """Start periodic maintenance tasks"""
        asyncio.create_task(self._periodic_health_check())
        asyncio.create_task(self._periodic_stats_broadcast())
    
    async def _periodic_health_check(self):
        """Periodic health check task"""
        while True:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                await self.health_check()
            except Exception as e:
                logger.error(f"Error in periodic health check: {e}")
    
    async def _periodic_stats_broadcast(self):
        """Periodic stats broadcast task"""
        while True:
            try:
                await asyncio.sleep(60)  # Every minute
                stats = self.get_connection_stats()
                
                await self.broadcast({
                    "type": "connection_stats",
                    "data": stats
                }, channel="system")
                
            except Exception as e:
                logger.error(f"Error in periodic stats broadcast: {e}")