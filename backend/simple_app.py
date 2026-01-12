"""
Simple working backend for testing frontend
"""
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Financial Intelligence Platform - Test Mode")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure upload directory exists
os.makedirs("uploads", exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Financial Intelligence Platform API", "status": "running"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/stats")
async def stats():
    return {
        "stats": {
            "total_companies": 8,
            "total_documents": 12,
            "total_alerts": 3,
            "avg_sentiment": 0.65
        }
    }

@app.get("/api/companies")
async def companies():
    return {
        "companies": [
            {"name": "Apple Inc.", "mention_count": 245, "avg_sentiment": 0.78},
            {"name": "Tesla", "mention_count": 189, "avg_sentiment": 0.62},
            {"name": "Microsoft", "mention_count": 156, "avg_sentiment": 0.71},
            {"name": "NVIDIA", "mention_count": 134, "avg_sentiment": 0.85}
        ]
    }

@app.get("/api/documents")
async def documents():
    return {
        "documents": [
            {"id": 1, "filename": "AAPL_Q4_2024.pdf", "company": "Apple", "uploaded": "2024-01-10", "processed": 1},
            {"id": 2, "filename": "TSLA_Earnings.pdf", "company": "Tesla", "uploaded": "2024-01-09", "processed": 1}
        ]
    }

@app.get("/api/alerts")
async def alerts():
    return {
        "alerts": [
            {"id": 1, "company": "Tesla", "severity": "high", "message": "Stock volatility detected", "timestamp": "2024-01-10T10:30:00"},
            {"id": 2, "company": "Apple", "severity": "medium", "message": "Earnings announcement soon", "timestamp": "2024-01-10T09:15:00"}
        ]
    }

@app.post("/api/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    company: str = Form(...),
    document_type: str = Form("earnings_report")
):
    """Handle document upload"""
    try:
        logger.info(f"📄 Receiving file: {file.filename} for {company}")

        # Save file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = os.path.join("uploads", safe_filename)

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        logger.info(f"✅ File saved: {file_path}")

        # Return mock analysis result
        return {
            "success": True,
            "document_id": 1,
            "filename": file.filename,
            "safe_filename": safe_filename,
            "company": company,
            "file_size_mb": len(content) / (1024 * 1024),
            "message": "Document uploaded successfully. Processing with CAMEL-AI agents...",
            "status": "processing",
            "analysis": {
                "extracted_text": "Sample extracted text from document...",
                "metrics": {
                    "revenue": 10200000000,
                    "net_income": 2100000000,
                    "eps": 5.25
                },
                "risk_score": 35,
                "risk_level": "LOW",
                "sentiment": 0.75
            }
        }

    except Exception as e:
        logger.error(f"❌ Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agents/status")
async def agent_status():
    """Multi-agent system status"""
    return {
        "system_status": "OPERATIONAL",
        "agents": {
            "Orchestrator": {"status": "idle", "tasks_completed": 0},
            "Document Processor": {"status": "idle", "tasks_completed": 0},
            "Financial Analyst": {"status": "idle", "tasks_completed": 0},
            "Risk Assessor": {"status": "idle", "tasks_completed": 0},
            "Knowledge Manager": {"status": "idle", "tasks_completed": 0},
            "News Monitor": {"status": "idle", "tasks_completed": 0},
            "Critic": {"status": "idle", "tasks_completed": 0}
        },
        "message_hub": {
            "total_agents": 7,
            "total_messages": 0
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("🚀 Starting simple test backend")
    logger.info("📍 Server: http://127.0.0.1:8002")
    logger.info("📊 API Docs: http://127.0.0.1:8002/docs")
    uvicorn.run(app, host="127.0.0.1", port=8002)
