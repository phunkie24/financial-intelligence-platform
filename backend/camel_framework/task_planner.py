"""
Task Planner - Task decomposition and dependency management.

Implements task planning logic for the Orchestrator agent:
- Decompose complex user requests into subtasks
- Manage task dependencies (DAG structure)
- Schedule task execution respecting dependencies
- Track task completion status

Key Classes:
- Task: Individual task with dependencies
- TaskPlan: Complete task execution plan
- TaskPlanner: Planning and parsing logic
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Task:
    """
    Individual task in a task plan.

    Attributes:
        id: Unique task identifier (e.g., "T1", "T2")
        agent: Agent responsible for this task
        action: Description of action to perform
        input: Input data for the task
        dependencies: List of task IDs that must complete first
        status: Current task status
        result: Task result (populated after completion)
        error: Error message if task failed
    """
    id: str
    agent: str
    action: str
    input: Any = ""
    dependencies: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_ready(self, completed_tasks: Set[str]) -> bool:
        """
        Check if task is ready to execute.

        Args:
            completed_tasks: Set of completed task IDs

        Returns:
            True if all dependencies are completed
        """
        return all(dep in completed_tasks for dep in self.dependencies)

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'agent': self.agent,
            'action': self.action,
            'input': self.input,
            'dependencies': self.dependencies,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'metadata': self.metadata
        }

    def __repr__(self) -> str:
        return f"Task({self.id}, agent={self.agent}, status={self.status.value})"


@dataclass
class TaskPlan:
    """
    Complete task execution plan.

    Contains all tasks and manages execution order based on dependencies.
    """
    tasks: List[Task] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_task(self, task: Task):
        """Add task to plan."""
        self.tasks.append(task)

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None

    def get_ready_tasks(self) -> List[Task]:
        """
        Get all tasks that are ready to execute.

        Returns:
            List of tasks with all dependencies completed
        """
        completed = {t.id for t in self.tasks if t.status == TaskStatus.COMPLETED}

        ready_tasks = [
            task for task in self.tasks
            if task.status == TaskStatus.PENDING and task.is_ready(completed)
        ]

        return ready_tasks

    def get_execution_order(self) -> List[List[Task]]:
        """
        Get execution order as batches (tasks in same batch can run in parallel).

        Returns:
            List of batches, where each batch contains tasks that can run in parallel
        """
        batches = []
        completed = set()
        remaining = set(t.id for t in self.tasks)

        while remaining:
            # Find tasks ready to execute
            batch = [
                task for task in self.tasks
                if task.id in remaining and task.is_ready(completed)
            ]

            if not batch:
                # Circular dependency or error
                raise ValueError(f"Circular dependency detected or no tasks ready. Remaining: {remaining}")

            batches.append(batch)

            # Mark batch as completed
            for task in batch:
                completed.add(task.id)
                remaining.remove(task.id)

        return batches

    def is_complete(self) -> bool:
        """Check if all tasks are completed."""
        return all(t.status == TaskStatus.COMPLETED for t in self.tasks)

    def has_failures(self) -> bool:
        """Check if any tasks failed."""
        return any(t.status == TaskStatus.FAILED for t in self.tasks)

    def get_statistics(self) -> Dict[str, Any]:
        """Get plan execution statistics."""
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t.status == TaskStatus.COMPLETED)
        failed = sum(1 for t in self.tasks if t.status == TaskStatus.FAILED)
        pending = sum(1 for t in self.tasks if t.status == TaskStatus.PENDING)
        running = sum(1 for t in self.tasks if t.status == TaskStatus.RUNNING)

        return {
            'total_tasks': total,
            'completed': completed,
            'failed': failed,
            'pending': pending,
            'running': running,
            'completion_rate': (completed / total * 100) if total > 0 else 0
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert plan to dictionary."""
        return {
            'tasks': [t.to_dict() for t in self.tasks],
            'metadata': self.metadata,
            'statistics': self.get_statistics()
        }

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return f"TaskPlan(tasks={stats['total_tasks']}, completed={stats['completed']})"


