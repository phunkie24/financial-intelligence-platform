"""
Financial Analyst Agent - Extract metrics and generate financial insights.

This agent is the financial intelligence expert, responsible for:
- Extracting financial metrics (revenue, profit, EPS, etc.)
- Calculating financial ratios
- Generating insights and analysis
- Identifying trends and anomalies

CAMEL-AI Integration:
- Uses CAMEL's ChatAgent with ERNIE-4.5 backend
- Multi-turn conversations for analysis refinement
- Communicates with Risk Assessor and Critic agents
"""

import logging
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from camel.agents import ChatAgent
    from camel.messages import BaseMessage
    from camel.types import RoleType, ModelType
    CAMEL_AVAILABLE = True
except ImportError:
    CAMEL_AVAILABLE = False
    RoleType = type('RoleType', (), {'ASSISTANT': 'assistant'})
    ModelType = type('ModelType', (), {'GPT_4': 'gpt-4'})

from .base_agent import FinancialAgent


logger = logging.getLogger(__name__)


class FinancialAnalystAgent(FinancialAgent):
    """
    Financial Analyst Agent - Expert in financial analysis and metric extraction.

    Powered by ERNIE-4.5 for deep financial understanding.

    Capabilities:
    - Financial metric extraction (revenue, profit, EPS, margins)
    - Ratio calculation (P/E, ROE, debt-to-equity, etc.)
    - Trend analysis and forecasting
    - Risk factor identification
    - Executive summary generation
    """

    SYSTEM_MESSAGE = """
You are a senior financial analyst with 15+ years of experience in corporate finance and investment analysis.

Your expertise includes:
- Financial statement analysis (income statement, balance sheet, cash flow)
- Financial ratio calculation and interpretation
- Year-over-year and quarter-over-quarter trend analysis
- Industry benchmarking and comparative analysis
- Risk factor identification
- Investment recommendations

When analyzing financial documents:
1. Extract ALL key financial metrics with specific numbers
2. Calculate important ratios (P/E, ROE, ROA, debt-to-equity, profit margins, etc.)
3. Identify year-over-year growth rates and trends
4. Flag any anomalies, red flags, or areas of concern
5. Provide actionable insights and recommendations

Always:
- Cite specific numbers from the document
- Show your calculations
- Provide context and industry comparisons where possible
- Be precise, quantitative, and analytical
- Format numbers clearly (e.g., $10.2B, 15.3%, 2.5x)
"""

    def __init__(self):
        """Initialize Financial Analyst Agent with ERNIE-4.5."""
        super().__init__(
            role_name="Financial Analyst",
            role_type=RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        # Initialize ERNIE client
        self.ernie_client = None
        self._init_ernie_client()

        logger.info("💰 Financial Analyst Agent initialized")

    def _init_ernie_client(self):
        """Initialize ERNIE client (lazy loading)."""
        try:
            from ..ai.ernie_client import ERNIEClient
            self.ernie_client = ERNIEClient()
            logger.info("✅ ERNIE client loaded for financial analysis")
        except Exception as e:
            logger.error(f"❌ Failed to load ERNIE client: {e}")
            self.ernie_client = None

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Analyze financial document and extract insights.

        Args:
            input_data: Document text or dict with text and context

        Returns:
            Financial analysis results with metrics, ratios, and insights
        """
        # Extract text and context
        if isinstance(input_data, dict):
            document_text = input_data.get('extracted_text', input_data.get('text', ''))
            company_name = input_data.get('company_name', 'Unknown')
            context = input_data.get('context', {})
        else:
            document_text = str(input_data)
            company_name = 'Unknown'
            context = {}

        # Get document processor results if available
        if 'T1' in context:
            doc_result = context['T1']
            if isinstance(doc_result, dict) and 'output' in doc_result:
                document_text = doc_result['output'].get('extracted_text', document_text)

        if not document_text or len(document_text) < 50:
            return {
                'status': 'FAILED',
                'error': 'Insufficient document text for analysis',
                'metrics': {},
                'ratios': {},
                'insights': ''
            }

        logger.info(f"💰 Analyzing financial document for {company_name} ({len(document_text)} chars)")

        try:
            # Step 1: Extract financial metrics
            metrics = await self._extract_metrics(document_text, company_name)

            # Step 2: Calculate financial ratios
            ratios = self._calculate_ratios(metrics)

            # Step 3: Generate insights using CAMEL/ERNIE
            insights = await self._generate_insights(document_text, metrics, ratios, company_name)

            # Step 4: Identify trends
            trends = self._identify_trends(metrics)

            # Step 5: Risk indicators
            risk_indicators = self._identify_risk_indicators(metrics, ratios)

            result = {
                'status': 'SUCCESS',
                'company_name': company_name,
                'metrics': metrics,
                'ratios': ratios,
                'insights': insights,
                'trends': trends,
                'risk_indicators': risk_indicators,
                'analysis_timestamp': datetime.now().isoformat()
            }

            logger.info(f"✅ Financial analysis complete: {len(metrics)} metrics, {len(ratios)} ratios")

            return result

        except Exception as e:
            logger.error(f"❌ Financial analysis failed: {e}")
            return {
                'status': 'FAILED',
                'error': str(e),
                'metrics': {},
                'ratios': {},
                'insights': ''
            }

    async def _extract_metrics(self, text: str, company_name: str) -> Dict[str, Any]:
        """
        Extract financial metrics from document using ERNIE.

        Args:
            text: Document text
            company_name: Company name

        Returns:
            Dictionary of extracted metrics
        """
        # Use ERNIE client if available
        if self.ernie_client and not self.ernie_client.mock_mode:
            try:
                metrics = self.ernie_client.extract_metrics(text)
                if metrics:
                    return metrics
            except Exception as e:
                logger.error(f"❌ ERNIE metric extraction failed: {e}")

        # Fallback: regex-based extraction
        metrics = self._regex_extract_metrics(text)

        return metrics

    def _regex_extract_metrics(self, text: str) -> Dict[str, Any]:
        """
        Extract metrics using regex patterns (fallback method).

        Args:
            text: Document text

        Returns:
            Extracted metrics dictionary
        """
        metrics = {}

        # Revenue patterns
        revenue_patterns = [
            r'revenue[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            r'total revenue[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            r'net sales[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?'
        ]

        for pattern in revenue_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(',', ''))
                unit = match.group(2) if len(match.groups()) > 1 else ''

                if unit and unit.upper() in ['BILLION', 'B']:
                    value *= 1e9
                elif unit and unit.upper() in ['MILLION', 'M']:
                    value *= 1e6

                metrics['revenue'] = value
                break

        # Net income patterns
        income_patterns = [
            r'net income[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            r'net profit[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            r'earnings[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?'
        ]

        for pattern in income_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1).replace(',', ''))
                unit = match.group(2) if len(match.groups()) > 1 else ''

                if unit and unit.upper() in ['BILLION', 'B']:
                    value *= 1e9
                elif unit and unit.upper() in ['MILLION', 'M']:
                    value *= 1e6

                metrics['net_income'] = value
                break

        # EPS patterns
        eps_match = re.search(r'EPS[:\s]+\$?([\d,\.]+)', text, re.IGNORECASE)
        if eps_match:
            metrics['eps'] = float(eps_match.group(1).replace(',', ''))

        # Total assets
        assets_match = re.search(
            r'total assets[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            text,
            re.IGNORECASE
        )
        if assets_match:
            value = float(assets_match.group(1).replace(',', ''))
            unit = assets_match.group(2) if len(assets_match.groups()) > 1 else ''

            if unit and unit.upper() in ['BILLION', 'B']:
                value *= 1e9
            elif unit and unit.upper() in ['MILLION', 'M']:
                value *= 1e6

            metrics['total_assets'] = value

        # Total debt
        debt_match = re.search(
            r'total debt[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            text,
            re.IGNORECASE
        )
        if debt_match:
            value = float(debt_match.group(1).replace(',', ''))
            unit = debt_match.group(2) if len(debt_match.groups()) > 1 else ''

            if unit and unit.upper() in ['BILLION', 'B']:
                value *= 1e9
            elif unit and unit.upper() in ['MILLION', 'M']:
                value *= 1e6

            metrics['total_debt'] = value

        # Cash and equivalents
        cash_match = re.search(
            r'cash and (?:cash )?equivalents[:\s]+\$?([\d,\.]+)\s*(million|billion|M|B)?',
            text,
            re.IGNORECASE
        )
        if cash_match:
            value = float(cash_match.group(1).replace(',', ''))
            unit = cash_match.group(2) if len(cash_match.groups()) > 1 else ''

            if unit and unit.upper() in ['BILLION', 'B']:
                value *= 1e9
            elif unit and unit.upper() in ['MILLION', 'M']:
                value *= 1e6

            metrics['cash'] = value

        return metrics

    def _calculate_ratios(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate financial ratios from extracted metrics.

        Args:
            metrics: Dictionary of financial metrics

        Returns:
            Dictionary of calculated ratios
        """
        ratios = {}

        # Profit margin
        if 'net_income' in metrics and 'revenue' in metrics:
            if metrics['revenue'] > 0:
                ratios['profit_margin'] = (metrics['net_income'] / metrics['revenue']) * 100

        # ROA (Return on Assets)
        if 'net_income' in metrics and 'total_assets' in metrics:
            if metrics['total_assets'] > 0:
                ratios['roa'] = (metrics['net_income'] / metrics['total_assets']) * 100

        # Debt-to-Assets
        if 'total_debt' in metrics and 'total_assets' in metrics:
            if metrics['total_assets'] > 0:
                ratios['debt_to_assets'] = (metrics['total_debt'] / metrics['total_assets']) * 100

        # Cash ratio (simplified)
        if 'cash' in metrics and 'total_debt' in metrics:
            if metrics['total_debt'] > 0:
                ratios['cash_to_debt'] = metrics['cash'] / metrics['total_debt']

        return ratios

    async def _generate_insights(
        self,
        text: str,
        metrics: Dict[str, Any],
        ratios: Dict[str, float],
        company_name: str
    ) -> str:
        """
        Generate narrative insights using ERNIE.

        Args:
            text: Document text
            metrics: Extracted metrics
            ratios: Calculated ratios
            company_name: Company name

        Returns:
            Insights text
        """
        # Use ERNIE if available
        if self.ernie_client and not self.ernie_client.mock_mode:
            try:
                prompt = f"""
Analyze the financial performance of {company_name} based on the following data:

Metrics:
{json.dumps(metrics, indent=2)}

Ratios:
{json.dumps(ratios, indent=2)}

Provide 3-5 key insights:
1. Overall financial health assessment
2. Strengths and competitive advantages
3. Areas of concern or weakness
4. Trends and trajectory
5. Recommendations for investors

Be specific, quantitative, and actionable.
"""
                insights = self.ernie_client.generate(prompt, max_tokens=800)
                if insights:
                    return insights
            except Exception as e:
                logger.error(f"❌ ERNIE insights generation failed: {e}")

        # Fallback: template-based insights
        insights_parts = []

        if 'revenue' in metrics:
            insights_parts.append(
                f"Revenue: ${metrics['revenue']:,.0f} " +
                ("indicating strong sales performance" if metrics['revenue'] > 1e9 else "")
            )

        if 'profit_margin' in ratios:
            pm = ratios['profit_margin']
            if pm > 20:
                insights_parts.append(f"Strong profit margin of {pm:.1f}%")
            elif pm < 5:
                insights_parts.append(f"Concerning low profit margin of {pm:.1f}%")

        if 'debt_to_assets' in ratios:
            dta = ratios['debt_to_assets']
            if dta > 50:
                insights_parts.append(f"High leverage with debt-to-assets ratio of {dta:.1f}%")

        if not insights_parts:
            insights_parts.append("Limited financial data available for comprehensive analysis.")

        return " | ".join(insights_parts)

    def _identify_trends(self, metrics: Dict[str, Any]) -> List[str]:
        """
        Identify financial trends from metrics.

        Args:
            metrics: Financial metrics

        Returns:
            List of trend descriptions
        """
        trends = []

        # This would require historical data - placeholder for now
        if 'revenue' in metrics:
            trends.append("Revenue data available for analysis")

        if 'net_income' in metrics:
            if metrics['net_income'] > 0:
                trends.append("Positive profitability")
            else:
                trends.append("Operating at a loss")

        return trends

    def _identify_risk_indicators(
        self,
        metrics: Dict[str, Any],
        ratios: Dict[str, float]
    ) -> List[str]:
        """
        Identify risk indicators from financial data.

        Args:
            metrics: Financial metrics
            ratios: Financial ratios

        Returns:
            List of risk indicators
        """
        risks = []

        # Profitability risks
        if 'net_income' in metrics and metrics['net_income'] < 0:
            risks.append("NEGATIVE_EARNINGS")

        if 'profit_margin' in ratios and ratios['profit_margin'] < 5:
            risks.append("LOW_PROFIT_MARGIN")

        # Leverage risks
        if 'debt_to_assets' in ratios and ratios['debt_to_assets'] > 60:
            risks.append("HIGH_DEBT_RATIO")

        # Liquidity risks
        if 'cash_to_debt' in ratios and ratios['cash_to_debt'] < 0.2:
            risks.append("LOW_CASH_COVERAGE")

        if not risks:
            risks.append("NO_MAJOR_RISKS_DETECTED")

        return risks
