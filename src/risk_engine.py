import pandas as pd
import numpy as np
from sqlalchemy import text
from db_connector import get_engine

class RiskEngine:
    """
    Calculates financial risk metrics for a given portfolio.
    """
    def __init__(self, portfolio_manager):
        """
        Initializes the RiskEngine.
        """
        self.portfolio_manager = portfolio_manager
        self.engine = get_engine()

    def get_historical_data(self, days: int = 252) -> pd.DataFrame:
        """
        Fetches the last 'n' days of historical price data for all tickers
        in the portfolio.
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
            
        historical_prices_pivot = df.pivot(index='price_date', columns='ticker', values='close_price')
        
        # Drop columns that are all NaN, which can happen if a ticker has no price data.
        # This prevents calculation errors downstream.
        historical_prices_pivot.dropna(axis='columns', how='all', inplace=True)
        
        return historical_prices_pivot

    def calculate_historical_performance(self, historical_prices: pd.DataFrame) -> pd.Series:
        """
        Calculates the daily market value of the portfolio over a historical period.
        """
        quantities = pd.Series(self.portfolio_manager.portfolio)
        aligned_quantities = quantities.reindex(historical_prices.columns, fill_value=0)
        daily_values = historical_prices * aligned_quantities
        portfolio_performance = daily_values.sum(axis=1)
        
        return portfolio_performance

    def calculate_historical_var(self, confidence_level: float = 0.95, days: int = 252) -> tuple:
        """
        Calculates the historical Value at Risk (VaR) for the portfolio.

        Returns:
            A tuple containing: (var_value, simulated_pl, historical_prices)
        """
        total_market_value = self.portfolio_manager.calculate_total_market_value()
        if total_market_value == 0:
            return 0.0, np.array([]), pd.DataFrame()

        historical_prices = self.get_historical_data(days=days)
        if historical_prices.empty:
            return 0.0, np.array([]), pd.DataFrame()

        # Calculate weights for each stock to properly attribute returns.
        weights = pd.Series(self.portfolio_manager.market_values) / total_market_value
        aligned_weights = weights.reindex(historical_prices.columns, fill_value=0)
            
        daily_returns = historical_prices.pct_change(fill_method=None).dropna()

        # If there's not enough data to calculate returns, exit gracefully.
        if daily_returns.empty:
            return 0.0, np.array([]), historical_prices

        # Calculate weighted portfolio returns and simulated Profit/Loss.
        portfolio_returns = (daily_returns * aligned_weights).sum(axis=1)
        simulated_pl = total_market_value * portfolio_returns

        var_percentile = 1 - confidence_level
        var_value = -np.percentile(simulated_pl, var_percentile * 100)

        return var_value, simulated_pl.to_numpy(), historical_prices
