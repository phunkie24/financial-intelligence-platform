"""
CAMEL-AI Framework Integration Layer

This module provides the core infrastructure for multi-agent coordination:
- Message routing and communication
- Task planning and decomposition
- Agent society management
- Tool wrappers for CAMEL compatibility

Components:
- message_hub: Central message routing for agent communication
- task_planner: Task decomposition and dependency management
- society_manager: Multi-agent coordination and orchestration
- role_definitions: Agent role configurations
- tools/: CAMEL-compatible tool wrappers
"""

from .message_hub import AgentMessageHub
from .task_planner import TaskPlanner, Task, TaskPlan
from .role_definitions import AgentRoles, get_system_message

__all__ = [
    'AgentMessageHub',
    'TaskPlanner',
    'Task',
    'TaskPlan',
    'AgentRoles',
    'get_system_message',
]
