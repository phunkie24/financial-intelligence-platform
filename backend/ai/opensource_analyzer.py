# Databricks notebook source
"""
Open Source AI Analysis using Hugging Face Transformers
100% Free - No API keys needed
"""

from transformers import pipeline
import logging
import re

logger = logging.getLogger(__name__)

class FinancialAnalyzer:
    def __init__(self):
        """Initialize AI models"""
        try:
            # Sentiment analysis (lightweight model)
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            
            # Summarization (lightweight model)
            self.summarizer = pipeline(
                "summarization",
                model="facebook/bart-large-cnn"
            )
            
            logger.info("✅ AI models loaded")
            
        except Exception as e:
            logger.warning(f"⚠️ Could not load AI models: {e}")
            self.sentiment_analyzer = None
            self.summarizer = None
    
    def analyze_financial_document(self, text):
        """
        Analyze financial document text
        Extract metrics, sentiment, and insights
        """
        try:
            # Extract financial metrics
            metrics = self._extract_metrics(text)
            
            # Analyze sentiment
            sentiment = self._analyze_sentiment(text)
            
            # Generate summary
            summary = self._generate_summary(text)
            
            # Calculate risk score
            risk = self._calculate_risk(text, sentiment)
            
            return {
                "success": True,
                "metrics": metrics,
                "sentiment": sentiment,
                "summary": summary,
                "risk": risk,
                "method": "Open Source AI (Hugging Face)"
            }
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_metrics(self, text):
        """Extract financial metrics using regex"""
        metrics = {
            "revenue": [],
            "profit": [],
            "growth": [],
            "eps": []
        }
        
        # Find revenue mentions (e.g., "$96.8B", "96.8 billion")
        revenue_pattern = r'\$?\d+\.?\d*\s*[BMK]?(?:illion)?.*?revenue'
        metrics["revenue"] = re.findall(revenue_pattern, text, re.IGNORECASE)[:3]
        
        # Find profit mentions
        profit_pattern = r'\$?\d+\.?\d*\s*[BMK]?(?:illion)?.*?(?:profit|earnings|income)'
        metrics["profit"] = re.findall(profit_pattern, text, re.IGNORECASE)[:3]
        
        # Find growth percentages
        growth_pattern = r'\d+\.?\d*%.*?(?:growth|increase|up)'
        metrics["growth"] = re.findall(growth_pattern, text, re.IGNORECASE)[:3]
        
        # Find EPS
        eps_pattern = r'EPS.*?\$?\d+\.?\d+'
        metrics["eps"] = re.findall(eps_pattern, text, re.IGNORECASE)[:2]
        
        return metrics
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment using AI"""
        if not self.sentiment_analyzer:
            return self._basic_sentiment(text)
        
        try:
            # Analyze chunks (models have token limits)
            chunks = self._split_text(text, max_length=500)
            sentiments = []
            
            for chunk in chunks[:5]:  # Analyze first 5 chunks
                result = self.sentiment_analyzer(chunk)[0]
                score = result['score'] if result['label'] == 'POSITIVE' else -result['score']
                sentiments.append(score)
            
            avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0
            
            return {
                "score": round(avg_sentiment, 3),
                "label": "Positive" if avg_sentiment > 0.1 else "Negative" if avg_sentiment < -0.1 else "Neutral",
                "confidence": abs(avg_sentiment)
            }
            
        except Exception as e:
            logger.error(f"Sentiment analysis error: {e}")
            return self._basic_sentiment(text)
    
    def _basic_sentiment(self, text):
        """Fallback sentiment analysis using keywords"""
        positive_words = ['growth', 'increase', 'strong', 'positive', 'up', 'gain', 'profit', 'success']
        negative_words = ['decline', 'decrease', 'weak', 'negative', 'down', 'loss', 'risk', 'concern']
        
        text_lower = text.lower()
        positive_count = sum(text_lower.count(word) for word in positive_words)
        negative_count = sum(text_lower.count(word) for word in negative_words)
        
        total = positive_count + negative_count
        if total == 0:
            return {"score": 0, "label": "Neutral", "confidence": 0}
        
        score = (positive_count - negative_count) / total
        
        return {
            "score": round(score, 3),
            "label": "Positive" if score > 0.1 else "Negative" if score < -0.1 else "Neutral",
            "confidence": abs(score)
        }
    
    def _generate_summary(self, text):
        """Generate summary using AI or extractive method"""
        if not self.summarizer or len(text) < 200:
            return self._extractive_summary(text)
        
        try:
            # Summarize first 1000 words
            words = text.split()[:1000]
            chunk = ' '.join(words)
            
            summary = self.summarizer(chunk, max_length=130, min_length=30, do_sample=False)[0]
            return summary['summary_text']
            
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            return self._extractive_summary(text)
    
    def _extractive_summary(self, text):
        """Simple extractive summary - first 3 sentences"""
        sentences = text.split('.')[:3]
        return '. '.join(sentences) + '.'
    
    def _calculate_risk(self, text, sentiment):
        """Calculate risk score based on text and sentiment"""
        risk_keywords = ['risk', 'uncertainty', 'concern', 'challenge', 'threat', 'negative', 'decline']
        
        text_lower = text.lower()
        risk_mentions = sum(text_lower.count(word) for word in risk_keywords)
        
        # Combine keyword count and sentiment
        sentiment_risk = max(0, -sentiment['score']) * 50
        keyword_risk = min(risk_mentions * 5, 50)
        
        risk_score = (sentiment_risk + keyword_risk)
        risk_level = "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 30 else "LOW"
        
        return {
            "score": round(risk_score, 2),
            "level": risk_level
        }
    
    def _split_text(self, text, max_length=500):
        """Split text into chunks"""
        words = text.split()
        chunks = []
        current_chunk = []
        
        for word in words:
            current_chunk.append(word)
            if len(' '.join(current_chunk)) > max_length:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks