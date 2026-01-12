"""
Base Agent Class - Foundation for all financial intelligence agents.

Extends CAMEL-AI's ChatAgent with domain-specific capabilities for
financial document analysis and multi-agent coordination.

Key Features:
- CAMEL ChatAgent inheritance for role-playing
- Task execution with context management
- Performance tracking and metrics
- Error handling and logging
- Agent health monitoring
"""

import logging
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    from camel.models import ModelFactory
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    # Fallback for development without CAMEL installed
    class ChatAgent:
        def __init__(self, *args, **kwargs):
            pass

    class BaseMessage:
        def __init__(self, *args, **kwargs):
            self.content = ""

    class RoleType:
        ASSISTANT = "assistant"
        USER = "user"
        CRITIC = "critic"


logger = logging.getLogger(__name__)


class FinancialAgent(ChatAgent if CAMEL_AVAILABLE else object):
    """
    Base class for all financial intelligence agents.

    Extends CAMEL's ChatAgent with:
    - Task execution framework
    - Performance monitoring
    - Error handling
    - Logging and debugging

    All specialized agents inherit from this class.
    """

    def __init__(
        self,
        role_name: str,
        role_type: RoleType,
        system_message: str,
        model_type: Optional[str] = None,
        model_config: Optional[Dict] = None,
        tools: Optional[List] = None
    ):
        """
        Initialize Financial Agent.

        Args:
            role_name: Name of the agent (e.g., "Financial Analyst")
            role_type: CAMEL RoleType (ASSISTANT, USER, CRITIC)
            system_message: System prompt defining agent behavior
            model_type: LLM model to use (e.g., "gpt-4", "ernie-4.0")
            model_config: Model configuration parameters
            tools: List of tools available to the agent
        """
        self.role_name = role_name
        self.role_type = role_type
        self.system_message = system_message
        self.tools = tools or []

        # Performance tracking
        self.task_history: List[Dict] = []
        self.performance_metrics: Dict[str, Any] = {
            'tasks_completed': 0,
            'tasks_failed': 0,
            'total_processing_time': 0.0,
            'average_response_time': 0.0,
            'success_rate': 100.0
        }

        # State management
        self.current_task: Optional[Dict] = None
        self.is_busy = False
        self.last_active = datetime.now()

        # Initialize CAMEL ChatAgent if available
        if CAMEL_AVAILABLE:
            try:
                super().__init__(
                    role_name=role_name,
                    role_type=role_type,
                    system_message=system_message,
                    model_type=model_type or ModelType.GPT_4,
                    model_config=model_config or {}
                )
                logger.info(f"✅ CAMEL-AI agent initialized: {role_name}")
            except Exception as e:
                logger.error(f"❌ Failed to initialize CAMEL agent: {e}")
                # Fallback to basic agent
        else:
            logger.warning(f"⚠️ CAMEL-AI not available. Using fallback mode for {role_name}")

    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned by the orchestrator.

        This is the main entry point for agent task execution.
        Handles logging, error handling, and performance tracking.

        Args:
            task: Task dictionary containing:
                - id: Unique task identifier
                - action: Action to perform
                - input: Input data
                - context: Context from dependent tasks
                - metadata: Additional task metadata

        Returns:
            Result dictionary:
                - task_id: Task identifier
                - status: SUCCESS or FAILED
                - output: Task output
                - metadata: Result metadata
                - processing_time: Time taken in seconds
        """
        task_id = task.get('id', 'unknown')
        start_time = datetime.now()

        self.current_task = task
        self.is_busy = True
        self.last_active = datetime.now()

        logger.info(f"🤖 {self.role_name} starting task {task_id}: {task.get('action', 'unknown')}")

        try:
            # Create CAMEL message if available
            if CAMEL_AVAILABLE:
                message = BaseMessage(
                    role_name="Orchestrator",
                    role_type=RoleType.USER,
                    content=self._format_task_input(task),
                    meta_dict=task.get('context', {})
                )

                # Execute using CAMEL step (multi-turn conversation)
                response = await self.step(message)
                output = response.content
                metadata = response.meta_dict
            else:
                # Fallback to direct processing
                output = await self.process(task['input'])
                metadata = {}

            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update performance tracking
            self._update_metrics(success=True, processing_time=processing_time)

            # Log task completion
            task_record = {
                'task_id': task_id,
                'action': task.get('action'),
                'input': task.get('input', '')[:200],  # Truncate for logging
                'output': str(output)[:200],
                'status': 'SUCCESS',
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            self.task_history.append(task_record)

            logger.info(f"✅ {self.role_name} completed task {task_id} in {processing_time:.2f}s")

            return {
                'task_id': task_id,
                'status': 'SUCCESS',
                'output': output,
                'metadata': metadata,
                'processing_time': processing_time,
                'agent': self.role_name
            }

        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()

            # Update failure metrics
            self._update_metrics(success=False, processing_time=processing_time)

            # Log error
            error_msg = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ {self.role_name} failed task {task_id}: {error_msg}")

            return {
                'task_id': task_id,
                'status': 'FAILED',
                'error': error_msg,
                'error_type': type(e).__name__,
                'metadata': {'agent': self.role_name},
                'processing_time': processing_time
            }

        finally:
            self.is_busy = False
            self.current_task = None
            self.last_active = datetime.now()

    def _format_task_input(self, task: Dict[str, Any]) -> str:
        """
        Format task input for CAMEL message.

        Converts task dictionary into natural language prompt
        suitable for LLM processing.
        """
        action = task.get('action', 'Process input')
        input_data = task.get('input', '')
        context = task.get('context', {})

        prompt = f"""
