"""
State Store - Persistent storage for agents
============================================

SQLite for durable storage, Redis for fast caching and pub/sub.
"""

import sqlite3
import json
import redis
from typing import Optional, Dict, Any, List
from pathlib import Path
from contextlib import contextmanager
import pickle


class StateStore:
    """
    Dual-layer state storage for agents.
    
    - SQLite: Durable, persistent storage for agent memory, tasks, projects
    - Redis: Fast cache for active state, pub/sub for coordination
    """
    
    def __init__(
        self,
        db_path: str = "~/.agentic_ai/state.db",
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
    ):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
        )
        
        self._init_db()
    
    def _init_db(self):
        """Initialize SQLite tables."""
        with self._get_conn() as conn:
            # Agent state table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_state (
                    agent_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    state_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tasks table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    task_id TEXT PRIMARY KEY,
                    agent_id TEXT,
                    task_type TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 0,
                    payload_json TEXT,
                    result_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (agent_id) REFERENCES agent_state(agent_id)
                )
            """)
            
            # Project memory table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS project_memory (
                    memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id TEXT NOT NULL,
                    agent_id TEXT,
                    memory_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    embedding BLOB,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_agent ON tasks(agent_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_memory_project ON project_memory(project_id)")
            
            conn.commit()
    
    @contextmanager
    def _get_conn(self):
        """Get database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # === Agent State ===
    
    def save_agent_state(self, agent_id: str, agent_type: str, state: Dict[str, Any]):
        """Save agent state to SQLite and cache to Redis."""
        state_json = json.dumps(state)
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO agent_state (agent_id, agent_type, state_json, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(agent_id) DO UPDATE SET
                    state_json = excluded.state_json,
                    updated_at = CURRENT_TIMESTAMP
            """, (agent_id, agent_type, state_json))
            conn.commit()
        
        # Cache in Redis
        self.redis_client.hset(
            "agent:state",
            agent_id,
            state_json,
        )
    
    def get_agent_state(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent state (Redis cache first, then SQLite)."""
        # Try Redis cache
        cached = self.redis_client.hget("agent:state", agent_id)
        if cached:
            return json.loads(cached)
        
        # Fall back to SQLite
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT state_json FROM agent_state WHERE agent_id = ?",
                (agent_id,)
            ).fetchone()
            
            if row:
                state = json.loads(row["state_json"])
                # Cache it
                self.redis_client.hset("agent:state", agent_id, row["state_json"])
                return state
        
        return None
    
    # === Tasks ===
    
    def create_task(
        self,
        task_id: str,
        task_type: str,
        agent_id: Optional[str] = None,
        priority: int = 0,
        payload: Optional[Dict[str, Any]] = None,
    ):
        """Create a new task."""
        payload_json = json.dumps(payload) if payload else None
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO tasks (task_id, agent_id, task_type, priority, payload_json)
                VALUES (?, ?, ?, ?, ?)
            """, (task_id, agent_id, task_type, priority, payload_json))
            conn.commit()
        
        # Publish task creation
        self.redis_client.publish(
            "tasks:new",
            json.dumps({"task_id": task_id, "task_type": task_type, "agent_id": agent_id})
        )
    
    def get_pending_tasks(self, agent_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Get pending tasks, optionally filtered by agent."""
        with self._get_conn() as conn:
            if agent_id:
                rows = conn.execute("""
                    SELECT * FROM tasks
                    WHERE agent_id = ? AND status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                """, (agent_id, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT * FROM tasks
                    WHERE status = 'pending'
                    ORDER BY priority DESC, created_at ASC
                    LIMIT ?
                """, (limit,)).fetchall()
            
            return [dict(row) for row in rows]
    
    def update_task_status(self, task_id: str, status: str, result: Optional[Dict] = None):
        """Update task status."""
        result_json = json.dumps(result) if result else None
        
        with self._get_conn() as conn:
            if status == "completed":
                conn.execute("""
                    UPDATE tasks
                    SET status = ?, result_json = ?, completed_at = CURRENT_TIMESTAMP
                    WHERE task_id = ?
                """, (status, result_json, task_id))
            else:
                conn.execute("""
                    UPDATE tasks SET status = ? WHERE task_id = ?
                """, (status, task_id))
            conn.commit()
    
    # === Project Memory ===
    
    def save_memory(
        self,
        project_id: str,
        memory_type: str,
        content: str,
        agent_id: Optional[str] = None,
        embedding: Optional[List[float]] = None,
    ):
        """Save a memory entry for a project."""
        embedding_blob = pickle.dumps(embedding) if embedding else None
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO project_memory
                (project_id, agent_id, memory_type, content, embedding)
                VALUES (?, ?, ?, ?, ?)
            """, (project_id, agent_id, memory_type, content, embedding_blob))
            conn.commit()
    
    def get_project_memories(
        self,
        project_id: str,
        memory_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Get memories for a project."""
        with self._get_conn() as conn:
            if memory_type:
                rows = conn.execute("""
                    SELECT memory_id, agent_id, memory_type, content, created_at
                    FROM project_memory
                    WHERE project_id = ? AND memory_type = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (project_id, memory_type, limit)).fetchall()
            else:
                rows = conn.execute("""
                    SELECT memory_id, agent_id, memory_type, content, created_at
                    FROM project_memory
                    WHERE project_id = ?
                    ORDER BY created_at DESC
                    LIMIT ?
                """, (project_id, limit)).fetchall()
            
            return [dict(row) for row in rows]
    
    # === Redis Pub/Sub ===
    
    def publish(self, channel: str, message: Dict[str, Any]):
        """Publish a message to a Redis channel."""
        self.redis_client.publish(channel, json.dumps(message))
    
    def subscribe(self, channel: str):
        """Get a pubsub object for subscribing to channels."""
        pubsub = self.redis_client.pubsub()
        pubsub.subscribe(channel)
        return pubsub
    
    def close(self):
        """Close connections."""
        self.redis_client.close()