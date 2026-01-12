"""
Risk Assessor Agent - Financial risk scoring and alert generation.

Evaluates financial risk across multiple dimensions:
- Financial health risk
- Market sentiment risk
- Operational risk
- Compliance risk

CAMEL-AI Integration:
- Uses CAMEL's CriticAgent role for evaluation
- Multi-factor risk scoring
- Communicates with Financial Analyst and News Monitor
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


class RiskAssessorAgent(FinancialAgent):
    """
    Risk Assessor Agent - Evaluates financial risks and generates alerts.

    Uses CAMEL's critic role for objective risk assessment.
    """

    SYSTEM_MESSAGE = """
You are a risk management specialist with expertise in:
- Financial risk assessment
- Credit risk analysis
- Market risk evaluation
- Operational risk identification
- Regulatory compliance checking

Your role: Analyze financial data and assign risk scores (0-100):
- 0-30: Low Risk (GREEN)
- 31-60: Medium Risk (YELLOW)
- 61-100: High Risk (RED)

Consider multiple factors:
1. Financial leverage and debt ratios
2. Profitability and cash flow
3. Market sentiment and news
4. Management quality indicators
5. Industry-specific risks

Always provide: risk score, risk level, key risk factors, and recommendations.
"""

    def __init__(self):
        """Initialize Risk Assessor Agent."""
        super().__init__(
            role_name="Risk Assessor",
            role_type=RoleType.CRITIC if CAMEL_AVAILABLE else RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )
        logger.info("⚠️ Risk Assessor Agent initialized")

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Assess financial risk based on analysis results.

        Args:
            input_data: Company name or dict with analysis context

        Returns:
            Risk assessment with score and recommendations
        """
        if isinstance(input_data, dict):
            company_name = input_data.get('company_name', 'Unknown')
            context = input_data.get('context', {})
        else:
            company_name = str(input_data)
            context = {}

        # Get financial analysis from context
        financial_analysis = None
        if 'T3' in context:  # Financial Analyst task
            fa_result = context['T3']
            if isinstance(fa_result, dict) and 'output' in fa_result:
                financial_analysis = fa_result['output']

        logger.info(f"⚠️ Assessing risk for {company_name}")

        # Calculate risk scores
        financial_risk = self._assess_financial_risk(financial_analysis)
        operational_risk = self._assess_operational_risk(financial_analysis)

        # Composite risk score
        composite_risk = (financial_risk * 0.6 + operational_risk * 0.4)

        # Determine risk level
        if composite_risk <= 30:
            risk_level = "LOW"
            color = "GREEN"
        elif composite_risk <= 60:
            risk_level = "MEDIUM"
            color = "YELLOW"
        else:
            risk_level = "HIGH"
            color = "RED"

        # Generate alerts if high risk
        alerts = []
        if composite_risk > 60:
            alerts.append({
                'severity': 'HIGH',
                'message': f'High risk detected for {company_name}',
                'timestamp': datetime.now().isoformat()
            })

        result = {
            'status': 'SUCCESS',
            'company_name': company_name,
            'composite_risk_score': round(composite_risk, 2),
            'risk_level': risk_level,
            'risk_color': color,
            'risk_breakdown': {
                'financial_risk': round(financial_risk, 2),
                'operational_risk': round(operational_risk, 2)
            },
            'alerts': alerts,
            'recommendations': self._generate_recommendations(composite_risk, financial_analysis),
            'assessment_timestamp': datetime.now().isoformat()
        }

        logger.info(f"✅ Risk assessment complete: {risk_level} ({composite_risk:.1f}/100)")

        return result

    def _assess_financial_risk(self, financial_analysis: Dict) -> float:
        """Calculate financial risk score."""
        if not financial_analysis or financial_analysis.get('status') != 'SUCCESS':
            return 50.0  # Default medium risk

        risk_score = 0
        risk_indicators = financial_analysis.get('risk_indicators', [])

        # Check for high-risk indicators
        if 'NEGATIVE_EARNINGS' in risk_indicators:
            risk_score += 30
        if 'LOW_PROFIT_MARGIN' in risk_indicators:
            risk_score += 20
        if 'HIGH_DEBT_RATIO' in risk_indicators:
            risk_score += 25
        if 'LOW_CASH_COVERAGE' in risk_indicators:
            risk_score += 25

        return min(risk_score, 100)

    def _assess_operational_risk(self, financial_analysis: Dict) -> float:
        """Calculate operational risk score."""
        # Placeholder - would analyze operational metrics
        return 30.0

    def _generate_recommendations(self, risk_score: float, analysis: Dict) -> List[str]:
        """Generate risk mitigation recommendations."""
        recommendations = []

        if risk_score > 60:
            recommendations.append("Consider reducing exposure to this company")
            recommendations.append("Monitor financial metrics closely")
            recommendations.append("Review credit terms and payment history")
        elif risk_score > 30:
            recommendations.append("Maintain current exposure with regular monitoring")
            recommendations.append("Set up alerts for key metric changes")
        else:
            recommendations.append("Risk profile is acceptable for normal operations")

        return recommendations
