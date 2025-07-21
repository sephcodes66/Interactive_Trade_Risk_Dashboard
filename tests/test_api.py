import pytest
import json
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from src.app import server

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    server.config['TESTING'] = True
    with server.test_client() as client:
        yield client

@patch('src.app.PortfolioManager')
@patch('src.app.RiskEngine')
def test_calculate_risk_success(mock_risk_engine, mock_portfolio_manager, client):
    """
    Test the /api/risk endpoint for a successful scenario.
    """
    mock_pm_instance = MagicMock()
    mock_pm_instance.calculate_total_market_value.return_value = 100000.0
    mock_pm_instance.market_values = {"AAPL": 50000.0, "GOOG": 50000.0}
    mock_portfolio_manager.return_value = mock_pm_instance

    mock_re_instance = MagicMock()
    mock_re_instance.calculate_historical_var.return_value = (5000.0, np.array([100, -200]))
    mock_risk_engine.return_value = mock_re_instance

    payload = {
        "portfolio": {"AAPL": 50, "GOOG": 50}
    }
    response = client.post('/api/risk', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 200
    data = response.get_json()
    assert data['total_market_value'] == 100000.0
    assert data['var'] == 5000.0
    assert data['simulated_pl'] == [100, -200]

    mock_portfolio_manager.assert_called_once_with(payload['portfolio'])
    mock_risk_engine.assert_called_once_with(mock_pm_instance)
    mock_pm_instance.calculate_total_market_value.assert_called_once()
    mock_re_instance.calculate_historical_var.assert_called_once_with()

def test_calculate_risk_invalid_input(client):
    """
    Test the /api/risk endpoint with invalid input (missing 'portfolio' key).
    """
    payload = {"wrong_key": {"AAPL": 10}}
    response = client.post('/api/risk', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "'portfolio' key is required" in data['error']

@patch('src.app.PortfolioManager', side_effect=TypeError("Invalid portfolio type"))
def test_calculate_risk_type_error(mock_portfolio_manager, client):
    """
    Test the /api/risk endpoint when PortfolioManager raises a TypeError.
    """
    payload = {"portfolio": "not-a-dict"}
    response = client.post('/api/risk', data=json.dumps(payload), content_type='application/json')

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid portfolio type" in data['error']