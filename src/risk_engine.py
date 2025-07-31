import pandas as pd
import numpy as np
from sqlalchemy import text
from .portfolio import PortfolioManager

class RiskEngine:
    """
    This is where the magic happens. The RiskEngine takes a portfolio
    and runs the calculations for Value at Risk (VaR).
    """
    def __init__(self, portfolio_manager: PortfolioManager):
        self.pm = portfolio_manager
        self.db = self.pm.db_session

    def get_historical_data(self, days=252) -> pd.DataFrame:
        """
        Fetches the last N days of historical price data for all tickers in the portfolio.
        
        I'm using a window function here (`row_number`) to do this efficiently in a
        single database query. The alternative would be to pull all data and then
        filter in pandas, but that would be much slower and use more memory.
        """
        # The SQL query uses a Common Table Expression (CTE) to first number the rows
        # for each ticker by date, and then it selects the top N rows.
        query = text(f"""
            WITH ranked_prices AS (
                SELECT
                    ticker,
                    date,
                    close,
                    ROW_NUMBER() OVER(PARTITION BY ticker ORDER BY date DESC) as rn
                FROM historical_prices
                WHERE ticker IN :tickers
            )
            SELECT ticker, date, close
            FROM ranked_prices
            WHERE rn <= :days
        """)
        
        df = pd.read_sql(query, self.db.bind, params={'tickers': tuple(self.pm.tickers), 'days': days})
        
        # Now, we pivot the data so that each column is a ticker and each row is a date.
        # This is the format we need for our calculations.
        pivot_df = df.pivot(index='date', columns='ticker', values='close').sort_index()
        
        # Financial data often has gaps (weekends, holidays). Forward-filling is a
        # standard way to handle this. It assumes the price just stays the same.
        return pivot_df.ffill()

    def calculate_historical_var(self, days=252, confidence_level=0.95):
        """
        Calculates the 1-day Value at Risk (VaR) using the historical simulation method.

        This method is simple and intuitive. It just looks at the historical daily
        returns and finds the point at which a certain percentage of losses
        would not have been exceeded.
        
        TODO: Add other VaR models, like Parametric VaR (which assumes a normal
        distribution) or a full-blown Monte Carlo simulation.
        """
        if not self.pm.market_values:
            # This should have been called already, but just in case...
            self.pm.calculate_total_market_value()

        # 1. Get historical data
        hist_data = self.get_historical_data(days)
        if hist_data.empty:
            return None, []

        # 2. Calculate daily returns for each stock
        returns = hist_data.pct_change().dropna()

        # 3. Calculate the dollar value of each stock in the portfolio
        weights = pd.Series(self.pm.market_values)
        
        # 4. Calculate the historical P/L for the portfolio
        # We do this by multiplying the daily returns of each stock by its
        # dollar value in the portfolio. This gives us the daily P/L for each asset.
        # Then we sum across the rows to get the total portfolio P/L for each day.
        historical_pl = (returns * weights).sum(axis=1)
        
        # 5. Find the VaR
        # The VaR is the quantile of the historical P/L distribution.
        # For a 95% confidence level, we're looking for the 5th percentile.
        var_value = -historical_pl.quantile(1 - confidence_level)
        
        return var_value, historical_pl.tolist()
