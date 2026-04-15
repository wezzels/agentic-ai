"""
Lead Agent - Orchestration and task routing
============================================

Coordinates multiple specialized agents, routes tasks,
and manages complex workflows.
"""

from typing import Optional, Dict, Any, List, Set
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import asyncio
import json

from .base import BaseAgent, AgentStatus, Permission, Tool
from .developer import DeveloperAgent
from .qa import QAAgent
from .sales import SalesAgent
from .finance import FinanceAgent
from .sysadmin import SysAdminAgent


class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class WorkflowStatus(str, Enum):
    """Workflow status."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class Task:
    """A task to be executed by an agent."""
    id: str
    type: str
    description: str
    agent_type: str
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    assigned_agent: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Workflow:
    """A workflow containing multiple tasks."""
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class LeadAgent(BaseAgent):
    """
    Lead agent for orchestration and task routing.
    
    Responsibilities:
    - Route tasks to appropriate specialized agents
    - Coordinate multi-agent workflows
    - Track task dependencies and execution order
    - Aggregate results from multiple agents
    - Provide unified interface for complex operations
    
    Model: gemma3:12b (reasoning-focused)
    Permission: ELEVATED (can delegate to all agents)
    """
    
    agent_type = "lead"
    
    LEAD_SYSTEM_PROMPT = """You are a lead orchestrator agent. Your responsibilities:

1. Understand complex requests and break them into tasks
2. Route tasks to appropriate specialized agents
3. Coordinate dependencies between tasks
4. Track execution status and handle failures
5. Aggregate results and provide coherent responses

Available agent types:
- developer: Code implementation, review, and testing
- qa: Quality assurance, test generation, bug finding
- sales: CRM, leads, opportunities, proposals
- finance: Financial analysis, reports, invoices
- sysadmin: System monitoring, logs, incidents

When routing tasks:
- Match task requirements to agent capabilities
- Consider task dependencies and order
- Balance workload across agents
- Monitor for failures and retry or reassign

When coordinating workflows:
- Execute tasks in correct dependency order
- Track status of all tasks
- Handle failures gracefully
- Provide progress updates

