"""
Agent Message System
Defines message structure and types for agent communication
"""

import json
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional
from uuid import uuid4
from dataclasses import dataclass, field, asdict


class MessageType(Enum):
    """Types of messages agents can send"""
    # Analysis messages
    SIGNAL = "signal"                    # Trading signal
    ANALYSIS = "analysis"                # Analysis result
    MARKET_DATA = "market_data"          # Market data update
    
    # Decision messages
    DECISION = "decision"                # Trading decision
    STRATEGY = "strategy"                # Strategy recommendation
    CONSENSUS = "consensus"              # Consensus result
    
    # Execution messages
    EXECUTION = "execution"              # Trade execution
    RISK_CHECK = "risk_check"            # Risk validation
    POSITION_SIZE = "position_size"      # Position sizing
    
    # Learning messages
    FEEDBACK = "feedback"                # Performance feedback
    LEARNING = "learning"                # Learning update
    PERFORMANCE = "performance"          # Performance metrics
    
    # Control messages
    QUERY = "query"                      # Information request
    RESPONSE = "response"                # Query response
    STATUS = "status"                    # Status update
    ERROR = "error"                      # Error notification
    COMMAND = "command"                  # Command to agent
    
    # System messages
    HEARTBEAT = "heartbeat"              # Health check
    SHUTDOWN = "shutdown"                # Shutdown signal
    RESET = "reset"                      # Reset signal


class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = "critical"    # Immediate processing required
    HIGH = "high"           # High priority
    NORMAL = "normal"       # Normal priority
    LOW = "low"            # Low priority
    BACKGROUND = "background"  # Background processing


@dataclass
class Message:
    """
    Message structure for agent communication
    
    Attributes:
        message_id: Unique message identifier
        from_agent: Sender agent name
        to_agent: Recipient agent name (or "ALL" for broadcast)
        message_type: Type of message
        data: Message payload
        priority: Message priority
        timestamp: Message creation time
        ttl: Time to live in seconds (optional)
        reply_to: ID of message this is replying to (optional)
        metadata: Additional metadata (optional)
    """
    from_agent: str
    to_agent: str
    message_type: MessageType
    data: Dict[str, Any]
    priority: MessagePriority = MessagePriority.NORMAL
    message_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    ttl: Optional[int] = None
    reply_to: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary"""
        result = asdict(self)
        result['message_type'] = self.message_type.value
        result['priority'] = self.priority.value
        return result
    
    def to_json(self) -> str:
        """Convert message to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Message':
        """Create message from dictionary"""
        # Convert string enums back to enum types
        if isinstance(data.get('message_type'), str):
            data['message_type'] = MessageType(data['message_type'])
        if isinstance(data.get('priority'), str):
            data['priority'] = MessagePriority(data['priority'])
        
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string"""
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    def is_expired(self) -> bool:
        """Check if message has expired based on TTL"""
        if self.ttl is None:
            return False
        
        created_at = datetime.fromisoformat(self.timestamp)
        age = (datetime.now() - created_at).total_seconds()
        return age > self.ttl
    
    def is_broadcast(self) -> bool:
        """Check if message is a broadcast"""
        return self.to_agent == "ALL"
    
    def create_reply(
        self,
        from_agent: str,
        data: Dict[str, Any],
        message_type: Optional[MessageType] = None
    ) -> 'Message':
        """
        Create a reply to this message
        
        Args:
            from_agent: Name of agent sending reply
            data: Reply data
            message_type: Type of reply (defaults to RESPONSE)
            
        Returns:
            New message as reply
        """
        return Message(
            from_agent=from_agent,
            to_agent=self.from_agent,
            message_type=message_type or MessageType.RESPONSE,
            data=data,
            priority=self.priority,
            reply_to=self.message_id
        )
    
    def __repr__(self) -> str:
        return (
            f"<Message(id='{self.message_id[:8]}...', "
            f"from='{self.from_agent}', to='{self.to_agent}', "
            f"type='{self.message_type.value}', priority='{self.priority.value}')>"
        )
    
    def __str__(self) -> str:
        return (
            f"[{self.priority.value.upper()}] "
            f"{self.from_agent} → {self.to_agent}: "
            f"{self.message_type.value}"
        )


class MessageBuilder:
    """
    Builder pattern for creating messages
    Provides a fluent interface for message construction
    """
    
    def __init__(self):
        self._from_agent: Optional[str] = None
        self._to_agent: Optional[str] = None
        self._message_type: Optional[MessageType] = None
        self._data: Dict[str, Any] = {}
        self._priority: MessagePriority = MessagePriority.NORMAL
        self._ttl: Optional[int] = None
        self._reply_to: Optional[str] = None
        self._metadata: Dict[str, Any] = {}
    
    def from_agent(self, agent: str) -> 'MessageBuilder':
        """Set sender agent"""
        self._from_agent = agent
        return self
    
    def to_agent(self, agent: str) -> 'MessageBuilder':
        """Set recipient agent"""
        self._to_agent = agent
        return self
    
    def broadcast(self) -> 'MessageBuilder':
        """Set as broadcast message"""
        self._to_agent = "ALL"
        return self
    
    def message_type(self, msg_type: MessageType) -> 'MessageBuilder':
        """Set message type"""
        self._message_type = msg_type
        return self
    
    def data(self, data: Dict[str, Any]) -> 'MessageBuilder':
        """Set message data"""
        self._data = data
        return self
    
    def add_data(self, key: str, value: Any) -> 'MessageBuilder':
        """Add single data field"""
        self._data[key] = value
        return self
    
    def priority(self, priority: MessagePriority) -> 'MessageBuilder':
        """Set message priority"""
        self._priority = priority
        return self
    
    def ttl(self, seconds: int) -> 'MessageBuilder':
        """Set time to live"""
        self._ttl = seconds
        return self
    
    def reply_to(self, message_id: str) -> 'MessageBuilder':
        """Set reply-to message ID"""
        self._reply_to = message_id
        return self
    
    def metadata(self, metadata: Dict[str, Any]) -> 'MessageBuilder':
        """Set metadata"""
        self._metadata = metadata
        return self
    
    def add_metadata(self, key: str, value: Any) -> 'MessageBuilder':
        """Add single metadata field"""
        self._metadata[key] = value
        return self
    
    def build(self) -> Message:
        """Build and return the message"""
        if not self._from_agent:
            raise ValueError("from_agent is required")
        if not self._to_agent:
            raise ValueError("to_agent is required")
        if not self._message_type:
            raise ValueError("message_type is required")
        
        return Message(
            from_agent=self._from_agent,
            to_agent=self._to_agent,
            message_type=self._message_type,
            data=self._data,
            priority=self._priority,
            ttl=self._ttl,
            reply_to=self._reply_to,
            metadata=self._metadata
        )
    
    def reset(self) -> 'MessageBuilder':
        """Reset builder to initial state"""
        self.__init__()
        return self


# Convenience functions for creating common message types

def create_signal_message(
    from_agent: str,
    to_agent: str,
    signal: str,
    confidence: float,
    reasoning: str,
    **kwargs
) -> Message:
    """Create a trading signal message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.SIGNAL,
        data={
            'signal': signal,
            'confidence': confidence,
            'reasoning': reasoning,
            **kwargs
        },
        priority=MessagePriority.HIGH
    )


