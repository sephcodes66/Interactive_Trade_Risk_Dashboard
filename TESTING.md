# RiskDash - User Acceptance Testing (UAT)

This document outlines the User Acceptance Testing (UAT) cases for the RiskDash Pre-Trade Risk Analysis Prototype. The purpose of these tests is to verify that the application meets the business requirements and functions correctly from an end-user's perspective.

## Test Cases

| Test Case ID | Test Scenario          | Action Steps                                                              | Expected Result                                                                                                                              |
|--------------|------------------------|---------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **UAT-01**   | **Minor Risk Increase**| 1. Launch the application. <br> 2. Use the default base portfolio. <br> 3. In the "Proposed Trade" section, enter Ticker: `GOOG`, Quantity: `5`. <br> 4. Click "Calculate Pre-Trade Risk". | The application calculates the New Portfolio VaR. The new VaR is slightly higher than the Current VaR, but the increase is within the 10% tolerance. A "Go!" recommendation is displayed. |
| **UAT-02**   | **Major Risk Increase**| 1. Launch the application. <br> 2. Use the default base portfolio. <br> 3. In the "Proposed Trade" section, enter Ticker: `TSLA`, Quantity: `50`. <br> 4. Click "Calculate Pre-Trade Risk". | The application calculates the New Portfolio VaR. The new VaR is significantly higher than the Current VaR, and the increase exceeds the 10% tolerance. A "No-Go!" recommendation is displayed. |
| **UAT-03**   | **Risk-Reducing Trade**| 1. Launch the application. <br> 2. Use the default base portfolio. <br> 3. In the "Proposed Trade" section, enter Ticker: `AGG`, Quantity: `100` (adding a bond ETF). <br> 4. Click "Calculate Pre-Trade Risk". | The application calculates the New Portfolio VaR. The new VaR is lower than the Current VaR. A "Go!" recommendation is displayed, indicating the trade reduces risk through diversification. |
| **UAT-04**   | **Data Visualization** | 1. Launch the application. <br> 2. Perform any calculation by clicking the "Calculate Pre-Trade Risk" button. | Two histograms are displayed under "Simulated Profit/Loss Distribution". Both charts render correctly, showing a distribution of simulated profits and losses around zero. |
| **UAT-05**   | **Invalid Ticker Input**| 1. Launch the application. <br> 2. In the "Proposed Trade" section, enter Ticker: `INVALIDTICKER`, Quantity: `10`. <br> 3. Click "Calculate Pre-Trade Risk". | The application handles the error gracefully. The metrics will likely show no change or a warning will be printed in the console/terminal. The application does not crash. The "New Portfolio" metrics will reflect a value calculated without the invalid ticker. |

---

## Acceptance Criteria for New Features

This section defines the acceptance criteria for the major features added during the project enhancement phase.

| Feature ID | Feature Name | Acceptance Criteria |
|---|---|---|
| **AC-01** | **REST API** | 1. A `POST` request to `/api/risk` with a valid JSON portfolio returns a `200 OK` status. <br> 2. The response body contains `total_market_value` and `var` as numeric values. <br> 3. A request with a missing `portfolio` key returns a `400 Bad Request` status with a clear error message. <br> 4. The API successfully handles portfolios with valid tickers that exist in the database. |
| **AC-02** | **Interactive Dashboard** | 1. The dashboard loads at the `/dash/` URL without errors. <br> 2. Entering a valid JSON portfolio into the text area and clicking "Analyze Portfolio" displays a results section. <br> 3. The results section correctly shows the Total Market Value and VaR. <br> 4. A pie chart visualizing the portfolio composition is rendered correctly. <br> 5. Entering invalid JSON and clicking the button displays a user-friendly error message. |
| **AC-03** | **Automated Report** | 1. Running the `src/automate_report.py` script executes without errors. <br> 2. The script generates a file at `reports/daily_risk_report.md`. <br> 3. The generated report is well-formatted and contains the correct placeholders for the calculated metrics (Market Value and VaR). |