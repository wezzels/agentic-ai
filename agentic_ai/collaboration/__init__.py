"""
Agentic AI Collaboration Module
=================================

Multiplayer and collaboration features for agent-human teamwork.
"""

from .workspace import Workspace, WorkspaceResource, ResourceLock, ChangeRecord
from .permissions import Permission, Role, PermissionManager

__all__ = [
    'Workspace',
    'WorkspaceResource',
    'ResourceLock',
    'ChangeRecord',
    'Permission',
    'Role',
    'PermissionManager',
]
