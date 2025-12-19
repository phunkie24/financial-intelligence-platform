# Databricks notebook source
"""
SQLAlchemy Database Models
Extended schema for document analysis
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ==================== EXISTING TABLES ====================

class NewsArticle(Base):
    """Existing news articles table"""
    __tablename__ = 'news_articles'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(500))
    content = Column(Text)
    url = Column(String(500), unique=True)
    source = Column(String(200))
    published_at = Column(DateTime)
    scraped_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    mentions = relationship("CompanyMention", back_populates="article")

class CompanyMention(Base):
    """Existing company mentions table"""
    __tablename__ = 'company_mentions'
    
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('news_articles.id'))
    company_name = Column(String(200), index=True)
    sentiment_score = Column(Float)
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    article = relationship("NewsArticle", back_populates="mentions")

class Alert(Base):
    """Existing alerts table"""
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    company_name = Column(String(200))
    alert_type = Column(String(50))
    severity = Column(String(20))
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_read = Column(Integer, default=0)

# ==================== NEW TABLES FOR DOCUMENT ANALYSIS ====================

class Document(Base):
    """Uploaded financial documents"""
    __tablename__ = 'documents'
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(50))
    file_size = Column(Integer)  # bytes
    
    # Metadata
    company_name = Column(String(200), index=True)
    document_type = Column(String(100))  # earnings, 10K, 10Q, presentation, etc.
    fiscal_period = Column(String(50))  # Q1 2024, FY 2023, etc.
    
    # Upload info
    upload_date = Column(DateTime, default=datetime.utcnow)
    uploaded_by = Column(String(200))
    
    # Processing status
    processed = Column(Boolean, default=False)
    processing_started = Column(DateTime)
    processing_completed = Column(DateTime)
    processing_error = Column(Text)
    
    # OCR results
    extracted_text = Column(Text)
    ocr_confidence = Column(Float)
    pages_count = Column(Integer)
    
    # Relationships
    analysis = relationship("DocumentAnalysis", back_populates="document", uselist=False)
    qa_history = relationship("QAHistory", back_populates="document")
    embeddings = relationship("DocumentEmbedding", back_populates="document")
    tables = relationship("ExtractedTable", back_populates="document")

class DocumentAnalysis(Base):
    """AI analysis results for documents"""
    __tablename__ = 'document_analysis'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), unique=True)
    
    # Summary
    executive_summary = Column(Text)
    key_takeaways = Column(JSON)  # List of strings
    
    # Financial metrics (JSON)
    key_metrics = Column(JSON)  # {revenue: {value, change, period}, profit: {...}, ...}
    
    # Risk analysis (JSON)
    risk_analysis = Column(JSON)  # {level, score, key_risks: [...], categories: {...}}
    
    # Sentiment
    sentiment_score = Column(Float)  # -1.0 to 1.0
    sentiment_label = Column(String(20))  # positive/negative/neutral
    sentiment_confidence = Column(Float)
    
    # AI insights (JSON)
    ai_insights = Column(JSON)  # Additional structured insights
    
    # Model info
    model_used = Column(String(100))  # ernie-4.5, ernie-financial-lora, etc.
    analysis_date = Column(DateTime, default=datetime.utcnow)
    processing_time = Column(Float)  # seconds
    
    # Relationships
    document = relationship("Document", back_populates="analysis")

class DocumentEmbedding(Base):
    """Vector embeddings for RAG"""
    __tablename__ = 'document_embeddings'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), index=True)
    
    chunk_id = Column(Integer)
    chunk_text = Column(Text)
    chunk_start = Column(Integer)  # Character position in original text
    chunk_end = Column(Integer)
    
    # Embedding stored in ChromaDB, just metadata here
    embedding_id = Column(String(200))  # ID in vector DB
    
    # Metadata
    page_number = Column(Integer)
    section_type = Column(String(100))  # header, body, table, footnote
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="embeddings")

class QAHistory(Base):
    """Q&A history for documents"""
    __tablename__ = 'qa_history'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), index=True)
    
    # Question & Answer
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    
    # Context used
    context = Column(Text)  # Retrieved chunks
    source_chunks = Column(JSON)  # List of chunk IDs used
    
    # Quality metrics
    confidence = Column(Float)
    relevance_score = Column(Float)
    
    # Feedback
    user_rating = Column(Integer)  # 1-5 stars
    user_feedback = Column(Text)
    
    # Metadata
    model_used = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    response_time = Column(Float)  # seconds
    
    # Relationships
    document = relationship("Document", back_populates="qa_history")

class ExtractedTable(Base):
    """Tables extracted from documents"""
    __tablename__ = 'extracted_tables'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey('documents.id'), index=True)
    
    page_number = Column(Integer)
    table_number = Column(Integer)  # Table N on page
    
    # Table data
    headers = Column(JSON)  # List of column headers
    data = Column(JSON)  # List of rows (each row is a list)
    rows_count = Column(Integer)
    cols_count = Column(Integer)
    
    # Extraction info
    extraction_method = Column(String(50))  # paddleocr, pdfplumber, camelot
    confidence = Column(Float)
    
    # Classification
    table_type = Column(String(100))  # income_statement, balance_sheet, cash_flow, etc.
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document", back_populates="tables")

class ModelVersion(Base):
    """Track fine-tuned model versions"""
    __tablename__ = 'model_versions'
    
    id = Column(Integer, primary_key=True)
    
    # Model info
    model_name = Column(String(200), nullable=False)
    version = Column(String(50), nullable=False)
    base_model = Column(String(200))
    
    # Fine-tuning
    fine_tuning_method = Column(String(50))  # LoRA, QLoRA, Full
    training_dataset = Column(String(500))
    training_samples = Column(Integer)
    
    # Hyperparameters (JSON)
    hyperparameters = Column(JSON)
    
    # Metrics (JSON)
    evaluation_metrics = Column(JSON)  # {accuracy, f1, loss, ...}
    
    # Storage
    model_path = Column(Text)
    huggingface_repo = Column(String(500))
    
    # Metadata
    created_by = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    training_time = Column(Float)  # hours
    
    # Status
    is_active = Column(Boolean, default=False)
    is_production = Column(Boolean, default=False)

class ComparisonSession(Base):
    """Track document comparison sessions"""
    __tablename__ = 'comparison_sessions'
    
    id = Column(Integer, primary_key=True)
    
    # Documents being compared
    document_ids = Column(JSON)  # List of document IDs
    
    # Comparison results
    comparison_summary = Column(Text)
    structured_comparison = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    session_duration = Column(Float)  # seconds