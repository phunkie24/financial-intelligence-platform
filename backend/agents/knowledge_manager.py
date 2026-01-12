"""
Knowledge Manager Agent - RAG-powered Q&A and document indexing.

Manages the knowledge base for the financial intelligence system:
- Document indexing with vector embeddings
- Semantic search and retrieval
- RAG-powered question answering
- Context-aware responses

CAMEL-AI Integration:
- Uses CAMEL's ChatAgent with retrieval tools
- Manages vector database (ChromaDB)
- Provides knowledge to other agents
"""

import logging
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


class KnowledgeManagerAgent(FinancialAgent):
    """
    Knowledge Manager Agent - RAG and semantic search specialist.

    Manages document indexing and retrieval for intelligent Q&A.
    """

    SYSTEM_MESSAGE = """
You are a knowledge management specialist with expertise in:
- Information retrieval and search
- Document indexing and organization
- Question answering with context
- Semantic understanding of financial documents
- Knowledge graph construction

Your role: Help users find information in financial documents by:
1. Indexing documents with semantic embeddings
2. Retrieving relevant context for questions
3. Providing accurate, cited answers
4. Maintaining knowledge base integrity

Always provide answers with source citations and confidence scores.
"""

    def __init__(self):
        """Initialize Knowledge Manager Agent."""
        super().__init__(
            role_name="Knowledge Manager",
            role_type=RoleType.ASSISTANT,
            system_message=self.SYSTEM_MESSAGE,
            model_type=ModelType.GPT_4 if CAMEL_AVAILABLE else None
        )

        self.vector_db = None
        self.embeddings_model = None
        self._init_rag_components()

        logger.info("📚 Knowledge Manager Agent initialized")

    def _init_rag_components(self):
        """Initialize RAG components (lazy loading)."""
        try:
            from ..ai.rag_engine import RAGEngine
            self.rag_engine = RAGEngine()
            logger.info("✅ RAG engine initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize RAG engine: {e}")
            self.rag_engine = None

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """
        Process document for indexing or answer question.

        Args:
            input_data: Dict with 'action' (index/query) and relevant data

        Returns:
            Indexing confirmation or answer result
        """
        if isinstance(input_data, dict):
            action = input_data.get('action', 'index')
            context = input_data.get('context', {})
        else:
            action = 'index'
            context = {}

        if action == 'index':
            return await self._index_document(context)
        elif action == 'query':
            query = input_data.get('query', input_data.get('input', ''))
            return await self._answer_question(query, context)
        else:
            return {
                'status': 'FAILED',
                'error': f'Unknown action: {action}'
            }

    async def _index_document(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Index document for semantic search.

        Args:
            context: Context with document text from Document Processor

        Returns:
            Indexing result
        """
        # Get document text from context
        doc_text = ""
        doc_id = context.get('document_id', 'unknown')

        if 'T1' in context:  # Document Processor result
            doc_result = context['T1']
            if isinstance(doc_result, dict) and 'output' in doc_result:
                doc_text = doc_result['output'].get('extracted_text', '')

        if not doc_text:
            return {
                'status': 'FAILED',
                'error': 'No document text to index'
            }

        logger.info(f"📚 Indexing document {doc_id} ({len(doc_text)} chars)")

        # Use RAG engine if available
        if self.rag_engine:
            try:
                chunks = self._split_into_chunks(doc_text)
                self.rag_engine.index_document(doc_id, chunks)

                return {
                    'status': 'SUCCESS',
                    'document_id': doc_id,
                    'chunks_indexed': len(chunks),
                    'indexed_at': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ Indexing failed: {e}")
                return {'status': 'FAILED', 'error': str(e)}

        # Fallback
        return {
            'status': 'SUCCESS',
            'document_id': doc_id,
            'message': 'Document indexed (mock mode)',
            'indexed_at': datetime.now().isoformat()
        }

    async def _answer_question(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Answer question using RAG.

        Args:
            query: User question
            context: Additional context

        Returns:
            Answer with sources
        """
        if not query:
            return {
                'status': 'FAILED',
                'error': 'No query provided'
            }

        logger.info(f"📚 Answering question: {query[:100]}")

        # Use RAG engine if available
        if self.rag_engine:
            try:
                result = self.rag_engine.query(query)
                return {
                    'status': 'SUCCESS',
                    'query': query,
                    'answer': result.get('answer', ''),
                    'sources': result.get('sources', []),
                    'confidence': result.get('confidence', 0.0),
                    'answered_at': datetime.now().isoformat()
                }
            except Exception as e:
                logger.error(f"❌ RAG query failed: {e}")

        # Fallback answer
        return {
            'status': 'SUCCESS',
            'query': query,
            'answer': 'RAG system not available. Please check configuration.',
            'sources': [],
            'confidence': 0.0,
            'answered_at': datetime.now().isoformat()
        }

    def _split_into_chunks(self, text: str, chunk_size: int = 1000) -> List[str]:
        """Split text into chunks for indexing."""
        words = text.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)

        return chunks
