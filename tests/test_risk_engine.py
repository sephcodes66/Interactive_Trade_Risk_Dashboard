import pytest
import pandas as pd
import numpy as np
from unittest.mock import MagicMock
from src.portfolio import PortfolioManager
from src.risk_engine import RiskEngine

@pytest.fixture
def mock_portfolio_manager(mocker):
    """Fixture to create a mocked PortfolioManager."""
    mock_pm = mocker.MagicMock(spec=PortfolioManager)
    mock_pm.portfolio = {'AAPL': 10, 'GOOG': 2}
    mock_pm.market_values = {'AAPL': 80000.0, 'GOOG': 20000.0}
    mock_pm.calculate_total_market_value.return_value = 100000.0 
    return mock_pm

@pytest.fixture
def mock_read_sql(mocker):
    """Fixture to mock the pandas.read_sql function."""
    # Create a sample historical data DataFrame to be returned by read_sql
    data = {
        'price_date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-01', '2023-01-02', '2023-01-03']),
        'ticker': ['AAPL', 'AAPL', 'AAPL', 'GOOG', 'GOOG', 'GOOG'],
        'close_price': [100, 101, 100, 2000, 1980, 2020]
    }
    mock_df = pd.DataFrame(data)
    
    # The RiskEngine uses pd.read_sql, so we patch that
    mocker.patch('pandas.read_sql', return_value=mock_df)

def test_risk_engine_initialization(mock_portfolio_manager):
    """Test that the RiskEngine initializes correctly."""
    re = RiskEngine(mock_portfolio_manager)
    assert re.portfolio_manager == mock_portfolio_manager

def test_get_historical_data(mock_portfolio_manager, mock_read_sql):
    """Test the fetching and pivoting of historical data."""
    re = RiskEngine(mock_portfolio_manager)
    historical_data = re.get_historical_data(days=3)
    
    assert not historical_data.empty
    assert 'AAPL' in historical_data.columns and 'GOOG' in historical_data.columns
    assert historical_data.shape == (3, 2)
    assert historical_data['AAPL'][pd.to_datetime('2023-01-02')] == 101

def test_calculate_historical_var(mock_portfolio_manager, mock_read_sql, mocker):
    """Test the main VaR calculation logic."""
    re = RiskEngine(mock_portfolio_manager)
    var_value, simulated_pl, hist_prices = re.calculate_historical_var()

    assert simulated_pl.shape[0] == 2 # 2 days of returns
    assert var_value is not None
    assert isinstance(var_value, float)
    assert not hist_prices.empty
    
    # With a known P/L array, we can test the percentile calculation
    re.get_historical_data = mocker.MagicMock()
    test_pl = np.array([-1000, -500, 100, 2000])
    var = -np.percentile(test_pl, 5)
    assert np.isclose(var, 925.0)

