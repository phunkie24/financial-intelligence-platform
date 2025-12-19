import requests
import feedparser
from datetime import datetime
from config import Config

class NewsScraper:
    def __init__(self):
        self.news_api_key = Config.NEWS_API_KEY
        self.rss_feeds = Config.RSS_FEEDS
    
    def scrape_news_api(self):
        if not self.news_api_key:
            return []
        
        url = 'https://newsapi.org/v2/everything'
        params = {
            'q': 'technology OR business OR finance',
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': 50,
            'apiKey': self.news_api_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return data.get('articles', [])
        except Exception as e:
            print(f"NewsAPI error: {e}")
            return []
    
    def scrape_rss(self):
        articles = []
        for feed_url in self.rss_feeds:
            try:
                feed = feedparser.parse(feed_url)
                for entry in feed.entries[:10]:
                    article = {
                        'title': entry.get('title', ''),
                        'description': entry.get('summary', ''),
                        'content': entry.get('summary', ''),
                        'url': entry.get('link', ''),
                        'publishedAt': entry.get('published', datetime.now().isoformat()),
                        'source': {'name': feed.feed.get('title', 'RSS')}
                    }
                    articles.append(article)
            except Exception as e:
                print(f"RSS error {feed_url}: {e}")
        return articles
    
    def scrape_all(self):
        articles = []
        articles.extend(self.scrape_news_api())
        articles.extend(self.scrape_rss())
        return articles