Always provide clear, actionable responses with task status."""

    def __init__(
        self,
        agent_id: Optional[str] = None,
        name: Optional[str] = None,
        project_path: Optional[str] = None,
        **kwargs
    ):
        if "permission" not in kwargs:
            kwargs["permission"] = Permission.ELEVATED
        
        super().__init__(
            agent_id=agent_id,
            name=name or "LeadAgent",
            **kwargs
        )
        
        self.project_path = Path(project_path) if project_path else None
        
        # Agent registry
        self._agents: Dict[str, BaseAgent] = {}
        self._agent_pools: Dict[str, List[str]] = {
            "developer": [],
            "qa": [],
            "sales": [],
            "finance": [],
            "sysadmin": [],
        }
        
        # Task and workflow tracking
        self._tasks: Dict[str, Task] = {}
        self._workflows: Dict[str, Workflow] = {}
        
        # Routing rules
        self._routing_rules = {
            "implement": "developer",
            "review": "developer",
            "fix_bug": "developer",
            "write_tests": "developer",
            "document": "developer",
            "generate_tests": "qa",
            "run_tests": "qa",
            "analyze_coverage": "qa",
            "find_bugs": "qa",
            "check_quality": "qa",
            "validate": "qa",
            "create_lead": "sales",
            "qualify_lead": "sales",
            "create_opportunity": "sales",
            "generate_proposal": "sales",
            "update_pipeline": "sales",
            "record_transaction": "finance",
            "create_budget": "finance",
            "analyze_spending": "finance",
            "create_invoice": "finance",
            "generate_report": "finance",
            "check_system": "sysadmin",
            "analyze_logs": "sysadmin",
            "create_incident": "sysadmin",
            "run_command": "sysadmin",
            "check_service": "sysadmin",
        }
        
        self._register_lead_tools()
    
    def _register_lead_tools(self):
        """Register lead-specific tools."""
        
        self.register_tool(Tool(
            name="create_workflow",
            description="Create a new workflow with multiple tasks",
            func=self._tool_create_workflow,
            parameters={
                "type": "object",
                "properties": {
                    "workflow_name": {"type": "string"},
                    "description": {"type": "string"},
                    "tasks": {"type": "array", "items": {"type": "object"}},
                },
                "required": ["workflow_name", "tasks"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="create_task",
            description="Create a single task",
            func=self._tool_create_task,
            parameters={
                "type": "object",
                "properties": {
                    "task_type": {"type": "string"},
                    "description": {"type": "string"},
                    "agent_type": {"type": "string"},
                    "priority": {"type": "string"},
                    "dependencies": {"type": "array", "items": {"type": "string"}},
                    "payload": {"type": "object"},
                },
                "required": ["task_type", "description"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="route_task",
            description="Route a task to the best agent",
            func=self._tool_route_task,
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                },
                "required": ["task_id"],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="execute_workflow",
            description="Execute a workflow",
            func=self._tool_execute_workflow,
            parameters={
                "type": "object",
                "properties": {
                    "workflow_id": {"type": "string"},
                },
                "required": ["workflow_id"],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="get_status",
            description="Get status of tasks and workflows",
            func=self._tool_get_status,
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "workflow_id": {"type": "string"},
                },
                "required": [],
            },
            requires_permission=Permission.STANDARD,
        ))
        
        self.register_tool(Tool(
            name="delegate_task",
            description="Delegate a task to a specific agent",
            func=self._tool_delegate_task,
            parameters={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string"},
                    "agent_id": {"type": "string"},
                },
                "required": ["task_id", "agent_id"],
            },
            requires_permission=Permission.ELEVATED,
        ))
        
        self.register_tool(Tool(
            name="analyze_request",
            description="Analyze a request and create appropriate tasks",
            func=self._tool_analyze_request,
            parameters={
                "type": "object",
                "properties": {
                    "request": {"type": "string"},
                },
                "required": ["request"],
            },
            requires_permission=Permission.STANDARD,
        ))
    
    # === Agent Management ===
    
    def register_agent(self, agent: BaseAgent) -> str:
        """Register an agent with the lead."""
        agent_type = agent.agent_type
        if agent_type not in self._agent_pools:
            self._agent_pools[agent_type] = []
        
        self._agents[agent.agent_id] = agent
        self._agent_pools[agent_type].append(agent.agent_id)
        
        self.log("agent_registered", {
            "agent_id": agent.agent_id,
            "agent_type": agent_type,
        })
        
        return agent.agent_id
    
    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get an agent by ID."""
        return self._agents.get(agent_id)
    
    def get_available_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Get an available agent of a specific type."""
        pool = self._agent_pools.get(agent_type, [])
        for agent_id in pool:
            agent = self._agents.get(agent_id)
            if agent and agent.status == AgentStatus.IDLE:
                return agent
        return None
    
    # === Tool Implementations ===
    
    async def _tool_create_workflow(
        self,
        workflow_name: str,
        tasks: List[Dict[str, Any]],
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a new workflow with tasks."""
        import uuid
        
        workflow_id = str(uuid.uuid4())[:8]
        created_tasks = []
        
        for task_def in tasks:
            task = Task(
                id=str(uuid.uuid4())[:8],
                type=task_def.get("type", "generic"),
                description=task_def.get("description", ""),
                agent_type=task_def.get("agent_type", "developer"),
                priority=TaskPriority(task_def.get("priority", "medium")),
                dependencies=task_def.get("dependencies", []),
                payload=task_def.get("payload", {}),
            )
            self._tasks[task.id] = task
            created_tasks.append(task.id)
        
        workflow = Workflow(
            id=workflow_id,
            name=workflow_name,
            description=description,
            tasks=[self._tasks[tid] for tid in created_tasks],
        )
        self._workflows[workflow_id] = workflow
        
        self.log("workflow_created", {
            "workflow_id": workflow_id,
            "name": workflow_name,
            "task_count": len(created_tasks),
        })
        
        return {
            "status": "created",
            "workflow_id": workflow_id,
            "task_ids": created_tasks,
        }
    
    async def _tool_create_task(
        self,
        task_type: str,
        description: str,
        agent_type: Optional[str] = None,
        priority: str = "medium",
        dependencies: Optional[List[str]] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a single task."""
        import uuid
        
        # Auto-route if agent_type not specified
        if not agent_type:
            agent_type = self._routing_rules.get(task_type, "developer")
        
        task = Task(
            id=str(uuid.uuid4())[:8],
            type=task_type,
            description=description,
            agent_type=agent_type,
            priority=TaskPriority(priority),
            dependencies=dependencies or [],
            payload=payload or {},
        )
        
        self._tasks[task.id] = task
        
        self.log("task_created", {
            "task_id": task.id,
            "type": task_type,
            "agent_type": agent_type,
        })
        
        return {
            "status": "created",
            "task_id": task.id,
            "task": {
                "id": task.id,
                "type": task.type,
                "agent_type": task.agent_type,
                "priority": task.priority.value,
                "status": task.status.value,
            },
        }
    
    async def _tool_route_task(self, task_id: str) -> Dict[str, Any]:
        """Route a task to the best available agent."""
        if task_id not in self._tasks:
            return {"error": f"Task not found: {task_id}"}
        
        task = self._tasks[task_id]
        
        # Find available agent
        agent = self.get_available_agent(task.agent_type)
        if not agent:
            # Create a new agent if needed
            agent = self._create_agent(task.agent_type)
            if not agent:
                return {"error": f"No agent available for type: {task.agent_type}"}
        
        # Assign task
        task.assigned_agent = agent.agent_id
        task.status = TaskStatus.ASSIGNED
        
        self.log("task_routed", {
            "task_id": task_id,
            "agent_id": agent.agent_id,
            "agent_type": task.agent_type,
        })
        
        return {
            "status": "routed",
            "task_id": task_id,
            "agent_id": agent.agent_id,
            "agent_type": task.agent_type,
        }
    
    async def _tool_execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow by running all tasks."""
        if workflow_id not in self._workflows:
            return {"error": f"Workflow not found: {workflow_id}"}
        
        workflow = self._workflows[workflow_id]
        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow().isoformat()
        
        results = []
        completed = 0
        failed = 0
        
        # Build dependency graph
        task_deps = {task.id: set(task.dependencies) for task in workflow.tasks}
        completed_tasks = set()
        
        # Execute tasks in dependency order
        while len(completed_tasks) < len(workflow.tasks):
            # Find tasks with all dependencies met
            ready = [
                task for task in workflow.tasks
                if task.id not in completed_tasks
                and task_deps[task.id].issubset(completed_tasks)
            ]
            
            if not ready:
                # Check for remaining tasks (might be blocked)
                remaining = [t for t in workflow.tasks if t.id not in completed_tasks]
                if remaining:
                    for task in remaining:
                        task.status = TaskStatus.BLOCKED
                    workflow.status = WorkflowStatus.FAILED
                    break
                break
            
            # Execute ready tasks
            for task in ready:
                # Route to agent
                route_result = await self._tool_route_task(task.id)
                if "error" in route_result:
                    task.status = TaskStatus.FAILED
                    task.error = route_result["error"]
                    failed += 1
                    completed_tasks.add(task.id)
                    continue
                
                # Execute task
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.utcnow().isoformat()
                
                try:
                    agent = self._agents.get(task.assigned_agent)
                    if agent:
                        result = await agent.perform_task(task.type, task.payload)
                        task.result = result
                        task.status = TaskStatus.COMPLETED
                        task.completed_at = datetime.utcnow().isoformat()
                        completed += 1
                    else:
                        task.status = TaskStatus.FAILED
                        task.error = "Agent not found"
                        failed += 1
                except Exception as e:
                    task.status = TaskStatus.FAILED
                    task.error = str(e)
                    failed += 1
                
                completed_tasks.add(task.id)
                results.append({
                    "task_id": task.id,
                    "status": task.status.value,
                    "result": task.result,
                    "error": task.error,
                })
        
        # Update workflow status
        if failed == 0:
            workflow.status = WorkflowStatus.COMPLETED
        elif completed > 0:
            workflow.status = WorkflowStatus.FAILED  # Partial failure
        else:
            workflow.status = WorkflowStatus.FAILED
        
        workflow.completed_at = datetime.utcnow().isoformat()
        
        self.log("workflow_completed", {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "completed": completed,
            "failed": failed,
        })
        
        return {
            "workflow_id": workflow_id,
            "status": workflow.status.value,
            "completed": completed,
            "failed": failed,
            "results": results,
        }
    
    async def _tool_get_status(
        self,
        task_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get status of tasks and workflows."""
        if workflow_id:
            if workflow_id not in self._workflows:
                return {"error": f"Workflow not found: {workflow_id}"}
            
            workflow = self._workflows[workflow_id]
            return {
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "task_count": len(workflow.tasks),
                "tasks": [
                    {
                        "id": t.id,
                        "type": t.type,
                        "status": t.status.value,
                        "assigned_agent": t.assigned_agent,
                    }
                    for t in workflow.tasks
                ],
            }
        
        if task_id:
            if task_id not in self._tasks:
                return {"error": f"Task not found: {task_id}"}
            
            task = self._tasks[task_id]
            return {
                "task_id": task_id,
                "type": task.type,
                "status": task.status.value,
                "agent_type": task.agent_type,
                "assigned_agent": task.assigned_agent,
                "result": task.result,
                "error": task.error,
            }
        
        # Return summary
        return {
            "total_tasks": len(self._tasks),
            "total_workflows": len(self._workflows),
            "tasks_by_status": {
                status.value: sum(1 for t in self._tasks.values() if t.status == status)
                for status in TaskStatus
            },
            "registered_agents": {
                agent_type: len(pool)
                for agent_type, pool in self._agent_pools.items()
            },
        }
    
    async def _tool_delegate_task(
        self,
        task_id: str,
        agent_id: str,
    ) -> Dict[str, Any]:
        """Delegate a task to a specific agent."""
        if task_id not in self._tasks:
            return {"error": f"Task not found: {task_id}"}
        
        if agent_id not in self._agents:
            return {"error": f"Agent not found: {agent_id}"}
        
        task = self._tasks[task_id]
        agent = self._agents[agent_id]
        
        task.assigned_agent = agent_id
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow().isoformat()
        
        try:
            result = await agent.perform_task(task.type, task.payload)
            task.result = result
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow().isoformat()
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {
                "status": "failed",
                "task_id": task_id,
                "error": str(e),
            }
        
        return {
            "status": "completed",
            "task_id": task_id,
            "result": task.result,
        }
    
    async def _tool_analyze_request(self, request: str) -> Dict[str, Any]:
        """Analyze a request and create appropriate tasks."""
        prompt = f"""Analyze this request and break it into tasks:

Request: {request}

For each task, identify:
1. Task type (implement, test, review, create_lead, check_system, etc.)
2. Description
3. Agent type (developer, qa, sales, finance, sysadmin)
4. Priority (low, medium, high, critical)
5. Dependencies on other tasks

Return a JSON array of tasks."""

        response = await self.think(prompt, system=self.LEAD_SYSTEM_PROMPT)
        
        # Parse response and create tasks
        tasks = []
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                task_defs = json.loads(json_match.group())
                
                for task_def in task_defs:
                    create_result = await self._tool_create_task(
                        task_type=task_def.get("type", "generic"),
                        description=task_def.get("description", ""),
                        agent_type=task_def.get("agent_type"),
                        priority=task_def.get("priority", "medium"),
                        dependencies=task_def.get("dependencies", []),
                        payload=task_def.get("payload", {}),
                    )
                    if "task_id" in create_result:
                        tasks.append(create_result["task_id"])
        except (json.JSONDecodeError, AttributeError):
            # If parsing fails, create a single task
            create_result = await self._tool_create_task(
                task_type="generic",
                description=request,
            )
            if "task_id" in create_result:
                tasks.append(create_result["task_id"])
        
        return {
            "request": request,
            "tasks_created": len(tasks),
            "task_ids": tasks,
            "analysis": response,
        }
    
    def _create_agent(self, agent_type: str) -> Optional[BaseAgent]:
        """Create a new agent of the specified type."""
        import uuid
        
        agent_id = str(uuid.uuid4())[:8]
        
        if agent_type == "developer":
            agent = DeveloperAgent(agent_id=agent_id, project_path=str(self.project_path) if self.project_path else None)
        elif agent_type == "qa":
            agent = QAAgent(agent_id=agent_id, project_path=str(self.project_path) if self.project_path else None)
        elif agent_type == "sales":
            agent = SalesAgent(agent_id=agent_id)
        elif agent_type == "finance":
            agent = FinanceAgent(agent_id=agent_id)
        elif agent_type == "sysadmin":
            agent = SysAdminAgent(agent_id=agent_id)
        else:
            return None
        
        # Copy inference and state store from lead
        agent.inference = self.inference
        agent.state_store = self.state_store
        agent.bus = self.bus
        
        self.register_agent(agent)
        return agent
    
    # === Task Handlers ===
    
    async def process_message(self, message) -> Optional[Any]:
        """Process an incoming message."""
        from ..protocol.acp import MessageType
        
        if message.type == MessageType.TASK_REQUEST:
            return await self._handle_task_request(message)
        elif message.type == MessageType.QUERY:
            return await self._handle_query(message)
        
        return None
    
    async def perform_task(self, task_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Perform a lead orchestration task."""
        if task_type == "create_workflow":
            return await self._tool_create_workflow(**payload)
        elif task_type == "create_task":
            return await self._tool_create_task(**payload)
        elif task_type == "route_task":
            return await self._tool_route_task(**payload)
        elif task_type == "execute_workflow":
            return await self._tool_execute_workflow(**payload)
        elif task_type == "get_status":
            return await self._tool_get_status(**payload)
        elif task_type == "delegate_task":
            return await self._tool_delegate_task(**payload)
        elif task_type == "analyze_request":
            return await self._tool_analyze_request(**payload)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def _handle_task_request(self, message) -> Optional[Any]:
        """Handle a task request."""
        from ..protocol.acp import MessageType
        
        task_type = message.subject
        supported = ["create_workflow", "create_task", "route_task",
                     "execute_workflow", "get_status", "delegate_task",
                     "analyze_request"]
        
        if task_type not in supported:
            self.bus.reject_task(message, f"Unsupported task: {task_type}")
            return None
        
        self.bus.accept_task(message)
        result = await self.perform_task(task_type, message.body)
        self.bus.complete_task(message, result)
        return result
    
    async def _handle_query(self, message) -> Optional[Any]:
        """Handle a query about orchestration."""
        response = await self.think(
            f"Answer this orchestration question: {message.subject}",
            system=self.LEAD_SYSTEM_PROMPT,
        )
        self.bus.respond(message, response)
        return {"answer": response}


def create_lead_agent(**kwargs) -> LeadAgent:
    """Create a lead agent."""
    return LeadAgent(**kwargs)