Task: {action}

Input:
{input_data}
"""

        if context:
            prompt += f"\nContext from previous tasks:\n"
            for dep_id, dep_result in context.items():
                prompt += f"- {dep_id}: {str(dep_result)[:200]}...\n"

        prompt += f"\nProvide a detailed response based on your role as {self.role_name}."

        return prompt

    def _update_metrics(self, success: bool, processing_time: float):
        """Update agent performance metrics."""
        if success:
            self.performance_metrics['tasks_completed'] += 1
        else:
            self.performance_metrics['tasks_failed'] += 1

        total_tasks = (
            self.performance_metrics['tasks_completed'] +
            self.performance_metrics['tasks_failed']
        )

        # Update success rate
        self.performance_metrics['success_rate'] = (
            (self.performance_metrics['tasks_completed'] / total_tasks * 100)
            if total_tasks > 0 else 100.0
        )

        # Update average response time
        self.performance_metrics['total_processing_time'] += processing_time
        self.performance_metrics['average_response_time'] = (
            self.performance_metrics['total_processing_time'] / total_tasks
            if total_tasks > 0 else 0.0
        )

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """
        Agent-specific processing logic.

        This method must be implemented by all subclasses.
        It defines the core functionality of the agent.

        Args:
            input_data: Input to process

        Returns:
            Processed output
        """
        raise NotImplementedError(f"{self.role_name} must implement process() method")

    def get_status(self) -> Dict[str, Any]:
        """
        Get agent health and performance status.

        Returns:
            Status dictionary with agent state and metrics
        """
        status = 'active' if self.is_busy else 'idle'

        return {
            'agent': self.role_name,
            'role_type': self.role_type if isinstance(self.role_type, str) else self.role_type.value,
            'status': status,
            'is_busy': self.is_busy,
            'current_task': self.current_task.get('id') if self.current_task else None,
            'last_active': self.last_active.isoformat(),
            'tasks_completed': self.performance_metrics['tasks_completed'],
            'tasks_failed': self.performance_metrics['tasks_failed'],
            'success_rate': round(self.performance_metrics['success_rate'], 2),
            'avg_response_time': round(self.performance_metrics['average_response_time'], 3),
            'tools': [t.__class__.__name__ if hasattr(t, '__class__') else str(t) for t in self.tools],
            'camel_enabled': CAMEL_AVAILABLE
        }

    def get_task_history(self, limit: int = 10) -> List[Dict]:
        """
        Get recent task history.

        Args:
            limit: Maximum number of tasks to return

        Returns:
            List of recent task records
        """
        return self.task_history[-limit:]

    async def send_message(self, target_agent: str, message: str, metadata: Dict = None) -> BaseMessage:
        """
        Send message to another agent (helper method).

        Args:
            target_agent: Target agent name
            message: Message content
            metadata: Additional metadata

        Returns:
            BaseMessage object
        """
        if CAMEL_AVAILABLE:
            return BaseMessage(
                role_name=self.role_name,
                role_type=self.role_type,
                content=message,
                meta_dict={
                    'from_agent': self.role_name,
                    'to_agent': target_agent,
                    'timestamp': datetime.now().isoformat(),
                    **(metadata or {})
                }
            )
        else:
            # Fallback message structure
            msg = BaseMessage()
            msg.content = message
            return msg

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.role_name}', status={'busy' if self.is_busy else 'idle'})>"