def create_analysis_message(
    from_agent: str,
    to_agent: str,
    analysis: Dict[str, Any],
    **kwargs
) -> Message:
    """Create an analysis message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.ANALYSIS,
        data={'analysis': analysis, **kwargs},
        priority=MessagePriority.NORMAL
    )


def create_decision_message(
    from_agent: str,
    to_agent: str,
    decision: str,
    confidence: float,
    reasoning: str,
    **kwargs
) -> Message:
    """Create a decision message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.DECISION,
        data={
            'decision': decision,
            'confidence': confidence,
            'reasoning': reasoning,
            **kwargs
        },
        priority=MessagePriority.HIGH
    )


def create_execution_message(
    from_agent: str,
    to_agent: str,
    action: str,
    parameters: Dict[str, Any],
    **kwargs
) -> Message:
    """Create an execution message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.EXECUTION,
        data={
            'action': action,
            'parameters': parameters,
            **kwargs
        },
        priority=MessagePriority.CRITICAL
    )


def create_error_message(
    from_agent: str,
    to_agent: str,
    error: str,
    details: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Message:
    """Create an error message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.ERROR,
        data={
            'error': error,
            'details': details or {},
            **kwargs
        },
        priority=MessagePriority.HIGH
    )


def create_query_message(
    from_agent: str,
    to_agent: str,
    query: str,
    parameters: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Message:
    """Create a query message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.QUERY,
        data={
            'query': query,
            'parameters': parameters or {},
            **kwargs
        },
        priority=MessagePriority.NORMAL
    )


def create_response_message(
    from_agent: str,
    to_agent: str,
    response: Any,
    reply_to: str,
    **kwargs
) -> Message:
    """Create a response message"""
    return Message(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=MessageType.RESPONSE,
        data={'response': response, **kwargs},
        priority=MessagePriority.NORMAL,
        reply_to=reply_to
    )