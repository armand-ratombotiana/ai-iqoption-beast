"""
KAEL AI Agents System
Multi-agent system for intelligent trading decisions

This module provides a comprehensive AI agent framework for autonomous trading.
Agents collaborate to analyze markets, make decisions, and execute trades.
"""

__version__ = "1.0.0"

# Base components
from agents.base.agent import BaseAgent, AgentState
from agents.base.message import Message, MessageType, MessagePriority, MessageBuilder
from agents.base.memory import AgentMemory

# Communication
from agents.communication.message_bus import MessageBus
from agents.communication.blackboard import Blackboard

# Orchestrator
from agents.orchestrator import AgentOrchestrator

__all__ = [
    # Base
    "BaseAgent",
    "AgentState",
    "Message",
    "MessageType",
    "MessagePriority",
    "MessageBuilder",
    "AgentMemory",
    
    # Communication
    "MessageBus",
    "Blackboard",
    
    # Orchestrator
    "AgentOrchestrator",
]