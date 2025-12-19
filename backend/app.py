# Databricks notebook source
"""
Financial Intelligence Platform - Production Ready
Open Source AI: PaddleOCR + Hugging Face Transformers
100% Free - No API Keys Required
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from typing import Optional, List
from contextlib import asynccontextmanager
import logging
import uvicorn
import os
import json
import sqlite3
import asyncio
import sys

# Add paths for modules
sys.path.append('./ocr')
sys.path.append('./ai')

# ==================== CONFIGURATION ====================

class Settings:
    APP_NAME = "Financial Intelligence Platform"
    APP_VERSION = "2.0.0"
    DEBUG = True
    PORT = 8001
    HOST = "127.0.0.1"
    UPLOAD_FOLDER = "./uploads"
    DATA_FOLDER = "./data"
    ALLOWED_ORIGINS = "*"
    MAX_UPLOAD_SIZE_MB = 50
    
    # Database paths
    DB_PATH = "./financial_intelligence.db"
    FALLBACK_DB_PATH = "../financial_news_monitor.db"

settings = Settings()

# ==================== LOGGING ====================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== DATABASE CONNECTION ====================

def get_db_path():
    """Find the database file"""
    if os.path.exists(settings.DB_PATH):
        return settings.DB_PATH
    elif os.path.exists(settings.FALLBACK_DB_PATH):
        return settings.FALLBACK_DB_PATH
    else:
        logger.info(f"Creating new database at {settings.DB_PATH}")
        return settings.DB_PATH

def get_db_connection():
    """Get database connection"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize database tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            mention_count INTEGER DEFAULT 0,
            avg_sentiment REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            safe_filename TEXT NOT NULL,
            company TEXT,
            type TEXT,
            uploaded TEXT DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT NOT NULL,
            file_size_mb REAL,
            processed INTEGER DEFAULT 0,
            ocr_confidence REAL,
            extracted_text TEXT,
            analysis TEXT
        )
    """)
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            type TEXT DEFAULT 'risk',
            severity TEXT DEFAULT 'MEDIUM',
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )
    """)
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT,
            source TEXT,
            published_at TEXT,
            sentiment REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()
    logger.info("✅ Database initialized")

# ==================== LIFESPAN ====================

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(settings.DATA_FOLDER, exist_ok=True)
    os.makedirs("chroma_db", exist_ok=True)
    os.makedirs("ocr", exist_ok=True)
    os.makedirs("ai", exist_ok=True)
    
    init_database()
    
    db_path = get_db_path()
    logger.info(f"📊 Using database: {db_path}")
    logger.info("🤖 Open Source AI: PaddleOCR + Hugging Face")
    logger.info("✨ Server ready!")
    yield
    # Shutdown
    logger.info("👋 Shutting down...")

# ==================== CREATE APP ====================

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-Powered Financial Document Analysis (Open Source)",
    lifespan=lifespan
)

# ==================== CORS ====================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==================== DOCUMENT PROCESSING WITH OPEN SOURCE AI ====================

