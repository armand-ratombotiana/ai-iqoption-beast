"""
Message Bus
Async message passing system for agent communication
"""

import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime
from typing import Dict, List, Set, Optional, Callable, Deque
from agents.base.message import Message, MessageType, MessagePriority


class MessageBus:
    """
    Asynchronous message bus for agent communication
    
    Features:
    - Topic-based pub/sub
    - Priority queue
    - Message routing
    - Broadcast support
    - Message history
    - Delivery confirmation
    - Dead letter queue
    """
    
    def __init__(
        self,
        max_queue_size: int = 1000,
        max_history_size: int = 100,
        enable_history: bool = True
    ):
        """
        Initialize message bus
        
        Args:
            max_queue_size: Maximum messages in queue
            max_history_size: Maximum messages in history
            enable_history: Enable message history tracking
        """
        # Message queues (priority-based)
        self.queues: Dict[str, asyncio.PriorityQueue] = {}
        self.max_queue_size = max_queue_size
        
        # Subscriptions (topic -> set of agent names)
        self.subscriptions: Dict[str, Set[str]] = defaultdict(set)
        
        # Message handlers (agent_name -> callback)
        self.handlers: Dict[str, Callable] = {}
        
        # Message history
        self.enable_history = enable_history
        self.history: Deque[Message] = deque(maxlen=max_history_size)
        
        # Dead letter queue (failed messages)
        self.dead_letter_queue: Deque[Dict] = deque(maxlen=100)
        
        # Statistics
        self.total_sent = 0
        self.total_delivered = 0
        self.total_failed = 0
        
        # Logging
        self.logger = logging.getLogger("MessageBus")
        
        # Running state
        self.is_running = False
        self._tasks: List[asyncio.Task] = []
        
        self.logger.info("✅ MessageBus initialized")
    
    # ========================================================================
    # Subscription Management
    # ========================================================================
    
    async def subscribe(
        self,
        agent_name: str,
        topic: str,
        handler: Optional[Callable] = None
    ) -> None:
        """
        Subscribe agent to topic
        
        Args:
            agent_name: Name of subscribing agent
            topic: Topic to subscribe to
            handler: Optional message handler callback
        """
        self.subscriptions[topic].add(agent_name)
        
        if handler:
            self.handlers[agent_name] = handler
        
        # Create queue for agent if doesn't exist
        if agent_name not in self.queues:
            self.queues[agent_name] = asyncio.PriorityQueue(maxsize=self.max_queue_size)
        
        self.logger.debug(f"📥 {agent_name} subscribed to '{topic}'")
    
    async def unsubscribe(self, agent_name: str, topic: str) -> None:
        """Unsubscribe agent from topic"""
        if topic in self.subscriptions:
            self.subscriptions[topic].discard(agent_name)
            self.logger.debug(f"📤 {agent_name} unsubscribed from '{topic}'")
    
    async def unsubscribe_all(self, agent_name: str) -> None:
        """Unsubscribe agent from all topics"""
        for topic in list(self.subscriptions.keys()):
            self.subscriptions[topic].discard(agent_name)
        
        if agent_name in self.handlers:
            del self.handlers[agent_name]
        
        self.logger.debug(f"📤 {agent_name} unsubscribed from all topics")
    
    # ========================================================================
    # Message Sending
    # ========================================================================
    
    async def send(self, message: Message) -> bool:
        """
        Send message to specific agent
        
        Args:
            message: Message to send
            
        Returns:
            True if sent successfully
        """
        try:
            self.total_sent += 1
            
            # Add to history
            if self.enable_history:
                self.history.append(message)
            
            # Check if message expired
            if message.is_expired():
                self.logger.warning(f"⚠️  Message {message.message_id[:8]} expired")
                self.total_failed += 1
                return False
            
            # Get recipient
            recipient = message.to_agent
            
            # Create queue if doesn't exist
            if recipient not in self.queues:
                self.queues[recipient] = asyncio.PriorityQueue(maxsize=self.max_queue_size)
            
            # Get priority value (lower number = higher priority)
            priority_map = {
                MessagePriority.CRITICAL: 0,
                MessagePriority.HIGH: 1,
                MessagePriority.NORMAL: 2,
                MessagePriority.LOW: 3,
                MessagePriority.BACKGROUND: 4
            }
            priority = priority_map.get(message.priority, 2)
            
            # Put in queue (priority, message)
            try:
                await asyncio.wait_for(
                    self.queues[recipient].put((priority, message)),
                    timeout=1.0
                )
                self.total_delivered += 1
                self.logger.debug(f"📨 Sent {message.message_type.value} to {recipient}")
                return True
            except asyncio.TimeoutError:
                self.logger.error(f"❌ Queue full for {recipient}")
                self._add_to_dead_letter(message, "Queue full")
                self.total_failed += 1
                return False
            
        except Exception as e:
            self.logger.error(f"❌ Error sending message: {e}")
            self._add_to_dead_letter(message, str(e))
            self.total_failed += 1
            return False
    
    async def broadcast(self, message: Message) -> int:
        """
        Broadcast message to all subscribed agents
        
        Args:
            message: Message to broadcast
            
        Returns:
            Number of agents message was sent to
        """
        sent_count = 0
        
        # Get all agents subscribed to this message type
        topic = message.message_type.value
        subscribers = self.subscriptions.get(topic, set())
        
        # If no specific subscribers, send to all agents
        if not subscribers:
            subscribers = set(self.queues.keys())
        
        # Send to each subscriber
        for agent_name in subscribers:
            # Create copy of message for each recipient
            msg_copy = Message(
                from_agent=message.from_agent,
                to_agent=agent_name,
                message_type=message.message_type,
                data=message.data.copy(),
                priority=message.priority,
                ttl=message.ttl,
                reply_to=message.reply_to,
                metadata=message.metadata.copy()
            )
            
            if await self.send(msg_copy):
                sent_count += 1
        
        self.logger.debug(f"📢 Broadcast {message.message_type.value} to {sent_count} agents")
        return sent_count
    
    async def publish(self, topic: str, message: Message) -> int:
        """
        Publish message to topic
        
        Args:
            topic: Topic to publish to
            message: Message to publish
            
        Returns:
            Number of subscribers message was sent to
        """
        sent_count = 0
        subscribers = self.subscriptions.get(topic, set())
        
        for agent_name in subscribers:
            msg_copy = Message(
                from_agent=message.from_agent,
                to_agent=agent_name,
                message_type=message.message_type,
                data=message.data.copy(),
                priority=message.priority,
                ttl=message.ttl,
                reply_to=message.reply_to,
                metadata=message.metadata.copy()
            )
            
            if await self.send(msg_copy):
                sent_count += 1
        
        self.logger.debug(f"📰 Published to '{topic}': {sent_count} subscribers")
        return sent_count
    
    # ========================================================================
    # Message Receiving
    # ========================================================================
    
    async def receive(self, agent_name: str, timeout: Optional[float] = None) -> Optional[Message]:
        """
        Receive message for agent
        
        Args:
            agent_name: Name of agent receiving message
            timeout: Timeout in seconds (None = wait forever)
            
        Returns:
            Message or None if timeout
        """
        if agent_name not in self.queues:
            self.queues[agent_name] = asyncio.PriorityQueue(maxsize=self.max_queue_size)
        
        try:
            if timeout:
                priority, message = await asyncio.wait_for(
                    self.queues[agent_name].get(),
                    timeout=timeout
                )
            else:
                priority, message = await self.queues[agent_name].get()
            
            self.logger.debug(f"📬 {agent_name} received {message.message_type.value}")
            return message
            
        except asyncio.TimeoutError:
            return None
        except Exception as e:
            self.logger.error(f"❌ Error receiving message: {e}")
            return None
    
    async def receive_all(self, agent_name: str) -> List[Message]:
        """
        Receive all pending messages for agent
        
        Args:
            agent_name: Name of agent
            
        Returns:
            List of messages
        """
        messages = []
        
        if agent_name not in self.queues:
            return messages
        
        while not self.queues[agent_name].empty():
            try:
                priority, message = await asyncio.wait_for(
                    self.queues[agent_name].get(),
                    timeout=0.1
                )
                messages.append(message)
            except asyncio.TimeoutError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error receiving messages: {e}")
                break
        
        self.logger.debug(f"📬 {agent_name} received {len(messages)} messages")
        return messages
    
    # ========================================================================
    # Queue Management
    # ========================================================================
    
    def get_queue_size(self, agent_name: str) -> int:
        """Get number of pending messages for agent"""
        if agent_name in self.queues:
            return self.queues[agent_name].qsize()
        return 0
    
    def is_queue_empty(self, agent_name: str) -> bool:
        """Check if agent's queue is empty"""
        if agent_name in self.queues:
            return self.queues[agent_name].empty()
        return True
    
    async def clear_queue(self, agent_name: str) -> int:
        """
        Clear all messages from agent's queue
        
        Returns:
            Number of messages cleared
        """
        count = 0
        if agent_name in self.queues:
            while not self.queues[agent_name].empty():
                try:
                    await asyncio.wait_for(self.queues[agent_name].get(), timeout=0.1)
                    count += 1
                except asyncio.TimeoutError:
                    break
        
        self.logger.debug(f"🗑️  Cleared {count} messages from {agent_name}")
        return count
    
    # ========================================================================
    # History & Dead Letter Queue
    # ========================================================================
    
    def get_history(self, count: int = 10) -> List[Message]:
        """Get recent message history"""
        return list(self.history)[-count:]
    
    def get_dead_letters(self, count: int = 10) -> List[Dict]:
        """Get recent dead letter messages"""
        return list(self.dead_letter_queue)[-count:]
    
    def _add_to_dead_letter(self, message: Message, reason: str) -> None:
        """Add failed message to dead letter queue"""
        self.dead_letter_queue.append({
            'message': message,
            'reason': reason,
            'timestamp': datetime.now().isoformat()
        })
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get message bus statistics"""
        return {
            'total_sent': self.total_sent,
            'total_delivered': self.total_delivered,
            'total_failed': self.total_failed,
            'delivery_rate': (self.total_delivered / self.total_sent * 100) if self.total_sent > 0 else 0,
            'total_queues': len(self.queues),
            'total_subscriptions': sum(len(subs) for subs in self.subscriptions.values()),
            'history_size': len(self.history),
            'dead_letter_size': len(self.dead_letter_queue)
        }
    
    def get_queue_stats(self) -> Dict[str, int]:
        """Get queue sizes for all agents"""
        return {
            agent: queue.qsize()
            for agent, queue in self.queues.items()
        }
    
    # ========================================================================
    # Lifecycle
    # ========================================================================
    
    async def start(self) -> None:
        """Start message bus"""
        self.is_running = True
        self.logger.info("▶️  MessageBus started")
    
    async def stop(self) -> None:
        """Stop message bus"""
        self.is_running = False
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        self.logger.info("⏸️  MessageBus stopped")
    
    async def reset(self) -> None:
        """Reset message bus"""
        # Clear all queues
        for agent_name in list(self.queues.keys()):
            await self.clear_queue(agent_name)
        
        # Clear subscriptions
        self.subscriptions.clear()
        self.handlers.clear()
        
        # Clear history
        self.history.clear()
        self.dead_letter_queue.clear()
        
        # Reset statistics
        self.total_sent = 0
        self.total_delivered = 0
        self.total_failed = 0
        
        self.logger.info("🔄 MessageBus reset")
    
    # ========================================================================
    # String Representation
    # ========================================================================
    
    def __repr__(self) -> str:
        return f"<MessageBus(queues={len(self.queues)}, subscriptions={len(self.subscriptions)})>"
    
    def __str__(self) -> str:
        stats = self.get_statistics()
        return (
            f"MessageBus: {stats['total_delivered']}/{stats['total_sent']} delivered "
            f"({stats['delivery_rate']:.1f}%)"
        )