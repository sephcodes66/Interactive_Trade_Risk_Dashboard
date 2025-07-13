import os
from datetime import datetime
from portfolio import PortfolioManager
from risk_engine import RiskEngine

# --- Configuration ---
# In a real application, this would come from a config file or a secure source.
SAMPLE_PORTFOLIO = {'AAPL': 150, 'MSFT': 100, 'GOOG': 50, 'TSLA': 75}
REPORT_OUTPUT_DIR = "reports"

def generate_report():
    """
    Generates a daily risk report for a sample portfolio.
    """
    print("Starting daily risk report generation...")

    # 1. Initialize Portfolio and Risk Engine
    try:
        pm = PortfolioManager(SAMPLE_PORTFOLIO)
        risk_engine = RiskEngine(pm)
    except Exception as e:
        print(f"Error initializing portfolio/risk engine: {e}")
        return

    # 2. Perform Calculations
    print("Calculating market value and VaR...")
    try:
        total_value = pm.calculate_total_market_value()
        var_value, _ = risk_engine.calculate_historical_var()
    except Exception as e:
        print(f"Error during risk calculation: {e}")
        return

    # 3. Create Report Content
    print("Formatting the report...")
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    report_content = f"""
# Daily Risk Report

**Report Generated:** {today_str}

---

## Overview

This report summarizes the key risk metrics for the firm's sample portfolio.

- **Portfolio:** `{', '.join(SAMPLE_PORTFOLIO.keys())}`
- **Total Market Value:** `${total_value:,.2f}`
- **95% Historical VaR (1-day):** `${var_value:,.2f}`

---

## Details

The 95% Value at Risk (VaR) of **${var_value:,.2f}** signifies that we can be 95% confident that the portfolio will not lose more than this amount over a one-day period, based on historical data from the last 252 trading days.

"""

    # 4. Write Report to File
    try:
        if not os.path.exists(REPORT_OUTPUT_DIR):
            os.makedirs(REPORT_OUTPUT_DIR)
        
        report_filename = os.path.join(REPORT_OUTPUT_DIR, "daily_risk_report.md")
        with open(report_filename, "w") as f:
            f.write(report_content)
        
        print(f"Successfully generated report: {report_filename}")

    except IOError as e:
        print(f"Error writing report to file: {e}")


if __name__ == '__main__':
    # This allows the script to be run directly from the command line.
    # e.g., python -m src.automate_report
    generate_report()
