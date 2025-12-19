# Databricks notebook source
"""
Application Configuration
"""

from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Financial Intelligence Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-in-production"
    API_V1_PREFIX: str = "/api/v1"
    
    # Server
    PORT: int = 8001
    HOST: str = "0.0.0.0"
    
    # Database
    DATABASE_URL: str = "sqlite:///financial_intelligence.db"
    
    # API Keys (optional for now)
    QIANFAN_AK: str = ""
    QIANFAN_SK: str = ""
    ERNIE_API_KEY: str = ""
    NEWS_API_KEY: str = ""
    
    # File Upload
    UPLOAD_FOLDER: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50  # MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "png", "jpg", "jpeg", "docx"]
    
    # AI/ML
    ERNIE_MODEL_PATH: str = "./models/ernie-financial-lora"
    PADDLEOCR_MODEL_PATH: str = "./models/paddleocr-financial-qlora"
    CHROMA_DB_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # HuggingFace
    HUGGINGFACE_TOKEN: str = ""
    WANDB_API_KEY: str = ""
    
    # Performance
    WORKERS: int = 1
    MAX_CONCURRENT_REQUESTS: int = 100
    TIMEOUT: int = 300
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Scraping (existing)
    SCRAPE_INTERVAL_MINUTES: int = 60
    MAX_ARTICLES_PER_SOURCE: int = 50
    
    # Risk Scoring Weights
    SENTIMENT_WEIGHT: float = 0.4
    FREQUENCY_WEIGHT: float = 0.3
    RECENCY_WEIGHT: float = 0.2
    CREDIBILITY_WEIGHT: float = 0.1
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()