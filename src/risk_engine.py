import pandas as pd
import numpy as np
from sqlalchemy import text
from db_connector import get_engine

class RiskEngine:
    """
    Calculates the Value at Risk (VaR) for a given portfolio.
    """
    def __init__(self, portfolio_manager):
        """
        Initializes the RiskEngine.

        Args:
            portfolio_manager (PortfolioManager): An instance of the portfolio manager
                                                  containing the portfolio to be analyzed.
        """
        self.portfolio_manager = portfolio_manager
        self.engine = get_engine()

    def get_historical_data(self, days: int = 252) -> pd.DataFrame:
        """
        Fetches the last 'n' days of historical price data for all tickers
        in the portfolio.

        Args:
            days (int): The number of historical days to fetch. Defaults to 252 (one trading year).

        Returns:
            pd.DataFrame: A DataFrame with historical price data, pivoted by ticker.
                          Returns an empty DataFrame if no data is found.
        """
        tickers = list(self.portfolio_manager.portfolio.keys())
        if not tickers:
            return pd.DataFrame()

        query = text("""
            WITH ranked_prices AS (
                SELECT
                    i.ticker,
                    m.price_date,
                    m.close_price,
                    ROW_NUMBER() OVER(PARTITION BY i.ticker ORDER BY m.price_date DESC) as rn
                FROM instruments i
                JOIN market_data m ON i.instrument_id = m.instrument_id
                WHERE i.ticker IN :tickers
            )
            SELECT ticker, price_date, close_price
            FROM ranked_prices
            WHERE rn <= :days
            ORDER BY price_date ASC;
        """)

        with self.engine.connect() as conn:
            df = pd.read_sql(query, conn, params={"tickers": tuple(tickers), "days": days})

        if df.empty:
            return pd.DataFrame()
            
        # Pivot the table to have dates as index and tickers as columns
        historical_prices_pivot = df.pivot(index='price_date', columns='ticker', values='close_price')
        return historical_prices_pivot

    def calculate_historical_var(self, confidence_level: float = 0.95, days: int = 252) -> tuple:
        """
        Calculates the historical Value at Risk (VaR) for the portfolio.

        Args:
            confidence_level (float): The confidence level for the VaR calculation (e.g., 0.95 for 95%).
            days (int): The number of historical days to use for the calculation.

        Returns:
            tuple: A tuple containing:
                   - var_value (float): The calculated VaR in currency.
                   - simulated_pl (np.array): The array of simulated Profit/Loss values.
        """
        # 1. Get the total market value of the current portfolio
        total_market_value = self.portfolio_manager.calculate_total_market_value()
        if total_market_value == 0:
            return 0.0, np.array([])

        # 2. Get historical price data
        historical_prices = self.get_historical_data(days=days)
        if historical_prices.empty:
            print("Warning: Could not retrieve historical data for VaR calculation.")
            return 0.0, np.array([])
            
        # 3. Calculate daily percentage returns
        daily_returns = historical_prices.pct_change().dropna()

        # 4. Simulate daily Profit/Loss (P/L)
        # Apply historical returns to the current portfolio's total value
        simulated_pl = total_market_value * daily_returns.sum(axis=1)

        # 5. Find the percentile for VaR
        # The VaR is the q-th percentile of the simulated P/L distribution.
        # For a 95% confidence level, we look at the 5th percentile (1 - 0.95).
        var_percentile = 1 - confidence_level
        var_value = -np.percentile(simulated_pl, var_percentile * 100)

        return var_value, simulated_pl.to_numpy()


if __name__ == '__main__':
    from portfolio import PortfolioManager

    # Example Usage
    sample_portfolio = {'AAPL': 10, 'MSFT': 20, 'TSLA': 5}
    print(f"Analyzing portfolio: {sample_portfolio}")

    # 1. Create a PortfolioManager
    pm = PortfolioManager(sample_portfolio)

    # 2. Create a RiskEngine
    risk_engine = RiskEngine(pm)

    # 3. Calculate VaR
    var_95, p_and_l = risk_engine.calculate_historical_var()

    print(f"\nPortfolio Total Value: ${pm.calculate_total_market_value():,.2f}")
    if var_95 is not None:
        print(f"95% Historical VaR (1-day): ${var_95:,.2f}")
        print(f"This means we are 95% confident the portfolio will not lose more than ${var_95:,.2f} in one day.")
    
    if p_and_l.size > 0:
        print(f"\nSimulated P/L distribution (first 5): {p_and_l[:5]}")
