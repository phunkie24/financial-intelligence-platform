# Databricks notebook source
"""
Extended Database Manager
Handles all database operations for documents and analysis
"""

import sys
import os

# Add parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from sqlalchemy import create_engine, func, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from models.database_models import (
    Base, NewsArticle, CompanyMention, Alert,
    Document, DocumentAnalysis, DocumentEmbedding,
    QAHistory, ExtractedTable, ModelVersion, ComparisonSession
)
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import logging

logger = logging.getLogger(__name__)

# ... rest of the file stays the same ...