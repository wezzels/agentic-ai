"""
ACP - Agent Communication Protocol
==================================

Message format and bus for inter-agent communication.
"""

import json
import uuid
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
import redis


class MessageType(str, Enum):
    """Types of messages agents can exchange."""
    
    # Task management
    TASK_REQUEST = "task_request"          # Request a task to be done
    TASK_ACCEPT = "task_accept"             # Accept a task
    TASK_REJECT = "task_reject"             # Reject a task
    TASK_COMPLETE = "task_complete"          # Task completed
    TASK_FAILED = "task_failed"             # Task failed
    
    # Information exchange
    QUERY = "query"                         # Ask for information
    RESPONSE = "response"                   # Respond to query
    BROADCAST = "broadcast"                 # Broadcast to all agents
    
    # Coordination
    HANDOFF = "handoff"                     # Hand off work to another agent
    COLLABORATE = "collaborate"             # Request collaboration
    SYNC = "sync"                           # Sync state
    
    # Status
    STATUS_UPDATE = "status_update"         # Agent status update
    HEARTBEAT = "heartbeat"                 # Keepalive
    
    # Error
    ERROR = "error"                         # Error message


class Priority(int, Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class ACPMessage:
    """
    Agent Communication Protocol Message.
    
    Standard message format for all inter-agent communication.
    """
    
    # Core fields
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: MessageType = MessageType.BROADCAST
    priority: Priority = Priority.NORMAL
    
    # Routing
    sender: str = ""                        # Agent ID of sender
    recipient: str = ""                     # Agent ID of recipient (empty = broadcast)
    channel: str = "default"               # Channel name for topic-based routing
    
    # Content
    subject: str = ""                       # Brief subject line
    body: Dict[str, Any] = field(default_factory=dict)  # Message payload
    
    # Metadata
    correlation_id: str = ""                # ID of message this responds to
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: Optional[str] = None        # Expiration timestamp
    
    # Processing
    retry_count: int = 0
    max_retries: int = 3
    
    def to_json(self) -> str:
        """Serialize message to JSON string."""
        data = asdict(self)
        data["type"] = self.type.value
        data["priority"] = self.priority.value
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> "ACPMessage":
        """Deserialize message from JSON string."""
        data = json.loads(json_str)
        data["type"] = MessageType(data["type"])
        data["priority"] = Priority(data["priority"])
        return cls(**data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["type"] = self.type.value
        data["priority"] = self.priority.value
        return data


class ACPBus:
    """
    Redis-based message bus for agent communication.
    
    Provides:
    - Pub/sub for broadcasts
    - Point-to-point messaging
    - Channel-based routing
    - Message persistence for offline agents
    """
    
    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_db: int = 0,
        agent_id: str = "",
    ):
        self.redis = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True,
        )
        self.agent_id = agent_id
        self._pubsub: Optional[redis.client.PubSub] = None
        self._handlers: Dict[str, Callable[[ACPMessage], None]] = {}
    
    def connect(self):
        """Connect to the message bus."""
        self._pubsub = self.redis.pubsub()
    
    def disconnect(self):
        """Disconnect from the message bus."""
        if self._pubsub:
            self._pubsub.close()
            self._pubsub = None
    
    # === Publishing ===
    
    def send(self, message: ACPMessage) -> bool:
        """
        Send a message to a specific agent.
        
        Uses a dedicated channel for the recipient.
        """
        if not message.sender:
            message.sender = self.agent_id
        
        channel = f"agent:{message.recipient}"
        self.redis.publish(channel, message.to_json())
        
        # Also store in pending queue for offline retrieval
        self.redis.lpush(
            f"pending:{message.recipient}",
            message.to_json()
        )
        
        return True
    
    def broadcast(self, message: ACPMessage) -> bool:
        """
        Broadcast to all agents on a channel.
        
        Use message.channel to specify topic.
        """
        if not message.sender:
            message.sender = self.agent_id
        
        channel = f"channel:{message.channel}"
        self.redis.publish(channel, message.to_json())
        return True
    
    def publish_status(self, status: str, details: Optional[Dict] = None):
        """Publish agent status update."""
        message = ACPMessage(
            type=MessageType.STATUS_UPDATE,
            sender=self.agent_id,
            channel="status",
            body={"status": status, "details": details or {}},
        )
        self.broadcast(message)
    
    # === Subscribing ===
    
    def subscribe_agent(self, handler: Callable[[ACPMessage], None]):
        """
        Subscribe to direct messages for this agent.
        
        Args:
            handler: Function to call when message received
        """
        if not self._pubsub:
            self.connect()
        
        channel = f"agent:{self.agent_id}"
        self._pubsub.subscribe(channel)
        self._handlers[channel] = handler
    
    def subscribe_channel(
        self,
        channel: str,
        handler: Callable[[ACPMessage], None],
    ):
        """
        Subscribe to a channel for broadcasts.
        
        Args:
            channel: Channel name
            handler: Function to call when message received
        """
        if not self._pubsub:
            self.connect()
        
        full_channel = f"channel:{channel}"
        self._pubsub.subscribe(full_channel)
        self._handlers[full_channel] = handler
    
    def get_pending_messages(self, limit: int = 10) -> List[ACPMessage]:
        """
        Get pending messages sent while offline.
        
        Returns up to `limit` messages and removes them from queue.
        """
        messages = []
        for _ in range(limit):
            data = self.redis.rpop(f"pending:{self.agent_id}")
            if data:
                messages.append(ACPMessage.from_json(data))
            else:
                break
        return messages
    
    def listen(self, timeout: float = 1.0) -> Optional[ACPMessage]:
        """
        Listen for messages (blocking with timeout).
        
        Returns a message if available, None otherwise.
        """
        if not self._pubsub:
            return None
        
        try:
            msg = self._pubsub.get_message(timeout=timeout)
            if msg and msg["type"] == "message":
                channel = msg["channel"]
                handler = self._handlers.get(channel)
                if handler:
                    message = ACPMessage.from_json(msg["data"])
                    handler(message)
                    return message
        except Exception:
            pass
        
        return None
    
    def listen_loop(self, timeout: float = 1.0):
        """
        Continuous listen loop (generator).
        
        Yields messages as they arrive.
        """
        while True:
            msg = self.listen(timeout=timeout)
            if msg:
                yield msg
    
    # === Task Coordination ===
    
    def request_task(
        self,
        recipient: str,
        task_type: str,
        payload: Dict[str, Any],
        priority: Priority = Priority.NORMAL,
    ) -> str:
        """
        Request another agent to perform a task.
        
        Returns the correlation ID for tracking responses.
        """
        correlation_id = str(uuid.uuid4())
        
        message = ACPMessage(
            type=MessageType.TASK_REQUEST,
            sender=self.agent_id,
            recipient=recipient,
            priority=priority,
            correlation_id=correlation_id,
            subject=task_type,
            body=payload,
        )
        
        self.send(message)
        return correlation_id
    
    def accept_task(self, request: ACPMessage, details: Optional[Dict] = None):
        """Accept a task request."""
        response = ACPMessage(
            type=MessageType.TASK_ACCEPT,
            sender=self.agent_id,
            recipient=request.sender,
            correlation_id=request.id,
            body=details or {},
        )
        self.send(response)
    
    def reject_task(
        self,
        request: ACPMessage,
        reason: str,
    ):
        """Reject a task request."""
        response = ACPMessage(
            type=MessageType.TASK_REJECT,
            sender=self.agent_id,
            recipient=request.sender,
            correlation_id=request.id,
            body={"reason": reason},
        )
        self.send(response)
    
    def complete_task(
        self,
        request: ACPMessage,
        result: Dict[str, Any],
    ):
        """Mark a task as completed."""
        response = ACPMessage(
            type=MessageType.TASK_COMPLETE,
            sender=self.agent_id,
            recipient=request.sender,
            correlation_id=request.id,
            body={"result": result},
        )
        self.send(response)
    
    def fail_task(
        self,
        request: ACPMessage,
        error: str,
        details: Optional[Dict] = None,
    ):
        """Mark a task as failed."""
        response = ACPMessage(
            type=MessageType.TASK_FAILED,
            sender=self.agent_id,
            recipient=request.sender,
            correlation_id=request.id,
            body={"error": error, "details": details or {}},
        )
        self.send(response)
    
    # === Query/Response ===
    
    def query(
        self,
        recipient: str,
        question: str,
        context: Optional[Dict] = None,
    ) -> str:
        """
        Query another agent for information.
        
        Returns correlation ID for response tracking.
        """
        correlation_id = str(uuid.uuid4())
        
        message = ACPMessage(
            type=MessageType.QUERY,
            sender=self.agent_id,
            recipient=recipient,
            correlation_id=correlation_id,
            subject=question,
            body=context or {},
        )
        
        self.send(message)
        return correlation_id
    
    def respond(
        self,
        query: ACPMessage,
        answer: Any,
    ):
        """Respond to a query."""
        response = ACPMessage(
            type=MessageType.RESPONSE,
            sender=self.agent_id,
            recipient=query.sender,
            correlation_id=query.id,
            body={"answer": answer},
        )
        self.send(response)