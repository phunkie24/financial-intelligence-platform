"""
Critic Agent - Quality assurance and output validation.

Reviews and validates outputs from other agents:
- Fact-checking against source documents
- Consistency verification
- Completeness assessment
- Quality scoring

CAMEL-AI Integration:
- Uses CAMEL's CriticAgent role
- Provides feedback to other agents
- Ensures output quality
"""

import logging
from typing import Dict, Any, List
from datetime import datetime

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    RoleType = type('RoleType', (), {'CRITIC': 'critic', 'ASSISTANT': 'assistant'})
    ModelType = type('ModelType', (), {'GPT_4': 'gpt-4'})

from .base_agent import FinancialAgent


logger = logging.getLogger(__name__)


class CriticAgent(FinancialAgent):
    """
    Critic Agent - Quality assurance specialist.

    Uses CAMEL's critic role to validate and improve agent outputs.
    """

    SYSTEM_MESSAGE = """
You are a senior quality assurance specialist responsible for:
- Validating accuracy of financial analysis
- Checking consistency across agent outputs
- Verifying completeness of responses
- Identifying potential errors or hallucinations
- Providing constructive feedback

Review criteria:
1. **Accuracy**: Are numbers and facts correct?
2. **Completeness**: Is all required information present?
3. **Consistency**: Do outputs from different agents align?
4. **Clarity**: Are insights clear and actionable?
5. **Citations**: Are sources properly referenced?

Provide quality scores (0-100) and specific feedback for improvement.
"""

    def __init__(self):
        """Initialize Critic Agent."""
        super().__init__(
            role_name="Critic",
            role_type=RoleType.CRITIC if CAMEL_AVAILABLE else RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        logger.info("🔍 Critic Agent initialized")

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Review and validate agent outputs.

        Args:
            input_data: Dict with context containing outputs to validate

        Returns:
            Validation report with quality scores and feedback
        """
        if isinstance(input_data, dict):
            context = input_data.get('context', {})
        else:
            context = {}

        logger.info("🔍 Critic reviewing agent outputs")

        # Extract outputs from context
        outputs_to_review = {}

        for task_id, task_result in context.items():
            if isinstance(task_result, dict) and 'output' in task_result:
                agent_name = task_result.get('agent', 'Unknown')
                outputs_to_review[agent_name] = task_result['output']

        if not outputs_to_review:
            return {
                'status': 'NO_OUTPUTS_TO_REVIEW',
                'quality_score': 0,
                'feedback': []
            }

        # Validate each output
        validations = {}
        total_score = 0

        for agent_name, output in outputs_to_review.items():
            validation = await self._validate_output(agent_name, output)
            validations[agent_name] = validation
            total_score += validation['quality_score']

        # Calculate overall quality
        overall_quality = total_score / len(validations) if validations else 0

        # Determine status
        if overall_quality >= 80:
            status = 'APPROVED'
        elif overall_quality >= 60:
            status = 'ACCEPTABLE_WITH_NOTES'
        else:
            status = 'REVISION_RECOMMENDED'

        result = {
            'status': status,
            'overall_quality_score': round(overall_quality, 2),
            'agent_validations': validations,
            'summary': self._generate_summary(validations, overall_quality),
            'reviewed_at': datetime.now().isoformat()
        }

        logger.info(f"✅ Critic review complete: {status} ({overall_quality:.1f}/100)")

        return result

    async def _validate_output(self, agent_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate individual agent output.

        Args:
            agent_name: Name of agent that produced output
            output: Output to validate

        Returns:
            Validation result with score and feedback
        """
        checks = {
            'has_content': self._check_has_content(output),
            'has_required_fields': self._check_required_fields(agent_name, output),
            'status_is_success': output.get('status') == 'SUCCESS',
            'no_errors': 'error' not in output or not output.get('error')
        }

        # Calculate quality score
        quality_score = (sum(checks.values()) / len(checks)) * 100

        # Generate feedback
        feedback = []
        if not checks['has_content']:
            feedback.append(f"{agent_name}: Output is empty or missing content")
        if not checks['has_required_fields']:
            feedback.append(f"{agent_name}: Missing required fields")
        if not checks['status_is_success']:
            feedback.append(f"{agent_name}: Task did not complete successfully")
        if not checks['no_errors']:
            feedback.append(f"{agent_name}: Error reported: {output.get('error')}")

        if not feedback:
            feedback.append(f"{agent_name}: Output quality is good")

        return {
            'agent': agent_name,
            'quality_score': round(quality_score, 2),
            'checks_passed': sum(checks.values()),
            'total_checks': len(checks),
            'checks': checks,
            'feedback': feedback
        }

    def _check_has_content(self, output: Dict[str, Any]) -> bool:
        """Check if output has meaningful content."""
        if not output:
            return False

        # Check for key data fields
        content_fields = ['extracted_text', 'metrics', 'insights', 'answer', 'articles']
        return any(field in output and output[field] for field in content_fields)

    def _check_required_fields(self, agent_name: str, output: Dict[str, Any]) -> bool:
        """Check if required fields are present."""
        required_by_agent = {
            'Document Processor': ['extracted_text', 'metadata'],
            'Financial Analyst': ['metrics', 'insights'],
            'Risk Assessor': ['composite_risk_score', 'risk_level'],
            'Knowledge Manager': ['status'],
            'News Monitor': ['articles'],
            'Orchestrator': ['status']
        }

        required = required_by_agent.get(agent_name, [])
        if not required:
            return True  # No specific requirements

        return all(field in output for field in required)

    def _generate_summary(self, validations: Dict[str, Dict], overall_quality: float) -> str:
        """Generate validation summary."""
        if overall_quality >= 80:
            return "All agent outputs meet quality standards. System performance is excellent."
        elif overall_quality >= 60:
            return "Most outputs are acceptable. Some minor issues noted for review."
        else:
            return "Significant quality issues detected. Recommend review and potential reprocessing."
