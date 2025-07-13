from sqlalchemy import text
from db_connector import get_engine

class PortfolioManager:
    """
    Manages a portfolio of stocks, including fetching current prices
    and calculating market value.
    """
    def __init__(self, portfolio_dict: dict):
        """
        Initializes the PortfolioManager.

        Args:
            portfolio_dict: A dictionary representing the portfolio,
                            e.g., {'AAPL': 50, 'GOOG': 30}
        """
        if not isinstance(portfolio_dict, dict):
            raise TypeError("Portfolio must be a dictionary of ticker symbols and quantities.")
        self.portfolio = portfolio_dict
        self.engine = get_engine()
        self.market_values = {}

    def get_current_prices(self) -> dict:
        """
        Fetches the most recent price for each ticker in the portfolio.
        """
        prices = {}
        tickers = list(self.portfolio.keys())
        if not tickers:
            return prices

        # This single query is more efficient than one query per ticker.
        query = text("""
            SELECT i.ticker, m.close_price
            FROM instruments i
            JOIN (
                SELECT instrument_id, MAX(price_date) as max_date
                FROM market_data
                GROUP BY instrument_id
            ) latest ON i.instrument_id = latest.instrument_id
            JOIN market_data m ON latest.instrument_id = m.instrument_id AND latest.max_date = m.price_date
            WHERE i.ticker IN :tickers;
        """)

        with self.engine.connect() as conn:
            result = conn.execute(query, {"tickers": tuple(tickers)}).fetchall()
            for row in result:
                prices[row[0]] = row[1]
        
        # Warn about any tickers that were not found in the database.
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