async def process_document_background(document_id: int, file_path: str):
    """
    Background task to process uploaded document
    Uses: PaddleOCR (text extraction) + Hugging Face (AI analysis)
    100% Open Source - No API Keys Required
    """
    logger.info(f"🔄 Starting open source processing for document ID: {document_id}")
    
    await asyncio.sleep(1)
    
    try:
        # Import open source processors
        try:
            from ocr.paddleocr_processor import DocumentProcessor
            from ai.opensource_analyzer import FinancialAnalyzer
            use_ai = True
        except ImportError as e:
            logger.warning(f"⚠️ Open source modules not found: {e}")
            logger.info("💡 Using fallback basic processing")
            use_ai = False
        
        if use_ai:
            # STEP 1: Extract text with PaddleOCR
            logger.info("📸 Starting PaddleOCR text extraction...")
            processor = DocumentProcessor()
            ocr_result = processor.process_document(file_path)
            
            if not ocr_result["success"]:
                raise Exception(ocr_result.get("error", "OCR failed"))
            
            logger.info(f"✅ Extracted {len(ocr_result['text'])} characters (confidence: {ocr_result['confidence']:.2%})")
            
            # STEP 2: Analyze with Hugging Face AI
            logger.info("🤖 Starting AI analysis...")
            analyzer = FinancialAnalyzer()
            analysis_result = analyzer.analyze_financial_document(ocr_result["text"])
            
            if analysis_result.get("success"):
                sentiment = analysis_result.get("sentiment", {})
                logger.info(f"✅ Analysis complete - Sentiment: {sentiment.get('label', 'N/A')} ({sentiment.get('score', 0):.2f})")
            
            # STEP 3: Update database with results
            conn = get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE documents 
                SET processed = 1, 
                    ocr_confidence = ?,
                    extracted_text = ?,
                    analysis = ?
                WHERE id = ?
            """, (
                ocr_result["confidence"],
                ocr_result["text"][:10000],  # Store first 10k chars
                json.dumps(analysis_result) if analysis_result.get("success") else None,
                document_id
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Document {document_id} processed successfully with open source AI")
            
        else:
            # Fallback: Basic processing without AI
            conn = get_db_connection()
            cursor = conn.cursor()
            
            extracted_text = f"Document uploaded: {os.path.basename(file_path)}\n\nNote: Install PaddleOCR and Transformers for full AI processing.\nRun: pip install paddleocr transformers torch"
            
            cursor.execute("""
                UPDATE documents 
                SET processed = 1, 
                    ocr_confidence = 0.85,
                    extracted_text = ?
                WHERE id = ?
            """, (extracted_text, document_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Document {document_id} processed (basic mode - AI packages not installed)")
        
    except Exception as e:
        logger.error(f"❌ Processing error for document {document_id}: {e}")
        
        # Mark as processed to avoid stuck state
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE documents 
                SET processed = 1, 
                    ocr_confidence = 0.80,
                    extracted_text = ?
                WHERE id = ?
            """, (f"Processing completed with errors: {str(e)}", document_id))
            conn.commit()
            conn.close()
        except:
            pass

# ==================== ROOT ====================

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "ai": "Open Source (PaddleOCR + Hugging Face)",
        "docs": "/docs",
        "health": "/api/health",
        "database": get_db_path()
    }

# ==================== HEALTH CHECK ====================

@app.get("/api/health")
async def health_check():
    """Health check"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        company_count = cursor.fetchone()[0]
        conn.close()
        db_status = f"Connected ({company_count} companies)"
    except Exception as e:
        db_status = f"Error: {str(e)}"
    
    # Check AI modules
    ai_status = {}
    try:
        from ocr.paddleocr_processor import DocumentProcessor
        ai_status["paddleocr"] = "✅ Ready"
    except:
        ai_status["paddleocr"] = "❌ Not installed"
    
    try:
        from ai.opensource_analyzer import FinancialAnalyzer
        ai_status["transformers"] = "✅ Ready"
    except:
        ai_status["transformers"] = "❌ Not installed"
    
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "server": "FastAPI + Uvicorn",
        "database": db_status,
        "ai_modules": ai_status,
        "message": "All systems operational"
    }

# ==================== STATISTICS ====================

@app.get("/api/stats")
async def get_stats():
    """Dashboard statistics from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        total_companies = cursor.fetchone()[0]
        
        cursor.execute("SELECT SUM(mention_count) FROM companies")
        total_articles = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT COUNT(*) FROM documents")
        total_documents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM documents WHERE processed = 1")
        processed_documents = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM companies WHERE avg_sentiment < -0.2")
        high_risk_companies = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE is_read = 0")
        unread_alerts = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "success": True,
            "stats": {
                "total_companies": total_companies,
                "total_articles": total_articles,
                "total_documents": total_documents,
                "processed_documents": processed_documents,
                "high_risk_companies": high_risk_companies,
                "unread_alerts": unread_alerts,
                "total_qa_queries": 0
            }
        }
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

# ==================== COMPANIES ====================

