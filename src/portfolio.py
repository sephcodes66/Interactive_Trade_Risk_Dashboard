from sqlalchemy import text
from db_connector import get_engine

class PortfolioManager:
    """
    Manages a simulated portfolio of stocks.
    """
    def __init__(self, portfolio_dict: dict):
        """
        Initializes the PortfolioManager with a portfolio.

        Args:
            portfolio_dict (dict): A dictionary representing the portfolio,
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

        Returns:
            dict: A dictionary mapping each ticker to its most recent close price.
        """
        prices = {}
        tickers = list(self.portfolio.keys())
        if not tickers:
            return prices

        # This SQL query finds the latest price for each requested ticker
        # It's more efficient to do this in one query than one query per ticker.
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
        
        # Check for any tickers that were not found in the database
        for ticker in tickers:
            if ticker not in prices:
                print(f"Warning: Could not find price data for ticker '{ticker}'. It will be ignored.")

        return prices

    def calculate_total_market_value(self) -> float:
        """
        Calculates the total market value of the portfolio.

        Returns:
            float: The total market value.
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

if __name__ == '__main__':
    # Example Usage
    # Define a sample portfolio
    sample_portfolio = {'AAPL': 10, 'MSFT': 20, 'TSLA': 5, 'INVALID': 100}
    
    print(f"Initializing portfolio: {sample_portfolio}")
    
    # Create a PortfolioManager instance
    manager = PortfolioManager(sample_portfolio)
    
    # Calculate and print the total market value
    total_value = manager.calculate_total_market_value()
    
    print("\nCalculating market values...")
    for ticker, value in manager.market_values.items():
        print(f"  - {ticker}: ${value:,.2f}")
        
    print(f"\nTotal Portfolio Market Value: ${total_value:,.2f}")
