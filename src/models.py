from sqlalchemy import Column, Integer, String, Float, Date, MetaData
from sqlalchemy.orm import declarative_base

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
