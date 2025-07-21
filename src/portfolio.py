from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from src import get_engine
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
        Fetches the most recent price for each ticker in the portfolio.
        
        This is a more "human" or iterative way of solving the problem. A developer might write this first
        before realizing it's inefficient and then optimizing it to the more complex subquery version.
        This version is easier to read but makes a separate database query for every single ticker.
        """
        prices = {}
        tickers = list(self.portfolio.keys())
        if not tickers:
            return prices

        session = self.Session()
        try:
            for ticker in tickers:
                # For each ticker, find the latest price.
                latest_price_query = session.query(
                    MarketData.close_price
                ).join(
                    Instrument, Instrument.instrument_id == MarketData.instrument_id
                ).filter(
                    Instrument.ticker == ticker
                ).order_by(
                    MarketData.price_date.desc()
                ).first()

                if latest_price_query:
                    prices[ticker] = latest_price_query[0]
                else:
                    print(f"Warning: Could not find price data for ticker '{ticker}'. It will be ignored.")
        finally:
            session.close()
        
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