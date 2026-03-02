"""
Blackboard System
Shared knowledge base for agent coordination
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from collections import defaultdict


class BlackboardEntry:
    """Single entry in the blackboard"""
    
    def __init__(
        self,
        key: str,
        value: Any,
        author: str,
        ttl: Optional[int] = None,
        metadata: Optional[Dict] = None
    ):
        self.key = key
        self.value = value
        self.author = author
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.ttl = ttl  # Time to live in seconds
        self.metadata = metadata or {}
        self.version = 1
    
    def is_expired(self) -> bool:
        """Check if entry has expired"""
        if self.ttl is None:
            return False
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl
    
    def update(self, value: Any, author: str) -> None:
        """Update entry value"""
        self.value = value
        self.author = author
        self.updated_at = datetime.now()
        self.version += 1
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'key': self.key,
            'value': self.value,
            'author': self.author,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'ttl': self.ttl,
            'metadata': self.metadata,
            'version': self.version
        }


class Blackboard:
    """
    Shared knowledge base for agent coordination
    
    Features:
    - Read/write operations
    - TTL support
    - Pattern matching queries
    - Change notifications
    - Conflict resolution
    - Version tracking
    - Access control
    """
    
    def __init__(
        self,
        enable_notifications: bool = True,
        cleanup_interval: int = 60
    ):
        """
        Initialize blackboard
        
        Args:
            enable_notifications: Enable change notifications
            cleanup_interval: Cleanup interval in seconds
        """
        # Storage
        self.entries: Dict[str, BlackboardEntry] = {}
        self.lock = asyncio.Lock()
        
        # Notifications
        self.enable_notifications = enable_notifications
        self.subscribers: Dict[str, Set[str]] = defaultdict(set)  # key -> set of agent names
        self.notification_callbacks: Dict[str, Any] = {}  # agent_name -> callback
        
        # Statistics
        self.total_writes = 0
        self.total_reads = 0
        self.total_deletes = 0
        
        # Cleanup
        self.cleanup_interval = cleanup_interval
        self._cleanup_task: Optional[asyncio.Task] = None
        
        # Logging
        self.logger = logging.getLogger("Blackboard")
        
        self.logger.info("✅ Blackboard initialized")
    
    # ========================================================================
    # Write Operations
    # ========================================================================
    
    async def write(
        self,
        key: str,
        value: Any,
        author: str,
        ttl: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        Write value to blackboard
        
        Args:
            key: Knowledge key
            value: Knowledge value
            author: Agent writing the value
            ttl: Time to live in seconds
            metadata: Additional metadata
            
        Returns:
            True if written successfully
        """
        async with self.lock:
            try:
                if key in self.entries:
                    # Update existing entry
                    self.entries[key].update(value, author)
                else:
                    # Create new entry
                    self.entries[key] = BlackboardEntry(
                        key=key,
                        value=value,
                        author=author,
                        ttl=ttl,
                        metadata=metadata
                    )
                
                self.total_writes += 1
                self.logger.debug(f"📝 {author} wrote '{key}'")
                
                # Notify subscribers
                if self.enable_notifications:
                    await self._notify_subscribers(key, value, author)
                
                return True
                
            except Exception as e:
                self.logger.error(f"❌ Error writing to blackboard: {e}")
                return False
    
    async def write_many(
        self,
        entries: Dict[str, Any],
        author: str,
        ttl: Optional[int] = None
    ) -> int:
        """
        Write multiple entries
        
        Args:
            entries: Dictionary of key-value pairs
            author: Agent writing the values
            ttl: Time to live for all entries
            
        Returns:
            Number of entries written
        """
        count = 0
        for key, value in entries.items():
            if await self.write(key, value, author, ttl):
                count += 1
        return count
    
    # ========================================================================
    # Read Operations
    # ========================================================================
    
    async def read(self, key: str) -> Optional[Any]:
        """
        Read value from blackboard
        
        Args:
            key: Knowledge key
            
        Returns:
            Value or None if not found
        """
        async with self.lock:
            self.total_reads += 1
            
            if key not in self.entries:
                return None
            
            entry = self.entries[key]
            
            # Check if expired
            if entry.is_expired():
                await self._delete_entry(key)
                return None
            
            self.logger.debug(f"📖 Read '{key}'")
            return entry.value
    
    async def read_entry(self, key: str) -> Optional[BlackboardEntry]:
        """
        Read full entry from blackboard
        
        Args:
            key: Knowledge key
            
        Returns:
            BlackboardEntry or None
        """
        async with self.lock:
            self.total_reads += 1
            
            if key not in self.entries:
                return None
            
            entry = self.entries[key]
            
            # Check if expired
            if entry.is_expired():
                await self._delete_entry(key)
                return None
            
            return entry
    
    async def read_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Read multiple values
        
        Args:
            keys: List of keys to read
            
        Returns:
            Dictionary of key-value pairs
        """
        result = {}
        for key in keys:
            value = await self.read(key)
            if value is not None:
                result[key] = value
        return result
    
    async def read_all(self) -> Dict[str, Any]:
        """
        Read all values from blackboard
        
        Returns:
            Dictionary of all key-value pairs
        """
        async with self.lock:
            result = {}
            for key, entry in self.entries.items():
                if not entry.is_expired():
                    result[key] = entry.value
            return result
    
    # ========================================================================
    # Query Operations
    # ========================================================================
    
    async def query(self, pattern: str) -> Dict[str, Any]:
        """
        Query blackboard by key pattern
        
        Args:
            pattern: Key pattern (supports wildcards)
            
        Returns:
            Dictionary of matching key-value pairs
        """
        async with self.lock:
            result = {}
            
            # Simple pattern matching (supports * wildcard)
            import re
            regex_pattern = pattern.replace('*', '.*')
            regex = re.compile(f"^{regex_pattern}$")
            
            for key, entry in self.entries.items():
                if regex.match(key) and not entry.is_expired():
                    result[key] = entry.value
            
            self.logger.debug(f"🔍 Query '{pattern}': {len(result)} results")
            return result
    
    async def query_by_author(self, author: str) -> Dict[str, Any]:
        """
        Query entries by author
        
        Args:
            author: Agent name
            
        Returns:
            Dictionary of entries by this author
        """
        async with self.lock:
            result = {}
            for key, entry in self.entries.items():
                if entry.author == author and not entry.is_expired():
                    result[key] = entry.value
            return result
    
    async def query_by_metadata(self, metadata_key: str, metadata_value: Any) -> Dict[str, Any]:
        """
        Query entries by metadata
        
        Args:
            metadata_key: Metadata key to match
            metadata_value: Metadata value to match
            
        Returns:
            Dictionary of matching entries
        """
        async with self.lock:
            result = {}
            for key, entry in self.entries.items():
                if (not entry.is_expired() and
                    metadata_key in entry.metadata and
                    entry.metadata[metadata_key] == metadata_value):
                    result[key] = entry.value
            return result
    
    # ========================================================================
    # Delete Operations
    # ========================================================================
    
    async def delete(self, key: str) -> bool:
        """
        Delete entry from blackboard
        
        Args:
            key: Knowledge key
            
        Returns:
            True if deleted
        """
        async with self.lock:
            return await self._delete_entry(key)
    
    async def _delete_entry(self, key: str) -> bool:
        """Internal delete method (assumes lock is held)"""
        if key in self.entries:
            del self.entries[key]
            self.total_deletes += 1
            self.logger.debug(f"🗑️  Deleted '{key}'")
            return True
        return False
    
    async def delete_many(self, keys: List[str]) -> int:
        """
        Delete multiple entries
        
        Args:
            keys: List of keys to delete
            
        Returns:
            Number of entries deleted
        """
        count = 0
        for key in keys:
            if await self.delete(key):
                count += 1
        return count
    
    async def clear(self) -> int:
        """
        Clear all entries
        
        Returns:
            Number of entries cleared
        """
        async with self.lock:
            count = len(self.entries)
            self.entries.clear()
            self.logger.info(f"🗑️  Cleared {count} entries")
            return count
    
    # ========================================================================
    # Subscription & Notifications
    # ========================================================================
    
    async def subscribe(
        self,
        agent_name: str,
        key: str,
        callback: Optional[Any] = None
    ) -> None:
        """
        Subscribe to changes on a key
        
        Args:
            agent_name: Name of subscribing agent
            key: Key to watch
            callback: Optional callback function
        """
        self.subscribers[key].add(agent_name)
        
        if callback:
            self.notification_callbacks[agent_name] = callback
        
        self.logger.debug(f"👁️  {agent_name} subscribed to '{key}'")
    
    async def unsubscribe(self, agent_name: str, key: str) -> None:
        """Unsubscribe from key changes"""
        if key in self.subscribers:
            self.subscribers[key].discard(agent_name)
            self.logger.debug(f"👁️  {agent_name} unsubscribed from '{key}'")
    
    async def _notify_subscribers(self, key: str, value: Any, author: str) -> None:
        """Notify subscribers of changes"""
        if key in self.subscribers:
            for agent_name in self.subscribers[key]:
                if agent_name in self.notification_callbacks:
                    try:
                        callback = self.notification_callbacks[agent_name]
                        if asyncio.iscoroutinefunction(callback):
                            await callback(key, value, author)
                        else:
                            callback(key, value, author)
                    except Exception as e:
                        self.logger.error(f"❌ Notification error: {e}")
    
    # ========================================================================
    # Utility Methods
    # ========================================================================
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        async with self.lock:
            if key not in self.entries:
                return False
            entry = self.entries[key]
            if entry.is_expired():
                await self._delete_entry(key)
                return False
            return True
    
    async def get_keys(self) -> List[str]:
        """Get all keys"""
        async with self.lock:
            return [
                key for key, entry in self.entries.items()
                if not entry.is_expired()
            ]
    
    async def get_size(self) -> int:
        """Get number of entries"""
        async with self.lock:
            return len([
                entry for entry in self.entries.values()
                if not entry.is_expired()
            ])
    
    # ========================================================================
    # Cleanup
    # ========================================================================
    
    async def cleanup_expired(self) -> int:
        """
        Remove expired entries
        
        Returns:
            Number of entries removed
        """
        async with self.lock:
            expired_keys = [
                key for key, entry in self.entries.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                await self._delete_entry(key)
            
            if expired_keys:
                self.logger.debug(f"🧹 Cleaned up {len(expired_keys)} expired entries")
            
            return len(expired_keys)
    
    async def start_cleanup_task(self) -> None:
        """Start automatic cleanup task"""
        if self._cleanup_task is None:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())
            self.logger.info("🧹 Cleanup task started")
    
    async def stop_cleanup_task(self) -> None:
        """Stop automatic cleanup task"""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None
            self.logger.info("🧹 Cleanup task stopped")
    
    async def _cleanup_loop(self) -> None:
        """Automatic cleanup loop"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval)
                await self.cleanup_expired()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Cleanup error: {e}")
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    def get_statistics(self) -> Dict:
        """Get blackboard statistics"""
        return {
            'total_entries': len(self.entries),
            'total_writes': self.total_writes,
            'total_reads': self.total_reads,
            'total_deletes': self.total_deletes,
            'total_subscribers': sum(len(subs) for subs in self.subscribers.values())
        }
    
    async def get_entry_info(self, key: str) -> Optional[Dict]:
        """Get detailed entry information"""
        entry = await self.read_entry(key)
        if entry:
            return entry.to_dict()
        return None
    
    # ========================================================================
    # String Representation
    # ========================================================================
    
    def __repr__(self) -> str:
        return f"<Blackboard(entries={len(self.entries)})>"
    
    def __str__(self) -> str:
        return f"Blackboard: {len(self.entries)} entries"