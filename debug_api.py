import pandas as pd
from src.portfolio import PortfolioManager
from src.risk_engine import RiskEngine

def simulate_api_call(portfolio_dict: dict):
    """
    Simulates the internal logic of the /api/risk endpoint to debug calculation errors.
    """
    print("="*60)
    print(f"Simulating API call for portfolio: {portfolio_dict}")
    print("="*60)

    try:
        # Step 1: Initialize Managers
        print("\n[Step 1] Initializing PortfolioManager and RiskEngine...")
        pm = PortfolioManager(portfolio_dict)
        risk_engine = RiskEngine(pm)
        print(" -> Success.")

        # Step 2: Calculate Market Value
        print("\n[Step 2] Calculating total market value...")
        total_value = pm.calculate_total_market_value()
        print(f" -> Total Market Value: {total_value}")
        print(f" -> Market Values per Stock: {pm.market_values}")
        if total_value == 0:
            print("\nError: Total market value is zero. Cannot proceed.")
            return

        # Step 3: Calculate VaR and Get Historical Data
        print("\n[Step 3] Calculating VaR and fetching historical prices...")
        var_value, simulated_pl, hist_prices = risk_engine.calculate_historical_var()
        print(f" -> VaR: {var_value}")
        print(f" -> Simulated P/L (first 5): {simulated_pl[:5]}")
        print(f" -> Historical Prices Shape: {hist_prices.shape}")
        print(" -> Historical Prices (last 2 rows):")
        print(hist_prices.tail(2))

        # Step 4: Calculate Historical Performance
        print("\n[Step 4] Calculating historical performance...")
        hist_performance = risk_engine.calculate_historical_performance(hist_prices)
        print(f" -> Historical Performance Shape: {hist_performance.shape}")
        print(" -> Historical Performance (last 2 rows):")
        print(hist_performance.tail(2))

        print("\n[Step 5] Simulation finished successfully!")

    except Exception as e:
        print("\n" + "="*25 + " AN ERROR OCCURRED " + "="*25)
        print(f"The simulation failed with the following error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    # --- Define the portfolio you want to test here ---
    # This portfolio uses a less common ETF which might have incomplete data,
    # making it a good candidate for debugging.
    test_portfolio = {'MSFT': 100} 

    # You can also test the sample portfolios from the dashboard
    # test_portfolio = {"Tech Heavy": {"AAPL": 40, "MSFT": 30, "GOOG": 20, "TSLA": 10}}
    # test_portfolio = {"Balanced": {"VTI": 60, "AGG": 40}}
    
    simulate_api_call(test_portfolio)
