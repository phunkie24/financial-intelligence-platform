"""
CAMEL-AI Multi-Agent System for Financial Intelligence

This module contains all specialized agents that collaborate to provide
intelligent financial document analysis, risk assessment, and monitoring.

Architecture:
- 7 specialized agents using CAMEL-AI framework
- Role-based agent design with clear responsibilities
- Agent-to-agent communication via message passing
- Task decomposition and coordination by Orchestrator

Agents:
- OrchestratorAgent: Task planning and coordination
- DocumentProcessorAgent: OCR and document extraction
- FinancialAnalystAgent: Metric extraction and insights (ERNIE-4.5)
- RiskAssessorAgent: Risk scoring and alert generation
- KnowledgeManagerAgent: RAG and semantic search
- NewsMonitorAgent: Real-time news surveillance
- QualityCriticAgent: Output validation and QA
"""

from .base_agent import FinancialAgent
from .orchestrator import OrchestratorAgent
from .document_processor import DocumentProcessorAgent
from .financial_analyst import FinancialAnalystAgent
from .risk_assessor import RiskAssessorAgent
from .knowledge_manager import KnowledgeManagerAgent
from .news_monitor import NewsMonitorAgent
from .critic import CriticAgent

__all__ = [
    'FinancialAgent',
    'OrchestratorAgent',
    'DocumentProcessorAgent',
    'FinancialAnalystAgent',
    'RiskAssessorAgent',
    'KnowledgeManagerAgent',
    'NewsMonitorAgent',
    'CriticAgent',
    'init_agent_system',
    'get_agent_system'
]

__version__ = '1.0.0'
__author__ = 'Financial Intelligence Platform Team'
__description__ = 'CAMEL-AI Multi-Agent System for Financial Analysis'


# Global agent system instance
_agent_system = None


def init_agent_system():
    """
    Initialize the complete multi-agent system.

    Creates and registers all 7 specialized agents with the orchestrator
    and message hub.

    Returns:
        tuple: (orchestrator, message_hub) - Main system components
    """
    global _agent_system

    if _agent_system is not None:
        return _agent_system

    import logging
    logger = logging.getLogger(__name__)

    logger.info("🚀 Initializing CAMEL-AI Multi-Agent System")

    # Import message hub
    from ..camel_framework.message_hub import AgentMessageHub

    # Create message hub
    message_hub = AgentMessageHub()

    # Create orchestrator
    orchestrator = OrchestratorAgent()

    # Create specialized agents
    doc_processor = DocumentProcessorAgent()
    financial_analyst = FinancialAnalystAgent()
    risk_assessor = RiskAssessorAgent()
    knowledge_manager = KnowledgeManagerAgent()
    news_monitor = NewsMonitorAgent()
    critic = CriticAgent()

    # Register agents with orchestrator
    orchestrator.register_agent(doc_processor)
    orchestrator.register_agent(financial_analyst)
    orchestrator.register_agent(risk_assessor)
    orchestrator.register_agent(knowledge_manager)
    orchestrator.register_agent(news_monitor)
    orchestrator.register_agent(critic)

    # Register agents with message hub
    message_hub.register_agent("Orchestrator", orchestrator)
    message_hub.register_agent("Document Processor", doc_processor)
    message_hub.register_agent("Financial Analyst", financial_analyst)
    message_hub.register_agent("Risk Assessor", risk_assessor)
    message_hub.register_agent("Knowledge Manager", knowledge_manager)
    message_hub.register_agent("News Monitor", news_monitor)
    message_hub.register_agent("Critic", critic)

    logger.info("✅ Multi-Agent System initialized successfully")
    logger.info(f"📊 Registered agents: {len(orchestrator.get_registered_agents())}")

    # Store globally
    _agent_system = (orchestrator, message_hub)

    return orchestrator, message_hub


def get_agent_system():
    """
    Get existing agent system or create new one.

    Returns:
        tuple: (orchestrator, message_hub)
    """
    global _agent_system

    if _agent_system is None:
        return init_agent_system()

    return _agent_system


def reset_agent_system():
    """Reset the global agent system (useful for testing)."""
    global _agent_system
    _agent_system = None
