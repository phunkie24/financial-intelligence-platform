# Databricks notebook source
"""
RAG (Retrieval-Augmented Generation) Engine
Vector database with ChromaDB for document Q&A
"""

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

class FinancialRAG:
    def __init__(self, persist_directory: str = "./chroma_db"):
        """Initialize RAG system"""
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            
            # Initialize ChromaDB
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="financial_documents",
                metadata={"hnsw:space": "cosine"}
            )
            
            logger.info("✅ RAG engine initialized")
            
        except Exception as e:
            logger.error(f"❌ RAG initialization failed: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to end at sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size * 0.7:  # If period is in last 30%
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
        
        return chunks
    
    def index_document(
        self,
        document_id: int,
        text: str,
        metadata: Dict
    ) -> int:
        """
        Index a document for RAG retrieval
        Returns number of chunks indexed
        """
        try:
            # Split into chunks
            chunks = self.chunk_text(text)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(chunks, show_progress_bar=False).tolist()
            
            # Prepare IDs and metadata
            ids = [f"doc_{document_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [
                {
                    **metadata,
                    'document_id': document_id,
                    'chunk_id': i,
                    'total_chunks': len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # Add to collection
            self.collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            
            logger.info(f"📚 Indexed document {document_id}: {len(chunks)} chunks")
            return len(chunks)
            
        except Exception as e:
            logger.error(f"Indexing error: {e}")
            raise
    
    def query(
        self,
        question: str,
        document_id: Optional[int] = None,
        top_k: int = 4
    ) -> Dict:
        """
        Query RAG system
        Returns answer with context and sources
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([question], show_progress_bar=False)[0].tolist()
            
            # Build filter
            where_filter = {"document_id": document_id} if document_id else None
            
            # Search
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where_filter
            )
            
            if not results['documents'] or not results['documents'][0]:
                return {
                    'answer': "No relevant information found.",
                    'context': "",
                    'sources': []
                }
            
            # Format context
            contexts = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            context = "\n\n".join([
                f"[Source {i+1}] {ctx}"
                for i, ctx in enumerate(contexts)
            ])
            
            # Generate answer using ERNIE (import here to avoid circular dependency)
            from .ernie_client import ERNIEClient
            ernie = ERNIEClient()
            
            prompt = f"""Based on the following context from a financial document, answer the question.

Context:
{context}

Question: {question}

Provide a detailed answer with:
- Direct answer to the question
- Supporting evidence from the context
- Relevant metrics or data points

Answer:"""
            
            answer = ernie.generate(prompt, max_tokens=500)
            
            # Format sources
            sources = [
                {
                    'chunk_id': meta['chunk_id'],
                    'document_id': meta['document_id'],
                    'relevance': 1 - dist,  # Convert distance to similarity
                    'preview': ctx[:200] + '...' if len(ctx) > 200 else ctx
                }
                for meta, dist, ctx in zip(metadatas, distances, contexts)
            ]
            
            return {
                'answer': answer,
                'context': context,
                'sources': sources,
                'confidence': 1 - min(distances)  # Use best match distance
            }
            
        except Exception as e:
            logger.error(f"Query error: {e}")
            return {
                'answer': f"Error processing query: {str(e)}",
                'context': "",
                'sources': []
            }
    
    def delete_document(self, document_id: int):
        """Remove document from index"""
        try:
            # Get all chunk IDs for document
            results = self.collection.get(
                where={"document_id": document_id}
            )
            
            if results and results['ids']:
                self.collection.delete(ids=results['ids'])
                logger.info(f"🗑️ Deleted document {document_id} from index")
            
        except Exception as e:
            logger.error(f"Delete error: {e}")
    
    def get_stats(self) -> Dict:
        """Get RAG system statistics"""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection.name
            }
        except:
            return {'total_chunks': 0}