# Databricks notebook source
"""
Complete Setup Script
Creates directories, initializes database, generates sample data
"""

import sys
import os

# Add to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_directories():
    """Create all necessary directories"""
    print("\n📁 Creating directories...")
    directories = ['data', 'uploads', 'chroma_db', 'models', 'logs', 'docs']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ {directory}/")

def create_package_structure():
    """Create __init__.py files"""
    print("\n📦 Creating package structure...")
    packages = ['.', 'models', 'utils', 'ai', 'ocr', 'scrapers', 'scripts', 'fine_tuning']
    for package in packages:
        if os.path.exists(package):
            init_file = os.path.join(package, '__init__.py')
            if not os.path.exists(init_file):
                with open(init_file, 'w') as f:
                    f.write(f'# {package} package\n')
                print(f"  ✅ {package}/__init__.py")

def initialize_database():
    """Initialize database tables"""
    print("\n🗄️ Initializing database...")
    try:
        from sqlalchemy import create_engine
        from models.database_models import Base
        from config import settings
        
        engine = create_engine(settings.DATABASE_URL, echo=False)
        Base.metadata.create_all(engine)
        print("  ✅ Database tables created")
    except Exception as e:
        print(f"  ⚠️ Database initialization skipped: {e}")

def generate_sample_data():
    """Generate sample financial news data"""
    print("\n📊 Generating sample data...")
    try:
        # Import after path is set
        from scripts.generate_sample_data import main as generate_main
        generate_main()
    except Exception as e:
        print(f"  ⚠️ Sample data generation skipped: {e}")
        print(f"  Run manually: python scripts/generate_sample_data.py")

def main():
    """Run complete setup"""
    print("\n" + "="*60)
    print("🚀 FINANCIAL INTELLIGENCE PLATFORM - COMPLETE SETUP")
    print("="*60)
    
    # Step 1: Directories
    create_directories()
    
    # Step 2: Package structure
    create_package_structure()
    
    # Step 3: Database
    initialize_database()
    
    # Step 4: Sample data
    generate_sample_data()
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\n🎯 Next steps:")
    print("  1. Configure .env file with your API keys")
    print("  2. Start the server: uvicorn app:app --port 8001 --reload")
    print("  3. Access API docs: http://localhost:8001/docs")
    print()

if __name__ == "__main__":
    main()