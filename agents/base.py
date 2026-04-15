"""
Base Agent - Foundation class for all agents
=============================================

Provides common functionality for all agent types:
- Identity and permissions
- State management
- Tool registration
- Memory access
- Transparency and logging
"""

import uuid
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List, Callable, Set
from datetime import datetime
import json

from ..infrastructure.state import StateStore
from ..infrastructure.inference import InferenceServer, get_inference_server
from ..protocol.acp import ACPBus, ACPMessage, MessageType, Priority


class AgentStatus(str, Enum):
    """Agent operational status."""
    INITIALIZING = "initializing"
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"
    OFFLINE = "offline"


class Permission(str, Enum):
    """Agent permission levels."""
    READ_ONLY = "read_only"         # Can only read, no writes
    STANDARD = "standard"           # Can read and write to assigned projects
    ELEVATED = "elevated"           # Can create projects, manage resources
    ADMIN = "admin"                 # Full access, can manage other agents


@dataclass
class Tool:
    """A tool that an agent can use."""
    name: str
    description: str
    func: Callable
    parameters: Dict[str, Any] = field(default_factory=dict)
    requires_permission: Permission = Permission.STANDARD
    
    def to_schema(self) -> Dict[str, Any]:
        """Return OpenAI-style tool schema."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            }
        }


@dataclass
class AgentMemory:
    """Short-term memory for an agent."""
    entries: List[Dict[str, Any]] = field(default_factory=list)
    max_entries: int = 100
    
    def add(self, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a memory entry."""
        entry = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self.entries.append(entry)
        
        # Trim to max
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """Get the n most recent entries."""
        return self.entries[-n:]
    
    def to_messages(self) -> List[Dict[str, str]]:
        """Convert to chat message format."""
        return [
            {"role": e["role"], "content": e["content"]}
            for e in self.entries
        ]
    
    def clear(self):
        """Clear all memory."""
        self.entries = []


