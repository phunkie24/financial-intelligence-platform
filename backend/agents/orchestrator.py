"""
Orchestrator Agent - Task planning and multi-agent coordination.

This agent acts as the central coordinator for the multi-agent system.
It decomposes complex user requests into subtasks, assigns them to
specialized agents, manages dependencies, and aggregates results.

Key Responsibilities:
- Analyze user requests and decompose into subtasks
- Assign tasks to specialized agents
- Monitor task execution and handle dependencies
- Aggregate results from multiple agents
- Handle errors and implement fallback strategies

CAMEL-AI Integration:
- Uses CAMEL's ChatAgent for task decomposition via LLM
- Coordinates agent-to-agent communication
- Manages task dependencies with TaskPlanner
"""

import logging
import asyncio
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    RoleType = type('RoleType', (), {'ASSISTANT': 'assistant', 'USER': 'user'})
    ModelType = type('ModelType', (), {'GPT_4': 'gpt-4'})
    BaseMessage = dict

from .base_agent import FinancialAgent
from ..camel_framework.task_planner import TaskPlanner, Task, TaskPlan, TaskStatus


logger = logging.getLogger(__name__)


class OrchestratorAgent(FinancialAgent):
    """
    Orchestrator Agent - Coordinates all other agents in the system.

    Uses CAMEL-AI's multi-agent coordination capabilities to manage
    the entire financial intelligence pipeline.
    """

    SYSTEM_MESSAGE = """
You are the Orchestrator Agent in a financial intelligence multi-agent system.

Your responsibilities:
1. Analyze user requests and decompose them into subtasks
2. Assign tasks to specialized agents with clear inputs/outputs
3. Monitor task execution and handle dependencies
4. Aggregate results from multiple agents
5. Handle errors and implement fallback strategies

Available Specialized Agents:
- Document Processor: OCR text extraction, table parsing, PDF processing
- Financial Analyst: Metric extraction, ratio analysis, insights generation
- Risk Assessor: Risk scoring, alert generation, compliance checking
- Knowledge Manager: RAG-powered Q&A, semantic search, document indexing
- News Monitor: News scraping, sentiment tracking, real-time alerts
- Critic: Output validation, quality assurance, consistency checking

When decomposing tasks, use this format:
Task Plan:
- T1: Agent Name - Action description - [dependencies]
- T2: Agent Name - Action description - [T1]
- T3: Agent Name - Action description - [T1, T2]

Always provide clear, specific task descriptions with expected inputs and outputs.
"""

    def __init__(self):
        """Initialize Orchestrator Agent."""
        super().__init__(
            role_name="Orchestrator",
            role_type=RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        self.task_planner = TaskPlanner()
        self.agent_registry: Dict[str, FinancialAgent] = {}
        self.active_plans: Dict[str, TaskPlan] = {}

        logger.info("🎯 Orchestrator Agent initialized")

    def register_agent(self, agent: FinancialAgent):
        """
        Register a specialized agent with the orchestrator.

        Args:
            agent: FinancialAgent instance to register
        """
        self.agent_registry[agent.role_name] = agent
        logger.info(f"✅ Registered agent: {agent.role_name}")

    def get_registered_agents(self) -> List[str]:
        """Get list of registered agent names."""
        return list(self.agent_registry.keys())

    async def process(self, user_request: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main orchestration logic - Process user request through multi-agent pipeline.

        Steps:
        1. Decompose user request into tasks using CAMEL conversation
        2. Execute tasks with dependency management
        3. Aggregate results from all agents

        Args:
            user_request: User's natural language request
            context: Additional context (file paths, company names, etc.)

        Returns:
            Aggregated results from all agents
        """
        plan_id = f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        context = context or {}

        logger.info(f"🎯 Orchestrator processing request: {user_request[:100]}...")

        try:
            # Step 1: Task decomposition using CAMEL
            task_plan = await self._decompose_task(user_request, context)
            self.active_plans[plan_id] = task_plan

            logger.info(f"📋 Task plan created with {len(task_plan.tasks)} tasks")

            # Step 2: Execute tasks with dependency management
            results = await self._execute_task_plan(task_plan)

            # Step 3: Aggregate results
            final_result = await self._aggregate_results(results, user_request)

            final_result['plan_id'] = plan_id
            final_result['plan_statistics'] = task_plan.get_statistics()

            return final_result

        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'plan_id': plan_id
            }

    async def _decompose_task(self, user_request: str, context: Dict[str, Any]) -> TaskPlan:
        """
        Use CAMEL conversation to decompose task into subtasks.

        Args:
            user_request: User's request
            context: Request context

        Returns:
            TaskPlan with decomposed tasks
        """
        # Check if we can use a predefined template
        if 'file_path' in context and 'document_type' in context:
            # Document analysis template
            return self.task_planner.create_plan_from_template(
                "document_analysis",
                file_path=context.get('file_path'),
                company_name=context.get('company_name', 'Unknown')
            )

        # Use CAMEL LLM for custom decomposition
        decomposition_prompt = f"""
User Request: {user_request}

Context: {json.dumps(context, indent=2)}

Decompose this request into a task plan for our multi-agent system.

Available agents and their capabilities:
- Document Processor: Extract text/tables from PDFs, OCR processing
- Financial Analyst: Extract financial metrics, calculate ratios, generate insights
- Risk Assessor: Calculate risk scores, generate alerts, identify red flags
- Knowledge Manager: Index documents, RAG-powered Q&A, semantic search
- News Monitor: Scrape news, sentiment analysis, company mentions
- Critic: Validate outputs, check consistency, quality assurance

Format (very important):
Task Plan:
- T1: Agent Name - Specific action description - []
- T2: Agent Name - Specific action description - [T1]
- T3: Agent Name - Specific action description - [T1, T2]

Provide the task plan now:
"""

        if CAMEL_AVAILABLE:
            try:
                message = BaseMessage(
                    role_name="User",
                    role_type=RoleType.USER,
                    content=decomposition_prompt
                )

                response = await self.step(message)
                task_plan = self.task_planner.parse_plan(response.content)

                if len(task_plan.tasks) == 0:
                    # Fallback to default plan
                    logger.warning("⚠️ LLM returned empty plan, using default")
                    task_plan = self._create_default_plan(user_request, context)

                return task_plan

            except Exception as e:
                logger.error(f"❌ CAMEL decomposition failed: {e}")
                return self._create_default_plan(user_request, context)
        else:
            # Fallback without CAMEL
            return self._create_default_plan(user_request, context)

    def _create_default_plan(self, user_request: str, context: Dict[str, Any]) -> TaskPlan:
        """
        Create a default task plan when LLM decomposition fails.

        Args:
            user_request: User request
            context: Context dictionary

        Returns:
            Default TaskPlan
        """
        plan = TaskPlan(metadata={'type': 'default', 'request': user_request})

        # Simple sequential plan
        plan.add_task(Task(
            id="T1",
            agent="Document Processor",
            action="Process document and extract content",
            input=context.get('file_path', ''),
            dependencies=[]
        ))

        plan.add_task(Task(
            id="T2",
            agent="Financial Analyst",
            action="Analyze financial metrics and generate insights",
            input=context.get('company_name', ''),
            dependencies=["T1"]
        ))

        plan.add_task(Task(
            id="T3",
            agent="Risk Assessor",
            action="Calculate risk scores and generate alerts",
            input=context.get('company_name', ''),
            dependencies=["T2"]
        ))

        return plan

    async def _execute_task_plan(self, plan: TaskPlan) -> Dict[str, Any]:
        """
        Execute tasks respecting dependencies.

        Uses parallel execution where possible (tasks with no mutual dependencies).

        Args:
            plan: TaskPlan to execute

        Returns:
            Dictionary mapping task IDs to results
        """
        results = {}
        completed_tasks = set()

        # Get execution batches (tasks that can run in parallel)
        try:
            batches = plan.get_execution_order()
        except ValueError as e:
            logger.error(f"❌ Invalid task plan: {e}")
            raise

        for batch_idx, batch in enumerate(batches):
            logger.info(f"📦 Executing batch {batch_idx + 1}/{len(batches)} ({len(batch)} tasks)")

            # Execute batch in parallel
            batch_tasks = [
                self._execute_single_task(task, results)
                for task in batch
            ]

            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # Process results
            for task, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"❌ Task {task.id} failed: {result}")
                    task.status = TaskStatus.FAILED
                    task.error = str(result)
                    results[task.id] = {
                        'status': 'FAILED',
                        'error': str(result)
                    }
                else:
                    task.status = TaskStatus.COMPLETED
                    task.result = result
                    results[task.id] = result
                    completed_tasks.add(task.id)

        return results

    async def _execute_single_task(self, task: Task, context: Dict) -> Any:
        """
        Delegate task to appropriate agent.

        Args:
            task: Task to execute
            context: Results from previous tasks

        Returns:
            Task result
        """
        agent = self.agent_registry.get(task.agent)

        if not agent:
            logger.warning(f"⚠️ Agent '{task.agent}' not found, skipping task {task.id}")
            return {
                'status': 'SKIPPED',
                'reason': f'Agent {task.agent} not registered',
                'task_id': task.id
            }

        # Mark task as running
        task.status = TaskStatus.RUNNING

        # Prepare task input with context from dependencies
        task_input = {
            'id': task.id,
            'action': task.action,
            'input': task.input,
            'context': {dep: context.get(dep, {}) for dep in task.dependencies}
        }

        logger.info(f"🤖 Delegating task {task.id} to {task.agent}")

        # Execute via agent
        result = await agent.execute_task(task_input)

        return result

    async def _aggregate_results(self, results: Dict[str, Any], user_request: str) -> Dict[str, Any]:
        """
        Combine results from all agents into final output.

        Args:
            results: Dictionary of task results
            user_request: Original user request

        Returns:
            Aggregated results
        """
        # Extract successful results
        successful_results = {
            task_id: result
            for task_id, result in results.items()
            if result.get('status') == 'SUCCESS'
        }

        # Count failures
        failed_count = sum(1 for r in results.values() if r.get('status') == 'FAILED')

        # Simple aggregation
        aggregated = {
            'status': 'SUCCESS' if len(successful_results) > 0 else 'FAILED',
            'user_request': user_request,
            'total_tasks': len(results),
            'successful_tasks': len(successful_results),
            'failed_tasks': failed_count,
            'results': successful_results,
            'timestamp': datetime.now().isoformat()
        }

        # If CAMEL is available, use LLM to create a summary
        if CAMEL_AVAILABLE and len(successful_results) > 0:
            try:
                summary = await self._generate_summary(successful_results, user_request)
                aggregated['summary'] = summary
            except Exception as e:
                logger.error(f"❌ Failed to generate summary: {e}")
                aggregated['summary'] = "Results aggregated successfully."

        return aggregated

    async def _generate_summary(self, results: Dict[str, Any], user_request: str) -> str:
        """
        Generate human-readable summary using CAMEL.

        Args:
            results: Task results
            user_request: Original request

        Returns:
            Summary text
        """
        summary_prompt = f"""
Original Request: {user_request}

Task Results:
{json.dumps(results, indent=2, default=str)[:3000]}

Provide a concise executive summary (3-5 sentences) combining the key insights from all agents.
Focus on:
- What was accomplished
- Key findings and metrics
- Any risks or concerns identified
- Actionable recommendations

Summary:
"""

        message = BaseMessage(
            role_name="System",
            role_type=RoleType.USER,
            content=summary_prompt
        )

        response = await self.step(message)
        return response.content if hasattr(response, 'content') else str(response)

    def get_plan_status(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of an active task plan.

        Args:
            plan_id: Plan identifier

        Returns:
            Plan status dictionary or None
        """
        plan = self.active_plans.get(plan_id)
        if not plan:
            return None

        return plan.to_dict()

    async def process_with_template(
        self,
        template_name: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process using predefined template.

        Args:
            template_name: Template identifier
            **kwargs: Template parameters

        Returns:
            Processing results
        """
        # Create plan from template
        task_plan = self.task_planner.create_plan_from_template(
            template_name,
            **kwargs
        )

        plan_id = f"plan_{template_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.active_plans[plan_id] = task_plan

        # Execute plan
        results = await self._execute_task_plan(task_plan)

        # Aggregate results
        final_result = await self._aggregate_results(
            results,
            f"Template: {template_name}"
        )

        final_result['plan_id'] = plan_id
        final_result['template'] = template_name

        return final_result
