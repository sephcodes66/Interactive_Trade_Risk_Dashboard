import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, BigInteger
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

# I'm using a declarative base, which is the modern way to do things with SQLAlchemy.
# It lets me define my tables as Python classes.
Base = declarative_base()

class HistoricalPrice(Base):
    """
    This class represents the `historical_prices` table in the database.
    It's designed to store the daily stock price data (Open, High, Low, Close).
    """
    __tablename__ = 'historical_prices'

    # I'm not using a composite primary key of (ticker, date) because it can be
    # a bit of a pain with some ORMs and it's often faster to have a single
    # integer primary key for joins.
    id = Column(Integer, primary_key=True)
    
    # Using a String for the ticker. A fixed-length CHAR might be slightly more
    # efficient, but String is more flexible if we ever get weird ticker symbols.
    ticker = Column(String, nullable=False, index=True)
    
    # The date of the price record. This is indexed because we'll almost always
    # be filtering our queries by date.
    date = Column(Date, nullable=False, index=True)
    
    # Using Float for the price columns. For serious financial applications,
    # a Decimal type would be better to avoid floating-point inaccuracies,
    # but for this prototype, Float is perfectly fine and much simpler.
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float, nullable=False)
    
    # Volume can get pretty big, so a BigInteger is safer than a standard Integer.
    volume = Column(BigInteger)

    def __repr__(self):
        return f"<HistoricalPrice(ticker='{self.ticker}', date='{self.date}', close='{self.close}')>"

# --- Database Connection Setup ---

# This part sets up the database connection so other parts of the app can use it.
load_dotenv()
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable not set.")

engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    A simple dependency for getting a database session.
    This is a common pattern in FastAPI and Flask apps.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_all_tickers():
    """
    A helper function to get a list of all unique tickers from the database.
    This is used to populate the dropdown in the UI.
    """
    db = next(get_db())
    # This query is much faster than loading all prices into pandas and then getting unique tickers.
    tickers = db.query(HistoricalPrice.ticker).distinct().all()
    return sorted([ticker[0] for ticker in tickers])
