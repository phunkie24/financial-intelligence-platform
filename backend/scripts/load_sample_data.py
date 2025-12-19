# Databricks notebook source
"""
Generate Sample Financial News Data
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()

# Configuration
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'sample_financial_news.csv')
NUM_ARTICLES = 1000

# Create output directory if it doesn't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
print(f"📁 Output directory: {OUTPUT_DIR}")

# Companies to track
COMPANIES = [
    'Tesla', 'Apple', 'Microsoft', 'Amazon', 'Google', 'Meta',
    'Netflix', 'Nvidia', 'Intel', 'AMD', 'JPMorgan', 'Goldman Sachs',
    'Bank of America', 'Walmart', 'Target', 'Ford'
]

# News sources with credibility scores
SOURCES = {
    'Reuters': 1.0,
    'Bloomberg': 1.0,
    'Financial Times': 0.95,
    'Wall Street Journal': 0.95,
    'CNBC': 0.85,
    'MarketWatch': 0.85,
    'TechCrunch': 0.80,
    'Business Insider': 0.75,
    'The Motley Fool': 0.70,
    'Yahoo Finance': 0.75
}

# Article templates
POSITIVE_TEMPLATES = [
    "{company} reports strong Q{quarter} earnings, beating analyst expectations",
    "{company} announces record revenue growth of {percent}% year-over-year",
    "{company} launches innovative new product line, stock surges",
    "{company} expands operations, creating {number} new jobs",
    "{company} declares special dividend, rewarding shareholders",
    "Analysts upgrade {company} rating following stellar performance",
    "{company} secures major contract worth ${millions}M",
    "{company} CEO confident about future growth prospects"
]

NEGATIVE_TEMPLATES = [
    "{company} faces regulatory scrutiny over business practices",
    "{company} reports disappointing earnings, misses targets",
    "{company} announces layoffs affecting {number} employees",
    "{company} stock drops {percent}% on weak guidance",
    "{company} facing supply chain disruptions",
    "Concerns grow over {company}'s mounting debt levels",
    "{company} recalls products due to safety concerns",
    "Competition intensifies for {company} in key markets"
]

NEUTRAL_TEMPLATES = [
    "{company} holds quarterly earnings call, provides update",
    "{company} appoints new board member",
    "{company} announces routine organizational changes",
    "{company} files quarterly report with SEC",
    "{company} maintains market position in competitive landscape",
    "Analysts maintain neutral rating on {company}",
    "{company} completes previously announced acquisition",
    "{company} participates in industry conference"
]

def generate_article():
    """Generate a single article"""
    company = random.choice(COMPANIES)
    source = random.choice(list(SOURCES.keys()))
    
    # Determine sentiment
    sentiment_type = random.choices(
        ['positive', 'negative', 'neutral'],
        weights=[0.3, 0.2, 0.5]
    )[0]
    
    if sentiment_type == 'positive':
        template = random.choice(POSITIVE_TEMPLATES)
        sentiment = random.uniform(0.3, 0.9)
    elif sentiment_type == 'negative':
        template = random.choice(NEGATIVE_TEMPLATES)
        sentiment = random.uniform(-0.9, -0.3)
    else:
        template = random.choice(NEUTRAL_TEMPLATES)
        sentiment = random.uniform(-0.2, 0.2)
    
    # Fill template
    title = template.format(
        company=company,
        quarter=random.randint(1, 4),
        percent=random.randint(5, 50),
        number=random.randint(100, 5000),
        millions=random.randint(10, 500)
    )
    
    # Generate content
    content = fake.paragraph(nb_sentences=5)
    
    # Generate URL
    url = f"https://{source.lower().replace(' ', '')}.com/article/{fake.uuid4()[:8]}"
    
    # Generate timestamp (last 30 days)
    days_ago = random.randint(0, 30)
    published_at = (datetime.now() - timedelta(days=days_ago)).isoformat()
    
    return {
        'title': title,
        'content': content,
        'url': url,
        'source': source,
        'company': company,
        'sentiment': round(sentiment, 3),
        'published_at': published_at,
        'credibility': SOURCES[source]
    }

def main():
    """Generate sample data"""
    print("\n" + "="*60)
    print("📊 Generating Sample Financial News Data")
    print("="*60 + "\n")
    
    print(f"Companies: {len(COMPANIES)}")
    print(f"Sources: {len(SOURCES)}")
    print(f"Articles to generate: {NUM_ARTICLES}")
    print(f"Output file: {OUTPUT_FILE}\n")
    
    # Generate articles
    articles = []
    for i in range(NUM_ARTICLES):
        if (i + 1) % 100 == 0:
            print(f"Generated {i + 1}/{NUM_ARTICLES} articles...")
        articles.append(generate_article())
    
    # Create DataFrame
    df = pd.DataFrame(articles)
    
    # Save to CSV
    df.to_csv(OUTPUT_FILE, index=False)
    
    print(f"\n✅ Successfully generated {NUM_ARTICLES} articles")
    print(f"💾 Saved to: {OUTPUT_FILE}")
    
    # Statistics
    print("\n" + "="*60)
    print("📈 Statistics:")
    print("="*60)
    print(f"Positive articles: {len(df[df['sentiment'] > 0.2])}")
    print(f"Negative articles: {len(df[df['sentiment'] < -0.2])}")
    print(f"Neutral articles: {len(df[df['sentiment'].between(-0.2, 0.2)])}")
    print(f"Average sentiment: {df['sentiment'].mean():.3f}")
    print(f"Date range: {df['published_at'].min()} to {df['published_at'].max()}")
    print("\nTop 5 companies by mentions:")
    print(df['company'].value_counts().head())

if __name__ == "__main__":
    main()