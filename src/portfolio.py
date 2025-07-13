from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from db_connector import get_engine
from src.models import Instrument, MarketData

class PortfolioManager:
    """
    Manages a portfolio of stocks, including fetching current prices
    and calculating market value using the SQLAlchemy ORM.
    """
    def __init__(self, portfolio_dict: dict):
        """
        Initializes the PortfolioManager.
        """
        if not isinstance(portfolio_dict, dict):
            raise TypeError("Portfolio must be a dictionary of ticker symbols and quantities.")
        self.portfolio = portfolio_dict
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)
        self.market_values = {}

    def get_current_prices(self) -> dict:
        """
        Fetches the most recent price for each ticker in the portfolio using an ORM query.
        """
        prices = {}
        tickers = list(self.portfolio.keys())
        if not tickers:
            return prices

        session = self.Session()
        try:
            # Subquery to find the latest date for each instrument
            latest_date_subquery = session.query(
                MarketData.instrument_id,
                func.max(MarketData.price_date).label('max_date')
            ).group_by(MarketData.instrument_id).subquery()

            # Main query to get the price at that latest date
            query_result = session.query(
                Instrument.ticker,
                MarketData.close_price
            ).join(
                latest_date_subquery,
                Instrument.instrument_id == latest_date_subquery.c.instrument_id
            ).join(
                MarketData,
                (MarketData.instrument_id == latest_date_subquery.c.instrument_id) &
                (MarketData.price_date == latest_date_subquery.c.max_date)
            ).filter(
                Instrument.ticker.in_(tickers)
            ).all()

            for ticker, price in query_result:
                prices[ticker] = price
        finally:
            session.close()
        
        for ticker in tickers:
            if ticker not in prices:
                print(f"Warning: Could not find price data for ticker '{ticker}'. It will be ignored.")

        return prices

    def calculate_total_market_value(self) -> float:
        """
        Calculates the total market value of the portfolio.
        """
        current_prices = self.get_current_prices()
        total_value = 0.0

        for ticker, quantity in self.portfolio.items():
            if ticker in current_prices:
                price = float(current_prices[ticker])
                value = price * quantity
                self.market_values[ticker] = value
                total_value += value
        
        return total_value