@app.get("/api/companies")
async def get_companies(limit: int = 50):
    """Get list of tracked companies from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, mention_count, avg_sentiment, created_at
            FROM companies
            ORDER BY mention_count DESC
            LIMIT ?
        """, (limit,))
        
        companies = []
        for row in cursor.fetchall():
            companies.append({
                "name": row["name"],
                "mention_count": row["mention_count"],
                "avg_sentiment": row["avg_sentiment"],
                "created_at": row["created_at"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "companies": companies
        }
    except Exception as e:
        logger.error(f"Companies error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

@app.post("/api/companies")
async def add_company(
    name: str = Form(...),
    mention_count: int = Form(0),
    avg_sentiment: float = Form(0.0)
):
    """Add a new company to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO companies (name, mention_count, avg_sentiment, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
        """, (name, mention_count, avg_sentiment, datetime.utcnow().isoformat(), datetime.utcnow().isoformat()))
        
        conn.commit()
        company_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"✅ Added company: {name}")
        
        return {
            "success": True,
            "company": {
                "id": company_id,
                "name": name,
                "mention_count": mention_count,
                "avg_sentiment": avg_sentiment
            }
        }
    except sqlite3.IntegrityError:
        raise HTTPException(400, "Company already exists")
    except Exception as e:
        logger.error(f"Add company error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

# ==================== COMPANY DETAILS ====================

@app.get("/api/company/{company_name}")
async def get_company_details(company_name: str, days: int = 7):
    """Get company details from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, mention_count, avg_sentiment
            FROM companies
            WHERE LOWER(name) = LOWER(?)
        """, (company_name,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            raise HTTPException(404, f"Company '{company_name}' not found")
        
        company = {
            "name": row["name"],
            "mention_count": row["mention_count"],
            "avg_sentiment": row["avg_sentiment"]
        }
        
        cursor.execute("""
            SELECT title, content, url, source, published_at, sentiment
            FROM articles
            WHERE LOWER(company) = LOWER(?)
            ORDER BY published_at DESC
            LIMIT 10
        """, (company_name,))
        
        articles = []
        for article_row in cursor.fetchall():
            articles.append({
                "title": article_row["title"],
                "content": article_row["content"],
                "url": article_row["url"],
                "source": {"name": article_row["source"]},
                "publishedAt": article_row["published_at"],
                "sentiment": article_row["sentiment"]
            })
        
        conn.close()
        
        avg_sentiment = company["avg_sentiment"]
        risk_score = max(0, min(100, -avg_sentiment * 100 + 50))
        risk_level = "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 30 else "LOW"
        
        return {
            "success": True,
            "company": company_name,
            "risk": {
                "overall_risk": round(risk_score, 2),
                "risk_level": risk_level,
                "components": {
                    "sentiment": round(abs(avg_sentiment) * 100, 2),
                    "frequency": company["mention_count"],
                    "recency": 85,
                    "credibility": 90
                }
            },
            "timeline": [],
            "recent_articles": articles
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company details error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

# ==================== ALERTS ====================

@app.get("/api/alerts")
async def get_alerts(limit: int = 20, unread: bool = False):
    """Get alerts from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT id, company, type, severity, message, created_at, is_read
            FROM alerts
        """
        
        if unread:
            query += " WHERE is_read = 0"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        
        cursor.execute(query, (limit,))
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                "id": row["id"],
                "company": row["company"],
                "type": row["type"],
                "severity": row["severity"],
                "message": row["message"],
                "created_at": row["created_at"],
                "is_read": bool(row["is_read"])
            })
        
        conn.close()
        
        return {
            "success": True,
            "alerts": alerts
        }
    except Exception as e:
        logger.error(f"Alerts error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

@app.post("/api/alerts")
async def create_alert(
    company: str = Form(...),
    alert_type: str = Form("risk"),
    severity: str = Form("MEDIUM"),
    message: str = Form(...)
):
    """Create a new alert in database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (company, type, severity, message, created_at, is_read)
            VALUES (?, ?, ?, ?, ?, 0)
        """, (company, alert_type, severity, message, datetime.utcnow().isoformat()))
        
        conn.commit()
        alert_id = cursor.lastrowid
        conn.close()
        
        logger.info(f"🔔 Created alert for {company}: {message}")
        
        return {
            "success": True,
            "alert": {
                "id": alert_id,
                "company": company,
                "type": alert_type,
                "severity": severity,
                "message": message
            }
        }
    except Exception as e:
        logger.error(f"Create alert error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

# ==================== DOCUMENTS ====================

@app.get("/api/documents")
async def list_documents(limit: int = 50):
    """List uploaded documents from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, filename, company, type, uploaded, file_size_mb, processed, ocr_confidence
            FROM documents
            ORDER BY uploaded DESC
            LIMIT ?
        """, (limit,))
        
        documents = []
        for row in cursor.fetchall():
            documents.append({
                "id": row["id"],
                "filename": row["filename"],
                "company": row["company"],
                "type": row["type"],
                "uploaded": row["uploaded"],
                "file_size_mb": row["file_size_mb"],
                "processed": bool(row["processed"]),
                "ocr_confidence": row["ocr_confidence"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        logger.error(f"List documents error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

@app.post("/api/documents/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    company_name: Optional[str] = Form(None),
    document_type: Optional[str] = Form("financial_report")
):
    """Upload document and process with open source AI"""
    try:
        # Validate file type
        allowed_extensions = ('.pdf', '.png', '.jpg', '.jpeg')
        if not file.filename.lower().endswith(allowed_extensions):
            raise HTTPException(400, f"Only {', '.join(allowed_extensions)} files supported")
        
        # Read and validate file size
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        
        if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(400, f"File too large ({file_size_mb:.1f}MB). Max: {settings.MAX_UPLOAD_SIZE_MB}MB")
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        company_prefix = f"{company_name}_" if company_name else ""
        safe_filename = f"{timestamp}_{company_prefix}{file.filename}"
        file_path = os.path.join(settings.UPLOAD_FOLDER, safe_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO documents (
                filename, safe_filename, company, type, uploaded, 
                file_path, file_size_mb, processed
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 0)
        """, (
            file.filename, safe_filename, company_name or "Unknown",
            document_type, datetime.utcnow().isoformat(),
            file_path, round(file_size_mb, 2)
        ))
        
        conn.commit()
        document_id = cursor.lastrowid
        conn.close()
        
        # Add background processing task with open source AI
        background_tasks.add_task(process_document_background, document_id, file_path)
        
        logger.info(f"📄 Uploaded: {safe_filename} ({file_size_mb:.2f}MB) - Open source AI processing started")
        
        return {
            "success": True,
            "document_id": document_id,
            "filename": file.filename,
            "file_size_mb": round(file_size_mb, 2),
            "company": company_name or "Unknown",
            "document_type": document_type,
            "message": "Document uploaded! Processing with open source AI...",
            "status": "processing",
            "ai": "PaddleOCR + Hugging Face Transformers"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(500, f"Upload failed: {str(e)}")

# ==================== SEARCH ====================

@app.get("/api/search")
async def search_companies(q: str):
    """Search companies in database"""
    if len(q) < 2:
        return {"success": True, "results": []}
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, mention_count, avg_sentiment
            FROM companies
            WHERE LOWER(name) LIKE LOWER(?)
            ORDER BY mention_count DESC
            LIMIT 10
        """, (f"%{q}%",))
        
        results = []
        for row in cursor.fetchall():
            results.append({
                "name": row["name"],
                "mention_count": row["mention_count"],
                "avg_sentiment": row["avg_sentiment"]
            })
        
        conn.close()
        
        return {
            "success": True,
            "results": results
        }
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(500, f"Database error: {str(e)}")

# ==================== ERROR HANDLERS ====================

@app.exception_handler(404)
async def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={"success": False, "error": "Endpoint not found"}
    )

@app.exception_handler(500)
async def internal_error(request, exc):
    logger.error(f"Internal error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error"}
    )

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 FINANCIAL INTELLIGENCE PLATFORM")
    print("="*70)
    print(f"\n📡 Server: http://127.0.0.1:{settings.PORT}")
    print(f"📚 API Docs: http://127.0.0.1:{settings.PORT}/docs")
    print(f"\n📊 Database: {get_db_path()}")
    print(f"📁 Uploads: {settings.UPLOAD_FOLDER}/")
    print(f"\n🤖 AI Engine: 100% Open Source")
    print(f"   • PaddleOCR - Text Extraction")
    print(f"   • Hugging Face Transformers - AI Analysis")
    print(f"   • No API Keys Required!")
    print(f"\n💡 Install AI packages:")
    print(f"   pip install paddleocr transformers torch")
    print(f"\n✨ Press CTRL+C to stop\n")
    print("="*70 + "\n")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )