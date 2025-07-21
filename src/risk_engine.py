import pandas as pd
import numpy as np
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker
from src import get_engine
from src.models import Instrument, MarketData

class RiskEngine:
    """
    Calculates financial risk metrics for a given portfolio using the SQLAlchemy ORM.
    """
    def __init__(self, portfolio_manager):
        """
        Initializes the RiskEngine.
        """
        self.portfolio_manager = portfolio_manager
        self.engine = get_engine()
        self.Session = sessionmaker(bind=self.engine)

    def get_historical_data(self, days: int = 252) -> pd.DataFrame:
        """
        Fetches the last 'n' days of historical price data for all tickers
        in the portfolio using an ORM query.
        """
        tickers = list(self.portfolio_manager.portfolio.keys())
        if not tickers:
            return pd.DataFrame()

        session = self.Session()
        try:
            ranked_prices_subquery = session.query(
                Instrument.ticker,
                MarketData.price_date,
                MarketData.close_price,
                func.row_number().over(
                    partition_by=Instrument.ticker,
                    order_by=MarketData.price_date.desc()
                ).label('rn')
            ).join(
                MarketData,
                Instrument.instrument_id == MarketData.instrument_id
            ).filter(
                Instrument.ticker.in_(tickers)
            ).subquery()

            query = session.query(
                ranked_prices_subquery.c.ticker,
                ranked_prices_subquery.c.price_date,
                ranked_prices_subquery.c.close_price
            ).filter(
                ranked_prices_subquery.c.rn <= days
            ).order_by(
                ranked_prices_subquery.c.price_date.asc()
            )
            
            df = pd.read_sql(query.statement, session.bind)

        finally:
            session.close()

        if df.empty:
            return pd.DataFrame()
            
        historical_prices_pivot = df.pivot(index='price_date', columns='ticker', values='close_price')
        
        # NOTE: Using forward-fill to handle missing data for non-trading days (like weekends).
        # This is a simplifying assumption: it assumes the price just carries over.
        # For a more advanced model, we might want to interpolate or use a more sophisticated method.
        historical_prices_pivot.ffill(inplace=True)
        
        # If a stock has no data at all in the window, it will be all NaNs. Drop it.
        historical_prices_pivot.dropna(axis='columns', how='all', inplace=True)
        
        return historical_prices_pivot

    def calculate_historical_var(self, confidence_level: float = 0.95, days: int = 252) -> tuple:
        """
        Calculates the historical Value at Risk (VaR) for the portfolio.
        """
        total_market_value = self.portfolio_manager.calculate_total_market_value()
        if total_market_value == 0:
            return 0.0, np.array([])

        historical_prices = self.get_historical_data(days=days)
        if historical_prices.empty:
            return 0.0, np.array([])

        weights = pd.Series(self.portfolio_manager.market_values) / total_market_value
        aligned_weights = weights.reindex(historical_prices.columns, fill_value=0)
            
        daily_returns = historical_prices.pct_change(fill_method=None).dropna()

        if daily_returns.empty:
            return 0.0, np.array([])

        portfolio_returns = (daily_returns * aligned_weights).sum(axis=1)
        simulated_pl = total_market_value * portfolio_returns

        var_percentile = 1 - confidence_level
        var_value = -np.percentile(simulated_pl, var_percentile * 100)

        return var_value, simulated_pl.to_numpy()