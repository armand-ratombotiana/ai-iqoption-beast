"""
Base Agent Class
Abstract base class for all AI agents in the KAEL system
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import uuid4


class AgentState(Enum):
    """Agent operational states"""
    IDLE = "idle"
    PERCEIVING = "perceiving"
    REASONING = "reasoning"
    ACTING = "acting"
    LEARNING = "learning"
    ERROR = "error"
    STOPPED = "stopped"


class BaseAgent(ABC):
    """
    Abstract base class for all AI agents
    
    Implements the Perceive-Reason-Act-Learn cycle:
    1. Perceive: Gather information from environment
    2. Reason: Process information and make decisions
    3. Act: Execute actions based on decisions
    4. Learn: Update knowledge from outcomes
    """
    
    def __init__(
        self,
        name: str,
        role: str,
        description: str = "",
        message_bus: Optional[Any] = None,
        blackboard: Optional[Any] = None
    ):
        """
        Initialize agent
        
        Args:
            name: Unique agent name
            role: Agent role/type
            description: Agent description
            message_bus: Message bus for communication
            blackboard: Shared knowledge base
        """
        self.agent_id = str(uuid4())
        self.name = name
        self.role = role
        self.description = description
        self.state = AgentState.IDLE
        
        # Communication
        self.message_bus = message_bus
        self.blackboard = blackboard
        
        # Memory and state
        from agents.base.memory import AgentMemory
        self.memory = AgentMemory()
        
        # Performance tracking
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        self.total_execution_time = 0.0
        
        # Logging
        self.logger = logging.getLogger(f"Agent.{self.name}")
        
        # Lifecycle
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.is_active = True
        
        self.logger.info(f"✅ Agent initialized: {self.name} ({self.role})")
    
    # ========================================================================
    # Core Agent Cycle (Perceive-Reason-Act-Learn)
    # ========================================================================
    
    async def run_cycle(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute one complete agent cycle
        
        Args:
            environment: Current environment state
            
        Returns:
            Cycle result with actions and outcomes
        """
        start_time = datetime.now()
        self.total_cycles += 1
        self.last_active = datetime.now()
        
        try:
            # 1. Perceive
            self.state = AgentState.PERCEIVING
            perception = await self.perceive(environment)
            self.memory.add_perception(perception)
            
            # 2. Reason
            self.state = AgentState.REASONING
            decision = await self.reason(perception)
            self.memory.add_decision(decision)
            
            # 3. Act
            self.state = AgentState.ACTING
            action_result = await self.act(decision)
            self.memory.add_action(action_result)
            
            # Update state
            self.state = AgentState.IDLE
            self.successful_cycles += 1
            
            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds()
            self.total_execution_time += execution_time
            
            return {
                'success': True,
                'agent': self.name,
                'perception': perception,
                'decision': decision,
                'action': action_result,
                'execution_time': execution_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.state = AgentState.ERROR
            self.failed_cycles += 1
            self.logger.error(f"❌ Agent cycle failed: {e}")
            
            return {
                'success': False,
                'agent': self.name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    @abstractmethod
    async def perceive(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perceive: Gather information from environment
        
        Args:
            environment: Current environment state
            
        Returns:
            Perceived information
        """
        pass
    
    @abstractmethod
    async def reason(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reason: Process information and make decisions
        
        Args:
            perception: Perceived information
            
        Returns:
            Decision/reasoning result
        """
        pass
    
    @abstractmethod
    async def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """
        Act: Execute actions based on decisions
        
        Args:
            decision: Decision from reasoning
            
        Returns:
            Action result
        """
        pass
    
    async def learn(self, outcome: Dict[str, Any]) -> None:
        """
        Learn: Update knowledge from outcomes (optional)
        
        Args:
            outcome: Outcome of actions
        """
        # Default implementation: store in memory
        self.memory.add_outcome(outcome)
        self.logger.debug(f"📚 Learning from outcome: {outcome.get('result', 'unknown')}")
    
    # ========================================================================
    # Communication Methods
    # ========================================================================
    
    async def send_message(
        self,
        to: str,
        message_type: str,
        data: Dict[str, Any],
        priority: str = "NORMAL"
    ) -> None:
        """
        Send message to another agent
        
        Args:
            to: Recipient agent name
            message_type: Type of message
            data: Message data
            priority: Message priority
        """
        if not self.message_bus:
            self.logger.warning("⚠️  No message bus configured")
            return
        
        from agents.base.message import Message, MessageType, MessagePriority
        
        message = Message(
            from_agent=self.name,
            to_agent=to,
            message_type=MessageType(message_type),
            data=data,
            priority=MessagePriority(priority)
        )
        
        await self.message_bus.send(message)
        self.logger.debug(f"📤 Sent message to {to}: {message_type}")
    
    async def broadcast_message(
        self,
        message_type: str,
        data: Dict[str, Any],
        priority: str = "NORMAL"
    ) -> None:
        """
        Broadcast message to all agents
        
        Args:
            message_type: Type of message
            data: Message data
            priority: Message priority
        """
        if not self.message_bus:
            self.logger.warning("⚠️  No message bus configured")
            return
        
        from agents.base.message import Message, MessageType, MessagePriority
        
        message = Message(
            from_agent=self.name,
            to_agent="ALL",
            message_type=MessageType(message_type),
            data=data,
            priority=MessagePriority(priority)
        )
        
        await self.message_bus.broadcast(message)
        self.logger.debug(f"📢 Broadcast message: {message_type}")
    
    async def write_to_blackboard(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> None:
        """
        Write knowledge to shared blackboard
        
        Args:
            key: Knowledge key
            value: Knowledge value
            ttl: Time to live in seconds (optional)
        """
        if not self.blackboard:
            self.logger.warning("⚠️  No blackboard configured")
            return
        
        await self.blackboard.write(key, value, self.name, ttl)
        self.logger.debug(f"📝 Wrote to blackboard: {key}")
    
    async def read_from_blackboard(self, key: str) -> Optional[Any]:
        """
        Read knowledge from shared blackboard
        
        Args:
            key: Knowledge key
            
        Returns:
            Knowledge value or None
        """
        if not self.blackboard:
            self.logger.warning("⚠️  No blackboard configured")
            return None
        
        value = await self.blackboard.read(key)
        self.logger.debug(f"📖 Read from blackboard: {key}")
        return value
    
    # ========================================================================
    # Agent Information & Status
    # ========================================================================
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'role': self.role,
            'description': self.description,
            'state': self.state.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'last_active': self.last_active.isoformat()
        }
    
    def get_performance(self) -> Dict[str, Any]:
        """Get agent performance metrics"""
        success_rate = 0.0
        if self.total_cycles > 0:
            success_rate = (self.successful_cycles / self.total_cycles) * 100
        
        avg_execution_time = 0.0
        if self.total_cycles > 0:
            avg_execution_time = self.total_execution_time / self.total_cycles
        
        return {
            'total_cycles': self.total_cycles,
            'successful_cycles': self.successful_cycles,
            'failed_cycles': self.failed_cycles,
            'success_rate': round(success_rate, 2),
            'total_execution_time': round(self.total_execution_time, 3),
            'avg_execution_time': round(avg_execution_time, 3)
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get complete agent status"""
        return {
            **self.get_info(),
            'performance': self.get_performance(),
            'memory_size': len(self.memory.get_recent_memories())
        }
    
    # ========================================================================
    # Lifecycle Management
    # ========================================================================
    
    async def start(self) -> None:
        """Start agent"""
        self.is_active = True
        self.state = AgentState.IDLE
        self.logger.info(f"▶️  Agent started: {self.name}")
    
    async def stop(self) -> None:
        """Stop agent"""
        self.is_active = False
        self.state = AgentState.STOPPED
        self.logger.info(f"⏸️  Agent stopped: {self.name}")
    
    async def reset(self) -> None:
        """Reset agent state"""
        self.memory.clear()
        self.total_cycles = 0
        self.successful_cycles = 0
        self.failed_cycles = 0
        self.total_execution_time = 0.0
        self.state = AgentState.IDLE
        self.logger.info(f"🔄 Agent reset: {self.name}")
    
    # ========================================================================
    # String Representation
    # ========================================================================
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}', role='{self.role}', state='{self.state.value}')>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.role}) - {self.state.value}"