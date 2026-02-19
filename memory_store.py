"""
Searchable, Self-Updating Memory Store for Personalized Browser Agent Behaviour

This module provides a comprehensive memory system for browser agents that:
- Stores interactions, preferences, and learned behaviors
- Provides fast semantic and keyword search
- Automatically updates based on agent actions
- Personalizes based on user patterns
"""

import sqlite3
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import hashlib


@dataclass
class Memory:
    """Represents a single memory entry"""
    id: Optional[int] = None
    timestamp: float = None
    memory_type: str = ""  # 'interaction', 'preference', 'learned_behavior', 'error', 'success'
    context: str = ""  # URL, page title, or context identifier
    action: str = ""  # What the agent did
    result: str = ""  # What happened
    user_feedback: Optional[str] = None  # positive, negative, neutral
    importance: float = 1.0  # 0-10 scale
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}


class MemoryStore:
    """Main memory store with search and auto-update capabilities"""
    
    def __init__(self, db_path: str = "agent_memory.db"):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self._initialize_database()
        
        # Personalization tracking
        self.user_patterns = defaultdict(int)
        self.success_patterns = defaultdict(list)
        self.failure_patterns = defaultdict(list)
        
        # Load existing patterns
        self._load_patterns()
    
    def _initialize_database(self):
        """Initialize SQLite database with required tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        
        # Main memories table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL NOT NULL,
                memory_type TEXT NOT NULL,
                context TEXT,
                action TEXT,
                result TEXT,
                user_feedback TEXT,
                importance REAL DEFAULT 1.0,
                tags TEXT,
                metadata TEXT
            )
        """)
        
        # User preferences table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                confidence REAL DEFAULT 1.0,
                updated_at REAL
            )
        """)
        
        # Pattern tracking table
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS patterns (
                pattern_key TEXT PRIMARY KEY,
                pattern_type TEXT,
                occurrences INTEGER DEFAULT 1,
                success_rate REAL DEFAULT 0.5,
                last_seen REAL,
                data TEXT
            )
        """)
        
        # Create indexes for faster search
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_memory_type ON memories(memory_type)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_context ON memories(context)
        """)
        
        self.conn.commit()
    
    def add_memory(self, memory: Memory) -> int:
        """Add a new memory to the store"""
        tags_json = json.dumps(memory.tags)
        metadata_json = json.dumps(memory.metadata)
        
        self.cursor.execute("""
            INSERT INTO memories 
            (timestamp, memory_type, context, action, result, user_feedback, importance, tags, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            memory.timestamp,
            memory.memory_type,
            memory.context,
            memory.action,
            memory.result,
            memory.user_feedback,
            memory.importance,
            tags_json,
            metadata_json
        ))
        
        self.conn.commit()
        memory_id = self.cursor.lastrowid
        
        # Auto-update patterns
        self._update_patterns(memory)
        
        return memory_id
    
    def search_memories(
        self,
        query: Optional[str] = None,
        memory_type: Optional[str] = None,
        context: Optional[str] = None,
        tags: Optional[List[str]] = None,
        min_importance: float = 0,
        limit: int = 50
    ) -> List[Memory]:
        """
        Search memories with various filters
        
        Args:
            query: Text to search in action and result fields
            memory_type: Filter by memory type
            context: Filter by context
            tags: Filter by tags
            min_importance: Minimum importance threshold
            limit: Maximum results to return
        """
        conditions = ["importance >= ?"]
        params = [min_importance]
        
        if memory_type:
            conditions.append("memory_type = ?")
            params.append(memory_type)
        
        if context:
            conditions.append("context LIKE ?")
            params.append(f"%{context}%")
        
        if query:
            conditions.append("(action LIKE ? OR result LIKE ? OR context LIKE ?)")
            params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
        
        where_clause = " AND ".join(conditions)
        
        sql = f"""
            SELECT id, timestamp, memory_type, context, action, result, 
                   user_feedback, importance, tags, metadata
            FROM memories
            WHERE {where_clause}
            ORDER BY importance DESC, timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        
        self.cursor.execute(sql, params)
        results = []
        
        for row in self.cursor.fetchall():
            memory = Memory(
                id=row[0],
                timestamp=row[1],
                memory_type=row[2],
                context=row[3],
                action=row[4],
                result=row[5],
                user_feedback=row[6],
                importance=row[7],
                tags=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {}
            )
            
            # Filter by tags if specified
            if tags and not any(tag in memory.tags for tag in tags):
                continue
            
            results.append(memory)
        
        return results[:limit]
    
    def get_recent_memories(self, count: int = 10, memory_type: Optional[str] = None) -> List[Memory]:
        """Get the most recent memories"""
        if memory_type:
            self.cursor.execute("""
                SELECT id, timestamp, memory_type, context, action, result,
                       user_feedback, importance, tags, metadata
                FROM memories
                WHERE memory_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (memory_type, count))
        else:
            self.cursor.execute("""
                SELECT id, timestamp, memory_type, context, action, result,
                       user_feedback, importance, tags, metadata
                FROM memories
                ORDER BY timestamp DESC
                LIMIT ?
            """, (count,))
        
        results = []
        for row in self.cursor.fetchall():
            results.append(Memory(
                id=row[0],
                timestamp=row[1],
                memory_type=row[2],
                context=row[3],
                action=row[4],
                result=row[5],
                user_feedback=row[6],
                importance=row[7],
                tags=json.loads(row[8]) if row[8] else [],
                metadata=json.loads(row[9]) if row[9] else {}
            ))
        
        return results
    
    def set_preference(self, key: str, value: Any, confidence: float = 1.0):
        """Set a user preference"""
        value_json = json.dumps(value)
        timestamp = time.time()
        
        self.cursor.execute("""
            INSERT OR REPLACE INTO preferences (key, value, confidence, updated_at)
            VALUES (?, ?, ?, ?)
        """, (key, value_json, confidence, timestamp))
        
        self.conn.commit()
    
    def get_preference(self, key: str, default: Any = None) -> Any:
        """Get a user preference"""
        self.cursor.execute("""
            SELECT value FROM preferences WHERE key = ?
        """, (key,))
        
        row = self.cursor.fetchone()
        if row:
            return json.loads(row[0])
        return default
    
    def get_all_preferences(self) -> Dict[str, Any]:
        """Get all user preferences"""
        self.cursor.execute("SELECT key, value, confidence FROM preferences")
        
        preferences = {}
        for row in self.cursor.fetchall():
            preferences[row[0]] = {
                'value': json.loads(row[1]),
                'confidence': row[2]
            }
        
        return preferences
    
    def _update_patterns(self, memory: Memory):
        """Auto-update learned patterns based on new memory"""
        # Create pattern key based on context and action
        pattern_key = self._generate_pattern_key(memory.context, memory.action)
        
        # Track success/failure
        is_success = memory.user_feedback == 'positive' or memory.memory_type == 'success'
        is_failure = memory.user_feedback == 'negative' or memory.memory_type == 'error'
        
        # Update pattern tracking
        self.cursor.execute("""
            SELECT occurrences, success_rate, data FROM patterns WHERE pattern_key = ?
        """, (pattern_key,))
        
        row = self.cursor.fetchone()
        
        if row:
            occurrences = row[0] + 1
            old_success_rate = row[1]
            
            # Update success rate with exponential moving average
            if is_success:
                new_success_rate = old_success_rate * 0.9 + 0.1 * 1.0
            elif is_failure:
                new_success_rate = old_success_rate * 0.9 + 0.1 * 0.0
            else:
                new_success_rate = old_success_rate
            
            self.cursor.execute("""
                UPDATE patterns 
                SET occurrences = ?, success_rate = ?, last_seen = ?
                WHERE pattern_key = ?
            """, (occurrences, new_success_rate, time.time(), pattern_key))
        else:
            # New pattern
            initial_success_rate = 1.0 if is_success else 0.0 if is_failure else 0.5
            pattern_data = json.dumps({
                'context': memory.context,
                'action': memory.action,
                'typical_result': memory.result
            })
            
            self.cursor.execute("""
                INSERT INTO patterns (pattern_key, pattern_type, occurrences, success_rate, last_seen, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (pattern_key, memory.memory_type, 1, initial_success_rate, time.time(), pattern_data))
        
        self.conn.commit()
    
    def _generate_pattern_key(self, context: str, action: str) -> str:
        """Generate a unique key for a context-action pattern"""
        combined = f"{context}::{action}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _load_patterns(self):
        """Load existing patterns into memory"""
        self.cursor.execute("SELECT pattern_key, success_rate, data FROM patterns")
        
        for row in self.cursor.fetchall():
            pattern_key = row[0]
            success_rate = row[1]
            
            if success_rate > 0.7:
                self.success_patterns[pattern_key].append(success_rate)
            elif success_rate < 0.3:
                self.failure_patterns[pattern_key].append(success_rate)
    
    def get_recommendations(self, context: str, action: str = None) -> List[Dict[str, Any]]:
        """
        Get personalized recommendations based on learned patterns
        
        Args:
            context: Current context (URL, page, etc.)
            action: Optional action to evaluate
        
        Returns:
            List of recommendations with confidence scores
        """
        recommendations = []
        
        if action:
            # Evaluate specific action
            pattern_key = self._generate_pattern_key(context, action)
            self.cursor.execute("""
                SELECT success_rate, occurrences, data FROM patterns WHERE pattern_key = ?
            """, (pattern_key,))
            
            row = self.cursor.fetchone()
            if row:
                recommendations.append({
                    'action': action,
                    'confidence': row[0],
                    'based_on_experiences': row[1],
                    'data': json.loads(row[2])
                })
        else:
            # Find best actions for this context
            # Search for similar contexts
            self.cursor.execute("""
                SELECT pattern_key, success_rate, occurrences, data 
                FROM patterns 
                WHERE data LIKE ?
                ORDER BY success_rate DESC, occurrences DESC
                LIMIT 5
            """, (f"%{context}%",))
            
            for row in self.cursor.fetchall():
                data = json.loads(row[3])
                recommendations.append({
                    'action': data.get('action'),
                    'confidence': row[1],
                    'based_on_experiences': row[2],
                    'typical_result': data.get('typical_result')
                })
        
        return recommendations
    
    def update_memory_importance(self, memory_id: int, new_importance: float):
        """Update the importance score of a memory"""
        self.cursor.execute("""
            UPDATE memories SET importance = ? WHERE id = ?
        """, (new_importance, memory_id))
        self.conn.commit()
    
    def add_feedback(self, memory_id: int, feedback: str):
        """Add user feedback to a memory"""
        self.cursor.execute("""
            UPDATE memories SET user_feedback = ? WHERE id = ?
        """, (feedback, memory_id))
        self.conn.commit()
        
        # Fetch the memory to update patterns
        self.cursor.execute("""
            SELECT timestamp, memory_type, context, action, result, user_feedback, importance, tags, metadata
            FROM memories WHERE id = ?
        """, (memory_id,))
        
        row = self.cursor.fetchone()
        if row:
            memory = Memory(
                id=memory_id,
                timestamp=row[0],
                memory_type=row[1],
                context=row[2],
                action=row[3],
                result=row[4],
                user_feedback=row[5],
                importance=row[6],
                tags=json.loads(row[7]) if row[7] else [],
                metadata=json.loads(row[8]) if row[8] else {}
            )
            self._update_patterns(memory)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the memory store"""
        stats = {}
        
        # Total memories
        self.cursor.execute("SELECT COUNT(*) FROM memories")
        stats['total_memories'] = self.cursor.fetchone()[0]
        
        # Memories by type
        self.cursor.execute("""
            SELECT memory_type, COUNT(*) FROM memories GROUP BY memory_type
        """)
        stats['by_type'] = dict(self.cursor.fetchall())
        
        # Total patterns
        self.cursor.execute("SELECT COUNT(*) FROM patterns")
        stats['total_patterns'] = self.cursor.fetchone()[0]
        
        # High success patterns
        self.cursor.execute("""
            SELECT COUNT(*) FROM patterns WHERE success_rate > 0.7
        """)
        stats['successful_patterns'] = self.cursor.fetchone()[0]
        
        # Total preferences
        self.cursor.execute("SELECT COUNT(*) FROM preferences")
        stats['total_preferences'] = self.cursor.fetchone()[0]
        
        return stats
    
    def cleanup_old_memories(self, days: int = 90, min_importance: float = 3.0):
        """Remove old, low-importance memories to keep the store manageable"""
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        self.cursor.execute("""
            DELETE FROM memories 
            WHERE timestamp < ? AND importance < ?
        """, (cutoff_time, min_importance))
        
        deleted_count = self.cursor.rowcount
        self.conn.commit()
        
        return deleted_count
    
    def export_memories(self, filepath: str = None) -> str:
        """Export all memories to JSON"""
        memories = self.search_memories(limit=10000)
        
        export_data = {
            'export_timestamp': time.time(),
            'total_memories': len(memories),
            'memories': [asdict(m) for m in memories],
            'preferences': self.get_all_preferences(),
            'statistics': self.get_statistics()
        }
        
        json_data = json.dumps(export_data, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_data)
        
        return json_data
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