class BaseAgent(ABC):
    """
    Base class for all agents.
    
    Provides:
    - Identity and permissions
    - State persistence (StateStore)
    - LLM inference (InferenceServer)
    - Message bus (ACPBus)
    - Tool management
    - Memory
    - Transparency logging
    """
    
    # Class-level agent type identifier
    agent_type: str = "base"
    
    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        permission: Permission = Permission.STANDARD,
        state_store: Optional[StateStore] = None,
        inference_server: Optional[InferenceServer] = None,
        message_bus: Optional[ACPBus] = None,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        ollama_host: str = "10.0.0.117",
        ollama_port: int = 11434,
    ):
        # Identity
        self.agent_id = agent_id or str(uuid.uuid4())
        self.name = name or f"{self.agent_type}_{self.agent_id[:8]}"
        self.permission = permission
        self.status = AgentStatus.INITIALIZING
        
        # Infrastructure
        self.state_store = state_store or StateStore(
            redis_host=redis_host,
            redis_port=redis_port,
        )
        self.inference = inference_server or get_inference_server(
            host=ollama_host,
            port=ollama_port,
        )
        self.bus = message_bus or ACPBus(
            redis_host=redis_host,
            redis_port=redis_port,
            agent_id=self.agent_id,
        )
        
        # Tools
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()
        
        # Memory
        self.memory = AgentMemory()
        
        # Transparency log
        self._transparency_log: List[Dict[str, Any]] = []
        
        # Load persisted state
        self._load_state()
        
        self.status = AgentStatus.IDLE
    
    # === Abstract Methods ===
    
    @abstractmethod
    async def process_message(self, message: ACPMessage) -> Optional[ACPMessage]:
        """
        Process an incoming message.
        
        Args:
            message: The incoming ACP message
        
        Returns:
            Optional response message
        """
        pass
    
    @abstractmethod
    async def perform_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform a specific task.
        
        Args:
            task_type: Type of task to perform
            payload: Task parameters
        
        Returns:
            Task result
        """
        pass
    
    # === State Management ===
    
    def _load_state(self):
        """Load state from persistent storage."""
        state = self.state_store.get_agent_state(self.agent_id)
        if state:
            self.name = state.get("name", self.name)
            self.permission = Permission(state.get("permission", self.permission.value))
            if "memory" in state:
                self.memory.entries = state["memory"]
            self.log("state_loaded", {"entries": len(self.memory.entries)})
    
    def save_state(self):
        """Save current state to persistent storage."""
        state = {
            "name": self.name,
            "permission": self.permission.value,
            "status": self.status.value,
            "memory": self.memory.entries[-50:],  # Save last 50
        }
        self.state_store.save_agent_state(
            self.agent_id,
            self.agent_type,
            state
        )
        self.log("state_saved")
    
    # === Tool Management ===
    
    def _register_default_tools(self):
        """Register default tools available to all agents."""
        self.register_tool(Tool(
            name="get_status",
            description="Get the current status of this agent",
            func=self._tool_get_status,
            requires_permission=Permission.READ_ONLY,
        ))
        
        self.register_tool(Tool(
            name="clear_memory",
            description="Clear the agent's short-term memory",
            func=self._tool_clear_memory,
            requires_permission=Permission.ELEVATED,
        ))
    
    def register_tool(self, tool: Tool):
        """Register a tool for this agent."""
        self._tools[tool.name] = tool
    
    def get_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get OpenAI-style tool schemas."""
        return [t.to_schema() for t in self._tools.values()]
    
    async def call_tool(self, name: str, **kwargs) -> Any:
        """Call a registered tool."""
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        
        tool = self._tools[name]
        
        # Check permission
        if not self._has_permission(tool.requires_permission):
            raise PermissionError(
                f"Agent lacks permission for tool: {name}"
            )
        
        self.log("tool_call", {"tool": name, "args": kwargs})
        
        try:
            result = await tool.func(**kwargs)
            self.log("tool_result", {"tool": name, "result": str(result)[:100]})
            return result
        except Exception as e:
            self.log("tool_error", {"tool": name, "error": str(e)})
            raise
    
    # === Permission Checks ===
    
    def _has_permission(self, required: Permission) -> bool:
        """Check if agent has required permission level."""
        levels = {
            Permission.READ_ONLY: 0,
            Permission.STANDARD: 1,
            Permission.ELEVATED: 2,
            Permission.ADMIN: 3,
        }
        return levels[self.permission] >= levels[required]
    
    def can_read(self, project_id: str) -> bool:
        """Check if agent can read from a project."""
        return self._has_permission(Permission.READ_ONLY)
    
    def can_write(self, project_id: str) -> bool:
        """Check if agent can write to a project."""
        return self._has_permission(Permission.STANDARD)
    
    def can_create_project(self) -> bool:
        """Check if agent can create new projects."""
        return self._has_permission(Permission.ELEVATED)
    
    def can_manage_agents(self) -> bool:
        """Check if agent can manage other agents."""
        return self._has_permission(Permission.ADMIN)
    
    # === Inference ===
    
    async def think(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False,
    ) -> str:
        """
        Use LLM inference to think about something.
        
        Args:
            prompt: The prompt to process
            system: System prompt (optional)
            temperature: Sampling temperature
            stream: Whether to stream response
        
        Returns:
            Generated response
        """
        self.log("think_start", {"prompt_length": len(prompt)})
        
        response = self.inference.generate(
            prompt=prompt,
            system=system,
            agent_type=self.agent_type,
            temperature=temperature,
            stream=stream,
        )
        
        self.log("think_complete", {"response_length": len(response)})
        return response
    
    async def chat(
        self,
        message: str,
        system: Optional[str] = None,
    ) -> str:
        """
        Chat with the LLM using conversation history.
        
        Args:
            message: New user message
            system: System prompt (optional)
        
        Returns:
            Assistant response
        """
        # Add to memory
        self.memory.add("user", message)
        
        # Build messages
        messages = self.memory.to_messages()
        if system:
            messages.insert(0, {"role": "system", "content": system})
        
        # Get response
        response = self.inference.chat(
            messages=messages,
            agent_type=self.agent_type,
        )
        
        # Add to memory
        self.memory.add("assistant", response)
        
        return response
    
    # === Message Handling ===
    
    async def start(self):
        """Start the agent (connect to message bus)."""
        self.bus.connect()
        self.bus.subscribe_agent(self._handle_message)
        self.status = AgentStatus.IDLE
        self.bus.publish_status("online", {"agent_type": self.agent_type})
        self.log("started")
    
    async def stop(self):
        """Stop the agent."""
        self.status = AgentStatus.OFFLINE
        self.bus.publish_status("offline")
        self.save_state()
        self.bus.disconnect()
        self.log("stopped")
    
    async def _handle_message(self, message: ACPMessage):
        """Internal message handler."""
        self.log("message_received", {
            "from": message.sender,
            "type": message.type.value,
            "subject": message.subject,
        })
        
        try:
            self.status = AgentStatus.WORKING
            response = await self.process_message(message)
            self.status = AgentStatus.IDLE
            
            if response:
                self.bus.send(response)
        except Exception as e:
            self.status = AgentStatus.ERROR
            self.log("error", {"error": str(e)})
            
            # Send error response if applicable
            if message.type in [MessageType.TASK_REQUEST, MessageType.QUERY]:
                self.bus.fail_task(message, str(e))
            
            self.status = AgentStatus.IDLE
    
    # === Transparency ===
    
    def log(self, event: str, data: Optional[Dict[str, Any]] = None):
        """
        Log an event for transparency.
        
        All agent actions are logged for auditability.
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "event": event,
            "data": data or {},
        }
        self._transparency_log.append(entry)
    
    def get_transparency_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent transparency log entries."""
        return self._transparency_log[-limit:]
    
    def export_transparency_log(self) -> str:
        """Export full transparency log as JSON."""
        return json.dumps(self._transparency_log, indent=2)
    
    # === Default Tools ===
    
    async def _tool_get_status(self) -> Dict[str, Any]:
        """Tool: Get agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type,
            "status": self.status.value,
            "permission": self.permission.value,
            "memory_entries": len(self.memory.entries),
            "tools_registered": len(self._tools),
        }
    
    async def _tool_clear_memory(self) -> Dict[str, Any]:
        """Tool: Clear agent memory."""
        count = len(self.memory.entries)
        self.memory.clear()
        return {"cleared_entries": count}
    
    # === String Representation ===
    
    def __repr__(self) -> str:
        return f"<{self.agent_type} {self.name} ({self.agent_id[:8]}) status={self.status.value}>"
    
    def __str__(self) -> str:
        return f"{self.name} ({self.agent_type})"