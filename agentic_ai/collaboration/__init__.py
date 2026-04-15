"""
Agentic AI Collaboration Module
=================================

Multiplayer and collaboration features for agent-human teamwork.
"""

from .workspace import Workspace, WorkspaceResource, ResourceLock, ChangeRecord
from .permissions import Permission, Role, PermissionManager
from .realtime import (
    RealTimeCollaboration, OperationalTransformer, PubSubChannel,
    Operation, OperationType, CursorPosition, ActiveUser, ConnectionStatus
)

__all__ = [
    'Workspace',
    'WorkspaceResource',
    'ResourceLock',
    'ChangeRecord',
    'Permission',
    'Role',
    'PermissionManager',
    'RealTimeCollaboration',
    'OperationalTransformer',
    'PubSubChannel',
    'Operation',
    'OperationType',
    'CursorPosition',
    'ActiveUser',
    'ConnectionStatus',
]
