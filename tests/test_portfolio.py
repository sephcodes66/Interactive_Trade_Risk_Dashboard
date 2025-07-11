import pytest
from portfolio import PortfolioManager

# Mock data to be returned by the mocked database query
MOCK_PRICES = {
    'AAPL': 150.00,
    'GOOG': 2800.00,
    'TSLA': 700.00,
}

@pytest.fixture
def mock_db_engine(mocker):
    """Fixture to mock the database engine and its connection."""
    mock_engine = mocker.patch('portfolio.get_engine')
    mock_connection = mock_engine.return_value.connect.return_value.__enter__.return_value
    
    # Set up the mock result for the fetchall() call
    mock_result = mocker.MagicMock()
    mock_result.fetchall.return_value = [
        ('AAPL', 150.00),
        ('GOOG', 2800.00),
        ('TSLA', 700.00)
    ]
    mock_connection.execute.return_value = mock_result
    return mock_engine

def test_portfolio_initialization():
    """Test that the portfolio manager initializes correctly."""
    portfolio_dict = {'AAPL': 10, 'GOOG': 5}
    pm = PortfolioManager(portfolio_dict)
    assert pm.portfolio == portfolio_dict

def test_portfolio_initialization_type_error():
    """Test that a TypeError is raised for invalid portfolio types."""
    with pytest.raises(TypeError):
        PortfolioManager(["AAPL", "GOOG"])

def test_get_current_prices(mock_db_engine):
    """Test fetching current prices, ensuring the mock DB is called."""
    pm = PortfolioManager({'AAPL': 10, 'TSLA': 2, 'FAKE': 5})
    prices = pm.get_current_prices()
    
    # The mock returns all prices, the manager filters them.
    # The test should check that the tickers requested are present.
    assert 'AAPL' in prices
    assert 'TSLA' in prices
    assert 'FAKE' not in prices
    assert prices['AAPL'] == 150.00
    assert prices['TSLA'] == 700.00
    # Verify that the database was queried
    mock_db_engine.return_value.connect.return_value.__enter__.return_value.execute.assert_called_once()

def test_calculate_total_market_value(mock_db_engine):
    """Test the calculation of the total market value."""
    portfolio_dict = {'AAPL': 10, 'GOOG': 2, 'FAKE': 10} # FAKE should be ignored
    pm = PortfolioManager(portfolio_dict)
    total_value = pm.calculate_total_market_value()
    
    # Expected value: (10 * 150.00) + (2 * 2800.00) = 1500 + 5600 = 7100
    assert total_value == 7100.00
    assert pm.market_values['AAPL'] == 1500.00
    assert pm.market_values['GOOG'] == 5600.00
    assert 'FAKE' not in pm.market_values

def test_calculate_empty_portfolio(mock_db_engine):
    """Test that an empty portfolio returns a total value of 0."""
    pm = PortfolioManager({})
    total_value = pm.calculate_total_market_value()
    assert total_value == 0.0
