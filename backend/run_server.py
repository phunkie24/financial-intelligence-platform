"""
Simple server startup script for testing the multi-agent system locally
"""
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("🚀 Starting Financial Intelligence Platform Backend")
    logger.info("📍 Server will run at: http://127.0.0.1:8001")
    logger.info("📊 API Docs available at: http://127.0.0.1:8001/docs")
    logger.info("🤖 Multi-Agent System will initialize on first request")

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8001,
        reload=True,
        log_level="info"
    )
