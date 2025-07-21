from sqlalchemy import Column, Integer, String, Float, Date, MetaData, text
from sqlalchemy.orm import declarative_base
from src import get_engine

Base = declarative_base()

class Instrument(Base):
    """
    ORM model for the 'instruments' table.
    """
    __tablename__ = 'instruments'
    
    instrument_id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    company_name = Column(String)

class MarketData(Base):
    """
    ORM model for the 'market_data' table.
    """
    __tablename__ = 'market_data'
    
    data_id = Column(Integer, primary_key=True)
    instrument_id = Column(Integer, nullable=False)
    price_date = Column(Date, nullable=False)
    open_price = Column(Float)
    high_price = Column(Float)
    low_price = Column(Float)
    close_price = Column(Float, nullable=False)
    volume = Column(Integer)

def get_all_tickers() -> list:
    """
    Fetches a sorted list of all unique ticker symbols from the database.
    """
    engine = get_engine()
    query = text("SELECT DISTINCT ticker FROM instruments ORDER BY ticker ASC;")
    
    tickers = []
    try:
        with engine.connect() as conn:
            result = conn.execute(query).fetchall()
            tickers = [row[0] for row in result]
    except Exception as e:
        print(f"Error fetching tickers: {e}")
        return ['AAPL', 'GOOG', 'MSFT', 'TSLA', 'VTI', 'AGG'] 
        
    return tickers