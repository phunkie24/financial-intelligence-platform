"""
Agent API Endpoints - Multi-agent system integration with FastAPI.

Provides endpoints for:
- Document analysis via multi-agent pipeline
- Agent status monitoring
- Agent communication logs
- Task plan tracking
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from typing import Optional, Dict, Any
import logging
import os
from datetime import datetime
from pathlib import Path

from ..agents import get_agent_system


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/agents", tags=["agents"])


# Initialize agent system on module load
try:
    orchestrator, message_hub = get_agent_system()
    logger.info("✅ Agent system loaded for API")
except Exception as e:
    logger.error(f"❌ Failed to load agent system: {e}")
    orchestrator = None
    message_hub = None


@router.post("/analyze-document")
async def analyze_document_with_agents(
    file: UploadFile = File(...),
    company_name: str = Form(...),
    document_type: str = Form("earnings_report"),
    background_tasks: BackgroundTasks = None
):
    """
    Analyze document using multi-agent pipeline.

    This endpoint triggers the full CAMEL-AI multi-agent workflow:
    1. Orchestrator decomposes the task
    2. Document Processor extracts text (PaddleOCR)
    3. Financial Analyst extracts metrics (ERNIE-4.5)
    4. Risk Assessor calculates risk scores
    5. Knowledge Manager indexes document
    6. Critic validates all outputs

    Args:
        file: PDF or image document
        company_name: Company name for analysis
        document_type: Type of document (earnings_report, 10k, etc.)

    Returns:
        Multi-agent analysis results
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Agent system not available"
        )

    # Save uploaded file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = upload_dir / filename

    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"📄 Document uploaded: {filename}")

        # Create user request for orchestrator
        user_request = f"""
Analyze the financial document for {company_name}:
- File: {filename}
- Type: {document_type}

Required analysis:
1. Extract text and tables from the document
2. Extract financial metrics and calculate ratios
3. Assess financial risk and generate alerts
4. Index document for semantic search
5. Validate all outputs for quality

Provide comprehensive analysis with insights and recommendations.
"""

        # Process through multi-agent system
        context = {
            'file_path': str(file_path),
            'company_name': company_name,
            'document_type': document_type
        }

        result = await orchestrator.process(user_request, context)

        return {
            'status': 'SUCCESS',
            'document_id': filename,
            'company_name': company_name,
            'analysis': result,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Multi-agent analysis failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status")
async def get_agent_system_status():
    """
    Get status of all agents in the system.

    Returns agent health, performance metrics, and current tasks.
    """
    if orchestrator is None or message_hub is None:
        raise HTTPException(
            status_code=503,
            detail="Agent system not available"
        )

    try:
        # Get agent statuses
        agent_statuses = message_hub.get_agent_status()

        # Get message hub stats
        hub_stats = message_hub.get_hub_stats()

        return {
            'system_status': 'OPERATIONAL',
            'agents': agent_statuses,
            'message_hub': hub_stats,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to get agent status: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/communication-log")
async def get_agent_communication_log(
    agent_name: Optional[str] = None,
    limit: int = 50
):
    """
    Get agent-to-agent communication history.

    Args:
        agent_name: Filter by specific agent (optional)
        limit: Maximum messages to return

    Returns:
        Message history showing agent interactions
    """
    if message_hub is None:
        raise HTTPException(
            status_code=503,
            detail="Message hub not available"
        )

    try:
        history = message_hub.get_conversation_history(
            agent_name=agent_name,
            limit=limit
        )

        return {
            'message_count': len(history),
            'filter_agent': agent_name,
            'messages': history,
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"❌ Failed to get communication log: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/plan/{plan_id}")
async def get_task_plan_status(plan_id: str):
    """
    Get status of a specific task plan.

    Shows task decomposition, dependencies, and execution progress.

    Args:
        plan_id: Task plan identifier

    Returns:
        Task plan details with execution status
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Orchestrator not available"
        )

    try:
        plan_status = orchestrator.get_plan_status(plan_id)

        if plan_status is None:
            raise HTTPException(
                status_code=404,
                detail=f"Plan {plan_id} not found"
            )

        return plan_status

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get plan status: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/ask")
async def ask_question_rag(
    question: str = Form(...),
    document_id: Optional[str] = Form(None)
):
    """
    Ask question about documents using RAG (Knowledge Manager Agent).

    Args:
        question: User question
        document_id: Optional document ID to search

    Returns:
        Answer with sources and confidence
    """
    if orchestrator is None:
        raise HTTPException(
            status_code=503,
            detail="Agent system not available"
        )

    try:
        # Create request for Knowledge Manager
        user_request = f"Answer this question using RAG: {question}"

        context = {
            'action': 'query',
            'query': question,
            'document_id': document_id
        }

        # Direct call to Knowledge Manager through orchestrator
        from ..agents import KnowledgeManagerAgent
        km_agent = KnowledgeManagerAgent()

        result = await km_agent.process({
            'action': 'query',
            'query': question,
            'input': question,
            'context': context
        })

        return result

    except Exception as e:
        logger.error(f"❌ RAG query failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check for agent system.
    """
    system_healthy = orchestrator is not None and message_hub is not None

    return {
        'status': 'healthy' if system_healthy else 'degraded',
        'orchestrator_available': orchestrator is not None,
        'message_hub_available': message_hub is not None,
        'timestamp': datetime.now().isoformat()
    }
