import pandas as pd
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()

COMPANIES = [
    'Apple', 'Microsoft', 'Google', 'Amazon', 'Tesla', 'Meta',
    'Netflix', 'Nvidia', 'Intel', 'AMD', 'JPMorgan', 'Goldman Sachs'
]

SOURCES = [
    {'name': 'Reuters', 'credibility': 1.0},
    {'name': 'Bloomberg', 'credibility': 1.0},
    {'name': 'CNBC', 'credibility': 0.85},
]

POSITIVE_TEMPLATES = [
    "{company} reports strong Q{q} earnings",
    "{company} stock surges on positive outlook",
    "{company} announces innovative new product",
]

NEGATIVE_TEMPLATES = [
    "{company} faces regulatory scrutiny",
    "{company} stock plummets on earnings miss",
    "{company} CEO steps down amid controversy",
]

NEUTRAL_TEMPLATES = [
    "{company} schedules earnings call",
    "{company} announces board meeting",
    "{company} releases sustainability report",
]

def generate_articles(count=1000):
    articles = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    for i in range(count):
        company = random.choice(COMPANIES)
        source = random.choice(SOURCES)
        
        sentiment_rand = random.random()
        if sentiment_rand < 0.6:
            sentiment = 'neutral'
            sentiment_score = random.uniform(-0.05, 0.05)
            template = random.choice(NEUTRAL_TEMPLATES)
        elif sentiment_rand < 0.85:
            sentiment = 'positive'
            sentiment_score = random.uniform(0.1, 0.9)
            template = random.choice(POSITIVE_TEMPLATES)
        else:
            sentiment = 'negative'
            sentiment_score = random.uniform(-0.9, -0.1)
            template = random.choice(NEGATIVE_TEMPLATES)
        
        title = template.format(company=company, q=random.randint(1, 4))
        content = f"{title}. {fake.paragraph(nb_sentences=3)}"
        
        days_offset = random.randint(0, 30)
        pub_date = start_date + timedelta(days=days_offset, seconds=random.randint(0, 86400))
        
        articles.append({
            'id': i + 1,
            'title': title,
            'content': content,
            'url': f"https://example.com/article-{i}",
            'source_name': source['name'],
            'source_credibility': source['credibility'],
            'published_at': pub_date.isoformat(),
            'company_mentioned': company,
            'sentiment_label': sentiment,
            'sentiment_score': round(sentiment_score, 4),
            'author': fake.name()
        })
    
    df = pd.DataFrame(articles)
    df = df.sort_values('published_at', ascending=False).reset_index(drop=True)
    return df

if __name__ == '__main__':
    print("Generating 1000 sample articles...")
    df = generate_articles(1000)
    df.to_csv('../data/sample_news_articles.csv', index=False)
    print(f"✅ Generated {len(df)} articles")
    print(f"Companies: {df['company_mentioned'].nunique()}")
    print(f"Sentiment distribution:\n{df['sentiment_label'].value_counts()}")
