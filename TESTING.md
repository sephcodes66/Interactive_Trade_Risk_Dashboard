# RiskDash - User Acceptance Testing (UAT)

This document outlines the User Acceptance Testing (UAT) cases for the RiskDash prototype. The purpose of these tests is to verify that the application meets the business requirements and functions correctly from an end-user's perspective.

## Test Scenarios

| Test Case ID | Test Scenario | Action Steps | Expected Result |
|---|---|---|---|
| **UAT-01** | **Analyze a Tech-Heavy Portfolio** | 1. Launch the application. <br> 2. From the "Select stocks" dropdown, choose `AAPL`, `MSFT`, and `TSLA`. <br> 3. In the input boxes that appear, enter `50` for AAPL, `30` for MSFT, and `20` for TSLA. <br> 4. Click "Analyze Portfolio". | The dashboard updates to show the analysis. All four sections (Key Risk Metrics, Risk Concentration, P/L Simulation, and Historical Performance) are displayed with calculated values. The pie chart shows the three stocks with their respective weights. |
| **UAT-02** | **Analyze a Diversified Portfolio** | 1. Launch the application. <br> 2. Select `VTI` (a stock ETF) and `AGG` (a bond ETF). <br> 3. Enter `60` for VTI and `40` for AGG. <br> 4. Click "Analyze Portfolio". | The dashboard updates. The calculated VaR should be relatively low compared to the tech-heavy portfolio, demonstrating the risk-reducing effect of diversification. All charts are displayed correctly. |
| **UAT-03** | **Handle a Stock with Missing Data** | 1. Launch the application. <br> 2. Select a single, less common stock that might have incomplete data (e.g., `AIEQ`). <br> 3. Enter a quantity of `100`. <br> 4. Click "Analyze Portfolio". | The application remains stable. If a chart cannot be generated due to insufficient data, a message like "Historical performance chart could not be generated" is displayed in its place, but the rest of the analysis (like VaR) is still shown. The app does not crash. |
| **UAT-04** | **Dynamically Update Portfolio** | 1. Perform the analysis for any portfolio. <br> 2. Remove one stock from the "Select stocks" dropdown. <br> 3. Click "Analyze Portfolio" again. | The dashboard updates correctly. The removed stock and its quantity input disappear. The analysis results are recalculated for the new, smaller portfolio. |
| **UAT-05** | **Invalid Input (No Quantity)** | 1. Launch the application. <br> 2. Select one or more stocks. <br> 3. Do not enter any quantities. <br> 4. Click "Analyze Portfolio". | A user-friendly error message like "Please enter a quantity for at least one stock" is displayed in red text. No analysis is performed. |

---

## Acceptance Criteria

This section defines the acceptance criteria for the major components of the application.

| Feature ID | Feature Name | Acceptance Criteria |
|---|---|---|
| **AC-01** | **REST API** | 1. A `POST` request to `/api/risk` with a valid portfolio returns a `200 OK` status. <br> 2. The response body contains `total_market_value`, `var`, `market_values_per_stock`, `simulated_pl`, and `historical_performance`. <br> 3. A request with an empty or invalid portfolio returns a `400 Bad Request` status with a clear error message. |
| **AC-02** | **Interactive Dashboard** | 1. The dashboard loads at the `/dash/` URL without errors. <br> 2. Selecting stocks dynamically generates the correct number of quantity input boxes. <br> 3. Clicking "Analyze Portfolio" with a valid portfolio displays the full results section with four distinct analysis cards. <br> 4. The "Risk Concentration" card shows a pie chart. <br> 5. The "Profit/Loss Simulation" card shows a smoothed density plot. |
| **AC-03** | **Automated Report** | 1. Running the `src/automate_report.py` script executes without errors. <br> 2. The script generates a file at `reports/daily_risk_report.md`. <br> 3. The generated report is well-formatted and contains the calculated VaR and Market Value. |
