"""
News Monitor Agent - Real-time news surveillance and sentiment tracking.

Autonomous agent that continuously monitors:
- Financial news for tracked companies
- Sentiment analysis
- Company mentions and alerts
- Market-moving events

CAMEL-AI Integration:
- Autonomous TaskAgent for background monitoring
- Publishes alerts to other agents
- Real-time sentiment tracking
"""

import logging
from typing import Dict, Any, List
from datetime import datetime
import asyncio

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


class NewsMonitorAgent(FinancialAgent):
    """
    News Monitor Agent - Autonomous news surveillance.

    Runs as background task, monitoring news and alerting on significant events.
    """

    SYSTEM_MESSAGE = """
You are a financial news monitoring specialist with expertise in:
- Real-time news aggregation
- Sentiment analysis
- Company mention detection
- Event impact assessment
- Alert prioritization

Your role: Monitor news sources and identify:
1. Negative sentiment spikes
2. Major corporate events (earnings, M&A, leadership changes)
3. Regulatory actions or legal issues
4. Market-moving announcements

Classify alerts as: CRITICAL, HIGH, MEDIUM, LOW
"""

    def __init__(self):
        """Initialize News Monitor Agent."""
        super().__init__(
            role_name="News Monitor",
            role_type=RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        self.monitoring = False
        self.monitor_task = None

        logger.info("📰 News Monitor Agent initialized")

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Process news monitoring request.

        Args:
            input_data: Company name or monitoring config

        Returns:
            Latest news and sentiment data
        """
        if isinstance(input_data, dict):
            company_name = input_data.get('company_name', input_data.get('input', 'Unknown'))
            action = input_data.get('action', 'fetch')
        else:
            company_name = str(input_data)
            action = 'fetch'

        logger.info(f"📰 Processing news for {company_name}")

        if action == 'start_monitoring':
            return await self.start_monitoring(company_name)
        elif action == 'stop_monitoring':
            return await self.stop_monitoring()
        else:
            return await self._fetch_news(company_name)

    async def _fetch_news(self, company_name: str) -> Dict[str, Any]:
        """
        Fetch recent news for company.

        Args:
            company_name: Company to monitor

        Returns:
            News articles with sentiment
        """
        # Mock news data (in production, would call NewsAPI or scrape sources)
        articles = [
            {
                'title': f'{company_name} reports strong quarterly earnings',
                'sentiment': 'positive',
                'sentiment_score': 0.75,
                'source': 'Financial Times',
                'published_at': datetime.now().isoformat()
            },
            {
                'title': f'Analysts raise price target for {company_name}',
                'sentiment': 'positive',
                'sentiment_score': 0.65,
                'source': 'Bloomberg',
                'published_at': datetime.now().isoformat()
            }
        ]

        # Calculate overall sentiment
        avg_sentiment = sum(a['sentiment_score'] for a in articles) / len(articles) if articles else 0

        return {
            'status': 'SUCCESS',
            'company_name': company_name,
            'articles': articles,
            'article_count': len(articles),
            'average_sentiment': avg_sentiment,
            'sentiment_label': self._classify_sentiment(avg_sentiment),
            'fetched_at': datetime.now().isoformat()
        }

    def _classify_sentiment(self, score: float) -> str:
        """Classify sentiment score."""
        if score > 0.6:
            return 'POSITIVE'
        elif score < 0.4:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

    async def start_monitoring(self, company_name: str) -> Dict[str, Any]:
        """Start autonomous monitoring."""
        if self.monitoring:
            return {'status': 'ALREADY_RUNNING', 'company': company_name}

        self.monitoring = True
        logger.info(f"📰 Starting autonomous monitoring for {company_name}")

        return {
            'status': 'SUCCESS',
            'message': f'Monitoring started for {company_name}',
            'started_at': datetime.now().isoformat()
        }

    async def stop_monitoring(self) -> Dict[str, Any]:
        """Stop autonomous monitoring."""
        self.monitoring = False
        logger.info("📰 Stopping autonomous monitoring")

        return {
            'status': 'SUCCESS',
            'message': 'Monitoring stopped',
            'stopped_at': datetime.now().isoformat()
        }
