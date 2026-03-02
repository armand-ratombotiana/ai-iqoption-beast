"""
Agent Memory System
Manages short-term and long-term memory for agents
"""

import json
from collections import deque
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Deque
from dataclasses import dataclass, field


@dataclass
class MemoryEntry:
    """Single memory entry"""
    entry_id: str
    entry_type: str  # perception, decision, action, outcome
    data: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    importance: float = 1.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'entry_id': self.entry_id,
            'entry_type': self.entry_type,
            'data': self.data,
            'timestamp': self.timestamp,
            'importance': self.importance,
            'metadata': self.metadata
        }
    
    def age_seconds(self) -> float:
        """Get age of memory in seconds"""
        created = datetime.fromisoformat(self.timestamp)
        return (datetime.now() - created).total_seconds()
    
    def age_minutes(self) -> float:
        """Get age of memory in minutes"""
        return self.age_seconds() / 60
    
    def is_older_than(self, seconds: float) -> bool:
        """Check if memory is older than specified seconds"""
        return self.age_seconds() > seconds


class AgentMemory:
    """
    Agent memory system with short-term and long-term storage
    
    Features:
    - Short-term memory (recent events, limited size)
    - Long-term memory (important events, unlimited)
    - Memory consolidation (move important memories to long-term)
    - Memory retrieval (search and filter)
    - Memory cleanup (remove old/unimportant memories)
    """
    
    def __init__(
        self,
        short_term_capacity: int = 100,
        long_term_capacity: int = 1000,
        consolidation_threshold: float = 0.7,
        cleanup_age_hours: int = 24
    ):
        """
        Initialize memory system
        
        Args:
            short_term_capacity: Max entries in short-term memory
            long_term_capacity: Max entries in long-term memory
            consolidation_threshold: Importance threshold for long-term storage
            cleanup_age_hours: Age in hours after which to cleanup low-importance memories
        """
        # Short-term memory (recent events)
        self.short_term: Deque[MemoryEntry] = deque(maxlen=short_term_capacity)
        
        # Long-term memory (important events)
        self.long_term: List[MemoryEntry] = []
        self.long_term_capacity = long_term_capacity
        
        # Configuration
        self.consolidation_threshold = consolidation_threshold
        self.cleanup_age_hours = cleanup_age_hours
        
        # Statistics
        self.total_memories_created = 0
        self.total_memories_consolidated = 0
        self.total_memories_cleaned = 0
        
        # Entry counter for unique IDs
        self._entry_counter = 0
    
    # ========================================================================
    # Memory Addition
    # ========================================================================
    
    def add_perception(self, data: Dict[str, Any], importance: float = 0.5) -> str:
        """Add perception to memory"""
        return self._add_memory('perception', data, importance)
    
    def add_decision(self, data: Dict[str, Any], importance: float = 0.7) -> str:
        """Add decision to memory"""
        return self._add_memory('decision', data, importance)
    
    def add_action(self, data: Dict[str, Any], importance: float = 0.8) -> str:
        """Add action to memory"""
        return self._add_memory('action', data, importance)
    
    def add_outcome(self, data: Dict[str, Any], importance: float = 0.9) -> str:
        """Add outcome to memory"""
        return self._add_memory('outcome', data, importance)
    
    def add_custom(
        self,
        entry_type: str,
        data: Dict[str, Any],
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add custom memory entry"""
        return self._add_memory(entry_type, data, importance, metadata)
    
    def _add_memory(
        self,
        entry_type: str,
        data: Dict[str, Any],
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Internal method to add memory"""
        self._entry_counter += 1
        entry_id = f"mem_{self._entry_counter:06d}"
        
        entry = MemoryEntry(
            entry_id=entry_id,
            entry_type=entry_type,
            data=data,
            importance=importance,
            metadata=metadata or {}
        )
        
        # Add to short-term memory
        self.short_term.append(entry)
        self.total_memories_created += 1
        
        # Check if should be consolidated to long-term
        if importance >= self.consolidation_threshold:
            self._consolidate_to_long_term(entry)
        
        return entry_id
    
    def _consolidate_to_long_term(self, entry: MemoryEntry) -> None:
        """Move important memory to long-term storage"""
        self.long_term.append(entry)
        self.total_memories_consolidated += 1
        
        # Trim long-term memory if needed
        if len(self.long_term) > self.long_term_capacity:
            # Remove oldest, least important memories
            self.long_term.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
            self.long_term = self.long_term[:self.long_term_capacity]
    
    # ========================================================================
    # Memory Retrieval
    # ========================================================================
    
    def get_recent_memories(
        self,
        count: int = 10,
        entry_type: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Get recent memories from short-term storage
        
        Args:
            count: Number of memories to retrieve
            entry_type: Filter by entry type (optional)
            
        Returns:
            List of recent memory entries
        """
        memories = list(self.short_term)
        
        if entry_type:
            memories = [m for m in memories if m.entry_type == entry_type]
        
        return memories[-count:]
    
    def get_important_memories(
        self,
        count: int = 10,
        min_importance: float = 0.7,
        entry_type: Optional[str] = None
    ) -> List[MemoryEntry]:
        """
        Get important memories from long-term storage
        
        Args:
            count: Number of memories to retrieve
            min_importance: Minimum importance threshold
            entry_type: Filter by entry type (optional)
            
        Returns:
            List of important memory entries
        """
        memories = [m for m in self.long_term if m.importance >= min_importance]
        
        if entry_type:
            memories = [m for m in memories if m.entry_type == entry_type]
        
        # Sort by importance and recency
        memories.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
        
        return memories[:count]
    
    def search_memories(
        self,
        query: str,
        search_short_term: bool = True,
        search_long_term: bool = True,
        max_results: int = 20
    ) -> List[MemoryEntry]:
        """
        Search memories by keyword
        
        Args:
            query: Search query
            search_short_term: Search short-term memory
            search_long_term: Search long-term memory
            max_results: Maximum results to return
            
        Returns:
            List of matching memory entries
        """
        results = []
        query_lower = query.lower()
        
        # Search short-term
        if search_short_term:
            for entry in self.short_term:
                if self._matches_query(entry, query_lower):
                    results.append(entry)
        
        # Search long-term
        if search_long_term:
            for entry in self.long_term:
                if self._matches_query(entry, query_lower):
                    results.append(entry)
        
        # Sort by relevance (importance) and recency
        results.sort(key=lambda e: (e.importance, e.timestamp), reverse=True)
        
        return results[:max_results]
    
    def _matches_query(self, entry: MemoryEntry, query: str) -> bool:
        """Check if memory entry matches query"""
        # Convert entry to string and search
        entry_str = json.dumps(entry.to_dict()).lower()
        return query in entry_str
    
    def get_memory_by_id(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get specific memory by ID"""
        # Search short-term
        for entry in self.short_term:
            if entry.entry_id == entry_id:
                return entry
        
        # Search long-term
        for entry in self.long_term:
            if entry.entry_id == entry_id:
                return entry
        
        return None
    
    def get_memories_by_type(
        self,
        entry_type: str,
        max_count: int = 50
    ) -> List[MemoryEntry]:
        """Get all memories of specific type"""
        memories = []
        
        # From short-term
        for entry in self.short_term:
            if entry.entry_type == entry_type:
                memories.append(entry)
        
        # From long-term
        for entry in self.long_term:
            if entry.entry_type == entry_type:
                memories.append(entry)
        
        # Sort by recency
        memories.sort(key=lambda e: e.timestamp, reverse=True)
        
        return memories[:max_count]
    
    # ========================================================================
    # Memory Management
    # ========================================================================
    
    def cleanup_old_memories(self) -> int:
        """
        Remove old, low-importance memories
        
        Returns:
            Number of memories cleaned
        """
        cleanup_age_seconds = self.cleanup_age_hours * 3600
        cleaned_count = 0
        
        # Cleanup long-term memory
        before_count = len(self.long_term)
        self.long_term = [
            entry for entry in self.long_term
            if not (
                entry.importance < self.consolidation_threshold and
                entry.is_older_than(cleanup_age_seconds)
            )
        ]
        cleaned_count = before_count - len(self.long_term)
        
        self.total_memories_cleaned += cleaned_count
        return cleaned_count
    
    def consolidate_memories(self) -> int:
        """
        Move important short-term memories to long-term
        
        Returns:
            Number of memories consolidated
        """
        consolidated_count = 0
        
        for entry in self.short_term:
            if entry.importance >= self.consolidation_threshold:
                # Check if not already in long-term
                if not any(e.entry_id == entry.entry_id for e in self.long_term):
                    self._consolidate_to_long_term(entry)
                    consolidated_count += 1
        
        return consolidated_count
    
    def clear(self) -> None:
        """Clear all memories"""
        self.short_term.clear()
        self.long_term.clear()
        self._entry_counter = 0
    
    def clear_short_term(self) -> None:
        """Clear only short-term memory"""
        self.short_term.clear()
    
    def clear_long_term(self) -> None:
        """Clear only long-term memory"""
        self.long_term.clear()
    
    # ========================================================================
    # Statistics & Information
    # ========================================================================
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get memory statistics"""
        return {
            'short_term_count': len(self.short_term),
            'long_term_count': len(self.long_term),
            'total_memories_created': self.total_memories_created,
            'total_memories_consolidated': self.total_memories_consolidated,
            'total_memories_cleaned': self.total_memories_cleaned,
            'consolidation_threshold': self.consolidation_threshold,
            'cleanup_age_hours': self.cleanup_age_hours
        }
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """Get summary of memory contents"""
        # Count by type
        type_counts = {}
        for entry in list(self.short_term) + self.long_term:
            type_counts[entry.entry_type] = type_counts.get(entry.entry_type, 0) + 1
        
        # Average importance
        all_memories = list(self.short_term) + self.long_term
        avg_importance = 0.0
        if all_memories:
            avg_importance = sum(e.importance for e in all_memories) / len(all_memories)
        
        return {
            'total_memories': len(all_memories),
            'short_term': len(self.short_term),
            'long_term': len(self.long_term),
            'by_type': type_counts,
            'average_importance': round(avg_importance, 2)
        }
    
    def export_memories(
        self,
        include_short_term: bool = True,
        include_long_term: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Export memories to list of dictionaries
        
        Args:
            include_short_term: Include short-term memories
            include_long_term: Include long-term memories
            
        Returns:
            List of memory dictionaries
        """
        memories = []
        
        if include_short_term:
            memories.extend([e.to_dict() for e in self.short_term])
        
        if include_long_term:
            memories.extend([e.to_dict() for e in self.long_term])
        
        return memories
    
    def import_memories(self, memories: List[Dict[str, Any]]) -> int:
        """
        Import memories from list of dictionaries
        
        Args:
            memories: List of memory dictionaries
            
        Returns:
            Number of memories imported
        """
        imported_count = 0
        
        for mem_dict in memories:
            entry = MemoryEntry(
                entry_id=mem_dict['entry_id'],
                entry_type=mem_dict['entry_type'],
                data=mem_dict['data'],
                timestamp=mem_dict['timestamp'],
                importance=mem_dict.get('importance', 0.5),
                metadata=mem_dict.get('metadata', {})
            )
            
            # Add to appropriate storage
            if entry.importance >= self.consolidation_threshold:
                self.long_term.append(entry)
            else:
                self.short_term.append(entry)
            
            imported_count += 1
        
        return imported_count
    
    # ========================================================================
    # String Representation
    # ========================================================================
    
    def __repr__(self) -> str:
        return (
            f"<AgentMemory(short_term={len(self.short_term)}, "
            f"long_term={len(self.long_term)})>"
        )
    
    def __str__(self) -> str:
        return (
            f"Memory: {len(self.short_term)} short-term, "
            f"{len(self.long_term)} long-term"
        )
    
    def __len__(self) -> int:
        """Total number of memories"""
        return len(self.short_term) + len(self.long_term)