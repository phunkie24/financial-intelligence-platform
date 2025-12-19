# Databricks notebook source
"""
Seed database with initial data
Creates tables if they don't exist
"""
import sqlite3
from datetime import datetime

def create_tables(cursor):
    """Create all necessary tables"""
    
    # Companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            mention_count INTEGER DEFAULT 0,
            avg_sentiment REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Documents table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            safe_filename TEXT NOT NULL,
            company TEXT,
            type TEXT,
            uploaded TEXT DEFAULT CURRENT_TIMESTAMP,
            file_path TEXT NOT NULL,
            file_size_mb REAL,
            processed INTEGER DEFAULT 0,
            ocr_confidence REAL,
            extracted_text TEXT,
            analysis TEXT
        )
    """)
    
    # Alerts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            type TEXT DEFAULT 'risk',
            severity TEXT DEFAULT 'MEDIUM',
            message TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            is_read INTEGER DEFAULT 0
        )
    """)
    
    # Articles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT,
            source TEXT,
            published_at TEXT,
            sentiment REAL DEFAULT 0.0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("✅ Tables created")

def seed_companies(cursor):
    """Seed initial companies"""
    companies = [
        ("Tesla", 25, -0.15),
        ("Apple", 22, 0.45),
        ("Microsoft", 19, 0.32),
        ("Amazon", 17, 0.12),
        ("Google", 15, 0.28),
        ("Meta", 13, -0.08),
        ("Netflix", 11, 0.18),
        ("Nvidia", 9, 0.52),
        ("Intel", 8, 0.05),
        ("AMD", 7, 0.35)
    ]
    
    added = 0
    for name, count, sentiment in companies:
        try:
            cursor.execute(
                "INSERT INTO companies (name, mention_count, avg_sentiment, created_at) VALUES (?, ?, ?, ?)",
                (name, count, sentiment, datetime.utcnow().isoformat())
            )
            added += 1
            print(f"  ✅ Added: {name}")
        except sqlite3.IntegrityError:
            print(f"  ⚠️  Skipped: {name} (already exists)")
    
    print(f"✅ Companies seeded ({added} new)")

def seed_alerts(cursor):
    """Seed initial alerts"""
    alerts = [
        ("Tesla", "risk", "HIGH", "Negative sentiment spike detected in last 24 hours"),
        ("Meta", "risk", "MEDIUM", "Regulatory concerns mentioned in 5 recent articles"),
        ("Netflix", "opportunity", "LOW", "Positive earnings surprise, stock up 8%"),
        ("Apple", "info", "LOW", "New product announcement scheduled for next week")
    ]
    
    added = 0
    for company, atype, severity, message in alerts:
        cursor.execute(
            "INSERT INTO alerts (company, type, severity, message, created_at, is_read) VALUES (?, ?, ?, ?, ?, 0)",
            (company, atype, severity, message, datetime.utcnow().isoformat())
        )
        added += 1
        print(f"  🔔 Added alert: {company} - {severity}")
    
    print(f"✅ Alerts seeded ({added} new)")

def seed_database():
    """Main seed function"""
    db_path = "./financial_intelligence.db"
    
    print("\n" + "="*60)
    print("🌱 Seeding Financial Intelligence Database")
    print("="*60)
    print(f"\n📊 Database: {db_path}\n")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    print("1️⃣  Creating tables...")
    create_tables(cursor)
    conn.commit()
    
    # Seed companies
    print("\n2️⃣  Seeding companies...")
    seed_companies(cursor)
    conn.commit()
    
    # Seed alerts
    print("\n3️⃣  Seeding alerts...")
    seed_alerts(cursor)
    conn.commit()
    
    # Show summary
    cursor.execute("SELECT COUNT(*) FROM companies")
    company_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM alerts")
    alert_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]
    
    conn.close()
    
    print("\n" + "="*60)
    print("✅ SEED COMPLETE!")
    print("="*60)
    print(f"\n📊 Database Summary:")
    print(f"   • Companies: {company_count}")
    print(f"   • Alerts: {alert_count}")
    print(f"   • Documents: {doc_count}")
    print(f"\n🚀 Start the server:")
    print(f"   uvicorn app:app --host 127.0.0.1 --port 8001 --reload")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    seed_database()