import pytest
from unittest.mock import MagicMock
from src.portfolio import PortfolioManager

@pytest.fixture
def mock_db_session(mocker):
    """Fixture to mock the SQLAlchemy session and ORM query."""
    mock_session = MagicMock()
    mock_query = MagicMock()
    
    mock_query.all.return_value = [
        ('AAPL', 150.00),
        ('GOOG', 2800.00),
        ('TSLA', 700.00)
    ]
    
    mock_session.query.return_value.join.return_value.join.return_value.filter.return_value = mock_query
    
    mocker.patch('src.portfolio.sessionmaker', return_value=lambda: mock_session)

def test_portfolio_initialization():
    """Test that the portfolio manager initializes correctly."""
    portfolio_dict = {'AAPL': 10, 'GOOG': 5}
    pm = PortfolioManager(portfolio_dict)
    assert pm.portfolio == portfolio_dict

def test_portfolio_initialization_type_error():
    """Test that a TypeError is raised for invalid portfolio types."""
    with pytest.raises(TypeError):
        PortfolioManager(["AAPL", "GOOG"])

def test_get_current_prices(mock_db_session):
    """Test fetching current prices, ensuring the mock DB is called."""
    pm = PortfolioManager({'AAPL': 10, 'TSLA': 2, 'FAKE': 5})
    prices = pm.get_current_prices()
    
    assert 'AAPL' in prices
    assert 'TSLA' in prices
    assert 'FAKE' not in prices
    assert prices['AAPL'] == 150.00
    assert prices['TSLA'] == 700.00

def test_calculate_total_market_value(mock_db_session):
    """Test the calculation of the total market value."""
    portfolio_dict = {'AAPL': 10, 'GOOG': 2, 'FAKE': 10}
    pm = PortfolioManager(portfolio_dict)
    total_value = pm.calculate_total_market_value()
    
    assert total_value == 7100.00
    assert pm.market_values['AAPL'] == 1500.00
    assert pm.market_values['GOOG'] == 5600.00
    assert 'FAKE' not in pm.market_values

def test_calculate_empty_portfolio(mock_db_session):
    """Test that an empty portfolio returns a total value of 0."""
    pm = PortfolioManager({})
    total_value = pm.calculate_total_market_value()
    assert total_value == 0.0