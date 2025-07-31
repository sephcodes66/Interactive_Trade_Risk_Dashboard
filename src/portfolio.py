from sqlalchemy.orm import Session
from .models import HistoricalPrice, get_db

class PortfolioManager:
    """
    Handles all the logic related to a user's portfolio, like fetching
    prices and calculating market values.
    """
    def __init__(self, portfolio: dict[str, int]):
        """
        Initializes the PortfolioManager with a portfolio.

        Args:
            portfolio: A dictionary where keys are stock tickers (e.g., "AAPL")
                       and values are the number of shares.
        """
        if not isinstance(portfolio, dict) or not portfolio:
            raise ValueError("Portfolio must be a non-empty dictionary.")
            
        self.portfolio = portfolio
        self.tickers = list(portfolio.keys())
        self.db_session: Session = next(get_db())
        
        # These will be populated by the methods below.
        self.current_prices = {}
        self.market_values = {}

    def get_current_prices(self) -> dict[str, float]:
        """
        Fetches the most recent closing price for each stock in the portfolio.
        
        TODO: This is a classic N+1 query problem. It's fine for a small number
        of tickers, but if the portfolio gets big, this will be slow.
        A better way would be to fetch all prices in a single query.
        """
        prices = {}
        for ticker in self.tickers:
            # For each ticker, we query the database for the most recent price record.
            result = self.db_session.query(HistoricalPrice.close)\
                .filter(HistoricalPrice.ticker == ticker)\
                .order_by(HistoricalPrice.date.desc())\
                .first()
            
            if result:
                prices[ticker] = result[0]
        
        self.current_prices = prices
        return prices

    def calculate_total_market_value(self) -> float:
        """
        Calculates the total market value of the entire portfolio.
        It needs to fetch the current prices first.
        """
        self.get_current_prices()
        
        total_value = 0.0
        for ticker, quantity in self.portfolio.items():
            price = self.current_prices.get(ticker)
            if price is not None:
                # If we found a price, we calculate the market value for this stock
                # and add it to our running total.
                market_value = price * quantity
                self.market_values[ticker] = market_value
                total_value += market_value
        
        return total_value
