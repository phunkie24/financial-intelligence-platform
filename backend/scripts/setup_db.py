from sqlalchemy import create_engine
from utils.db_manager import Base

def setup_database():
    engine = create_engine('sqlite:///financial_news.db')
    Base.metadata.create_all(engine)
    print("✅ Database created successfully!")

if __name__ == '__main__':
    setup_database()
