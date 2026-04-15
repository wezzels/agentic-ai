"""
Agent Framework
===============

Base classes and utilities for building agents.
"""

from .base import BaseAgent, AgentStatus, Permission, Tool
from .developer import DeveloperAgent, create_developer_agent
from .qa import QAAgent, create_qa_agent
from .sales import SalesAgent, create_sales_agent
from .finance import FinanceAgent, create_finance_agent
from .sysadmin import SysAdminAgent, create_sysadmin_agent
from .lead import LeadAgent, create_lead_agent, Task, Workflow, TaskPriority, TaskStatus, WorkflowStatus

__all__ = [
    "BaseAgent", "AgentStatus", "Permission", "Tool",
    "DeveloperAgent", "create_developer_agent",
    "QAAgent", "create_qa_agent",
    "SalesAgent", "create_sales_agent",
    "FinanceAgent", "create_finance_agent",
    "SysAdminAgent", "create_sysadmin_agent",
    "LeadAgent", "create_lead_agent",
    "Task", "Workflow", "TaskPriority", "TaskStatus", "WorkflowStatus",
]