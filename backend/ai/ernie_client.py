# Databricks notebook source
"""
ERNIE 4.5 API Client
Handles API calls, prompt management, and response parsing
"""

import os
import json
import logging
from typing import Dict, Optional
import qianfan

logger = logging.getLogger(__name__)

class ERNIEClient:
    def __init__(self):
        """Initialize ERNIE client with API credentials"""
        self.ak = os.getenv('QIANFAN_AK')
        self.sk = os.getenv('QIANFAN_SK')
        
        if not self.ak or not self.sk:
            logger.warning("⚠️ ERNIE API credentials not found. Using mock mode.")
            self.mock_mode = True
        else:
            try:
                self.chat_comp = qianfan.ChatCompletion()
                self.mock_mode = False
                logger.info("✅ ERNIE client initialized")
            except Exception as e:
                logger.error(f"❌ ERNIE initialization failed: {e}")
                self.mock_mode = True
    
    def generate(self, prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate text using ERNIE
        """
        if self.mock_mode:
            return self._mock_response(prompt)
        
        try:
            response = self.chat_comp.do(
                model="ERNIE-4.5-8K",
                messages=[{
                    "role": "user",
                    "content": prompt
                }],
                temperature=temperature,
                max_output_tokens=max_tokens
            )
            
            if response and 'result' in response['body']:
                return response['body']['result']
            else:
                logger.error("Invalid ERNIE response format")
                return ""
                
        except Exception as e:
            logger.error(f"ERNIE generation error: {e}")
            return self._mock_response(prompt)
    
    def analyze(self, text: str, prompt_template: str, **kwargs) -> Dict:
        """
        Analyze text using a prompt template
        Returns parsed response
        """
        # Fill template
        prompt = prompt_template.format(document=text[:8000], **kwargs)  # Limit context
        
        # Generate
        response = self.generate(prompt)
        
        # Try to parse as JSON if response looks like JSON
        if response.strip().startswith('{'):
            try:
                return json.loads(response)
            except:
                pass
        
        # Return as text
        return {'raw_response': response}
    
    def summarize(self, text: str, max_length: int = 200) -> str:
        """Generate executive summary"""
        prompt = f"""Summarize the following financial document in {max_length} words or less. 
Focus on key financial metrics, performance, and outlook.

Document:
{text[:10000]}

Summary:"""
        
        return self.generate(prompt, max_tokens=max_length * 2)
    
    def extract_metrics(self, text: str) -> Dict:
        """Extract key financial metrics"""
        prompt = f"""Extract financial metrics from this document and return as JSON.

Document:
{text[:8000]}

Return JSON with structure:
{{
    "revenue": {{"value": "", "change": "", "period": ""}},
    "profit": {{"value": "", "change": "", "period": ""}},
    "eps": {{"value": "", "change": ""}},
    "guidance": {{"revenue": "", "profit": ""}},
    "margins": {{"gross": "", "operating": "", "net": ""}}
}}

JSON:"""
        
        response = self.generate(prompt, temperature=0.3)
        
        try:
            # Clean response (remove markdown code blocks if present)
            response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(response)
        except:
            return {'raw_response': response}
    
    def assess_risk(self, text: str) -> Dict:
        """Assess financial risks"""
        prompt = f"""Analyze risks in this financial document.

Document:
{text[:8000]}

Return JSON:
{{
    "risk_level": "HIGH/MEDIUM/LOW",
    "risk_score": 0-100,
    "key_risks": ["risk 1", "risk 2"],
    "risk_categories": {{
        "operational": 0-100,
        "financial": 0-100,
        "market": 0-100,
        "regulatory": 0-100
    }}
}}

JSON:"""
        
        response = self.generate(prompt, temperature=0.3)
        
        try:
            response = response.replace('```json', '').replace('```', '').strip()
            return json.loads(response)
        except:
            return {
                'risk_level': 'UNKNOWN',
                'risk_score': 50,
                'key_risks': [],
                'raw_response': response
            }
    
    def _mock_response(self, prompt: str) -> str:
        """Mock response for testing without API"""
        if 'risk' in prompt.lower():
            return json.dumps({
                "risk_level": "MEDIUM",
                "risk_score": 55,
                "key_risks": [
                    "Market volatility concerns",
                    "Supply chain disruptions",
                    "Regulatory uncertainty"
                ],
                "risk_categories": {
                    "operational": 45,
                    "financial": 60,
                    "market": 70,
                    "regulatory": 55
                }
            })
        elif 'metric' in prompt.lower():
            return json.dumps({
                "revenue": {"value": "$10.5B", "change": "+12%", "period": "Q4 2024"},
                "profit": {"value": "$2.1B", "change": "+8%", "period": "Q4 2024"},
                "eps": {"value": "$3.45", "change": "+10%"},
                "margins": {"gross": "45%", "operating": "25%", "net": "20%"}
            })
        else:
            return "This is a mock response. The company showed strong performance with revenue growth of 12% YoY."