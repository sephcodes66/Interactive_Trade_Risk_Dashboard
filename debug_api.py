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
        print("\n[Step 1] Initializing PortfolioManager and RiskEngine...")
        pm = PortfolioManager(portfolio_dict)
        risk_engine = RiskEngine(pm)
        print(" -> Success.")

        print("\n[Step 2] Calculating total market value...")
        total_value = pm.calculate_total_market_value()
        print(" -> Total Market Value: {}".format(total_value))
        print(" -> Market Values per Stock: {}".format(pm.market_values))
        if total_value == 0:
            print("\nError: Total market value is zero. Cannot proceed.")
            return

        print("\n[Step 3] Calculating VaR and fetching historical prices...")
        var_value, simulated_pl, hist_prices = risk_engine.calculate_historical_var()
        print(" -> VaR: {}".format(var_value))
        print(" -> Simulated P/L (first 5): {}".format(simulated_pl[:5]))
        print(" -> Historical Prices Shape: {}".format(hist_prices.shape))
        print(" -> Historical Prices (last 2 rows):")
        print(hist_prices.tail(2))

        print("\n[Step 4] Calculating historical performance...")
        hist_performance = risk_engine.calculate_historical_performance(hist_prices)
        print(" -> Historical Performance Shape: {}".format(hist_performance.shape))
        print(" -> Historical Performance (last 2 rows):")
        print(hist_performance.tail(2))

        print("\n[Step 5] Simulation finished successfully!")

    except Exception as e:
        print("\n" + "="*25 + " AN ERROR OCCURRED " + "="*25)
        print(f"The simulation failed with the following error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_portfolio = {'MSFT': 100} 
    
    simulate_api_call(test_portfolio)