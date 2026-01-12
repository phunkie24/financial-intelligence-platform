"""
Vercel Serverless Function Entry Point for Multi-Agent System

This module adapts the FastAPI backend to work with Vercel's serverless functions.
Note: Some features (like background tasks) may be limited in serverless environment.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the FastAPI app
try:
    from backend.app import app as fastapi_app
except ImportError:
    # Fallback: create minimal app
    fastapi_app = FastAPI(title="Financial Intelligence Platform API")

    @fastapi_app.get("/api/health")
    async def health():
        return {"status": "healthy", "mode": "vercel-serverless"}

# Configure CORS for Vercel
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this based on your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Vercel expects a variable named 'app' or a handler function
app = fastapi_app

# For Vercel Serverless Functions
def handler(request, context):
    """Vercel serverless function handler"""
    return app(request, context)
