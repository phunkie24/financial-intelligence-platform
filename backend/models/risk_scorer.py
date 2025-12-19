import numpy as np
from datetime import datetime, timedelta
from models.sentiment import SentimentAnalyzer
from config import Config

class RiskScorer:
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.weights = Config.WEIGHTS
        self.source_scores = Config.SOURCE_CREDIBILITY
    
    def calculate_risk(self, company_name, articles, time_window_days=7):
        if not articles:
            return {'overall_risk': 0.0, 'risk_level': 'UNKNOWN'}
        
        # Sentiment score
        sentiments = [a.get('sentiment', 0) for a in articles]
        avg_sentiment = np.mean(sentiments)
        sentiment_score = max(0, -avg_sentiment * 100)
        
        # Frequency score
        mention_count = len(articles)
        frequency_score = min(100, (mention_count / time_window_days) * 20)
        
        # Recency score
        now = datetime.now()
        recency_scores = []
        for article in articles:
            try:
                pub_date = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00'))
                days_ago = (now - pub_date).days
                recency = max(0, 100 - (days_ago * 10))
                recency_scores.append(recency)
            except:
                recency_scores.append(50)
        recency_score = np.mean(recency_scores)
        
        # Credibility score
        credibility_scores = []
        for article in articles:
            source = article.get('source', {}).get('name', 'default').lower()
            cred = self.source_scores.get(source, self.source_scores['default'])
            credibility_scores.append(cred * 100)
        credibility_score = np.mean(credibility_scores)
        
        # Weighted final score
        final_risk = (
            sentiment_score * self.weights['sentiment'] +
            frequency_score * self.weights['frequency'] +
            recency_score * self.weights['recency'] +
            credibility_score * self.weights['credibility']
        )
        
        return {
            'overall_risk': round(final_risk, 2),
            'risk_level': self._get_risk_level(final_risk),
            'articles_analyzed': len(articles),
            'avg_sentiment': round(avg_sentiment, 3),
            'components': {
                'sentiment_score': round(sentiment_score, 2),
                'frequency_score': round(frequency_score, 2),
                'recency_score': round(recency_score, 2),
                'credibility_score': round(credibility_score, 2)
            }
        }
    
    def _get_risk_level(self, risk_score):
        if risk_score >= 70:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MEDIUM'
        return 'LOW'