class TaskPlanner:
    """
    Task planning and parsing utilities.

    Helps parse LLM-generated task plans into structured TaskPlan objects.
    """

    def __init__(self):
        """Initialize task planner."""
        pass

    def parse_plan(self, llm_response: str) -> TaskPlan:
        """
        Parse LLM response into TaskPlan.

        Expected format:
            Task Plan:
            - T1: Agent Name - Action description - [dependencies]
            - T2: Agent Name - Action description - [T1]
            - T3: Agent Name - Action description - [T1, T2]

        Args:
            llm_response: Response from LLM containing task plan

        Returns:
            Parsed TaskPlan object
        """
        plan = TaskPlan()

        # Extract task lines
        lines = llm_response.strip().split('\n')

        for line in lines:
            line = line.strip()

            # Skip empty lines and headers
            if not line or 'task plan' in line.lower() or line.startswith('#'):
                continue

            # Try to parse task line
            task = self._parse_task_line(line)
            if task:
                plan.add_task(task)

        logger.info(f"📋 Parsed task plan with {len(plan.tasks)} tasks")

        return plan

    def _parse_task_line(self, line: str) -> Optional[Task]:
        """
        Parse a single task line.

        Expected formats:
        - T1: Agent Name - Action description - []
        - T2: Agent Name - Action description - [T1]
        - T1 | Agent Name | Action description | []

        Args:
            line: Task line string

        Returns:
            Task object or None if parsing fails
        """
        # Remove leading dash or bullet
        line = re.sub(r'^\s*[-*•]\s*', '', line)

        # Try format: T1: Agent - Action - [deps]
        match = re.match(
            r'(T\d+)\s*[:|\|]\s*([^-:|]+)\s*[-:|]\s*([^-:|]+)\s*[-:|]\s*\[(.*?)\]',
            line,
            re.IGNORECASE
        )

        if match:
            task_id = match.group(1).strip()
            agent = match.group(2).strip()
            action = match.group(3).strip()
            deps_str = match.group(4).strip()

            # Parse dependencies
            if deps_str:
                dependencies = [d.strip() for d in deps_str.split(',') if d.strip()]
            else:
                dependencies = []

            return Task(
                id=task_id,
                agent=agent,
                action=action,
                dependencies=dependencies
            )

        # Try simpler format: T1: Agent - Action
        match = re.match(
            r'(T\d+)\s*[:|\|]\s*([^-:|]+)\s*[-:|]\s*(.+)',
            line,
            re.IGNORECASE
        )

        if match:
            task_id = match.group(1).strip()
            agent = match.group(2).strip()
            action = match.group(3).strip()

            return Task(
                id=task_id,
                agent=agent,
                action=action,
                dependencies=[]
            )

        # Could not parse
        return None

    def create_plan_from_template(self, template_name: str, **kwargs) -> TaskPlan:
        """
        Create task plan from predefined template.

        Args:
            template_name: Template identifier
            **kwargs: Template parameters

        Returns:
            TaskPlan from template
        """
        if template_name == "document_analysis":
            return self._template_document_analysis(**kwargs)
        elif template_name == "risk_assessment":
            return self._template_risk_assessment(**kwargs)
        else:
            raise ValueError(f"Unknown template: {template_name}")

    def _template_document_analysis(
        self,
        file_path: str = None,
        company_name: str = None,
        **kwargs
    ) -> TaskPlan:
        """
        Template for document analysis workflow.

        Args:
            file_path: Path to document
            company_name: Company name

        Returns:
            TaskPlan for document analysis
        """
        plan = TaskPlan(metadata={'template': 'document_analysis'})

        plan.add_task(Task(
            id="T1",
            agent="Document Processor",
            action="Extract text and tables from document",
            input=file_path,
            dependencies=[]
        ))

        plan.add_task(Task(
            id="T2",
            agent="Knowledge Manager",
            action="Generate embeddings and index document",
            input="",
            dependencies=["T1"]
        ))

        plan.add_task(Task(
            id="T3",
            agent="Financial Analyst",
            action="Extract financial metrics and generate insights",
            input=company_name,
            dependencies=["T1"]
        ))

        plan.add_task(Task(
            id="T4",
            agent="Risk Assessor",
            action="Calculate risk scores and generate alerts",
            input=company_name,
            dependencies=["T3"]
        ))

        plan.add_task(Task(
            id="T5",
            agent="Critic",
            action="Validate all outputs and check consistency",
            input="",
            dependencies=["T3", "T4"]
        ))

        return plan

    def _template_risk_assessment(self, company_name: str = None, **kwargs) -> TaskPlan:
        """
        Template for risk assessment workflow.

        Args:
            company_name: Company to assess

        Returns:
            TaskPlan for risk assessment
        """
        plan = TaskPlan(metadata={'template': 'risk_assessment'})

        plan.add_task(Task(
            id="T1",
            agent="News Monitor",
            action="Fetch recent news articles",
            input=company_name,
            dependencies=[]
        ))

        plan.add_task(Task(
            id="T2",
            agent="Financial Analyst",
            action="Analyze financial health from documents",
            input=company_name,
            dependencies=[]
        ))

        plan.add_task(Task(
            id="T3",
            agent="Risk Assessor",
            action="Calculate composite risk score",
            input=company_name,
            dependencies=["T1", "T2"]
        ))

        return plan

    def visualize_plan(self, plan: TaskPlan) -> str:
        """
        Create ASCII visualization of task plan.

        Args:
            plan: TaskPlan to visualize

        Returns:
            ASCII art representation
        """
        lines = ["Task Execution Plan:", "=" * 60]

        batches = plan.get_execution_order()

        for i, batch in enumerate(batches):
            lines.append(f"\nBatch {i + 1} (parallel execution):")
            for task in batch:
                deps_str = ", ".join(task.dependencies) if task.dependencies else "none"
                lines.append(f"  - {task.id}: {task.agent} - {task.action}")
                lines.append(f"    Dependencies: {deps_str}")
                lines.append(f"    Status: {task.status.value}")

        lines.append("\n" + "=" * 60)

        return "\n".join(lines)
