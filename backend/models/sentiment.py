from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
    
    def analyze(self, text):
        scores = self.vader.polarity_scores(text)
        return {
            'compound': scores['compound'],
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'label': self._get_label(scores['compound'])
        }
    
    def _get_label(self, compound_score):
        if compound_score >= 0.05:
            return 'positive'
        elif compound_score <= -0.05:
            return 'negative'
        return 'neutral'
    
    def analyze_context(self, text, company_name):
        """Analyze sentiment specifically about the company"""
        sentences = text.split('.')
        relevant = [s for s in sentences if company_name.lower() in s.lower()]
        
        if not relevant:
            return self.analyze(text)
        
        combined = ' '.join(relevant)
        return self.analyze(combined)
