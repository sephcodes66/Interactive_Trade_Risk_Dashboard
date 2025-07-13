# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2025-07-13

### Added
- **Interactive Portfolio Builder:** Replaced the JSON text input with a dynamic, searchable dropdown for selecting stocks and individual quantity inputs, significantly improving usability.
- **Enhanced Visualizations:** Added two new charts to the dashboard: a historical portfolio performance line chart and a P&L simulation density plot.
- **Explanatory UI Text:** Added titles and descriptive text to all dashboard components to clarify the meaning of each risk management feature.
- **ORM Layer:** Refactored the entire data access layer to use the SQLAlchemy ORM, replacing raw SQL queries with maintainable Python objects.
- **Project Documentation:** Created `BUSINESS_REQUIREMENTS.md` and `TESTING.md` to formalize project goals and quality assurance processes.

### Changed
- **Project Renaming:** Renamed the project from "RITA" to "RiskDash" across all files and documentation.
- **Upgraded P/L Chart:** Replaced the P/L simulation histogram with a smoother, more intuitive Kernel Density Estimate (KDE) plot.
- **Improved Chart Scaling:** Fixed scaling and formatting issues on all charts to ensure currency values are displayed clearly.
- **Sticky Layout:** Made the input panel sticky so it remains visible while scrolling through results.

### Fixed
- **Critical Data Serialization Bug:** Resolved a recurring `500 Internal Server Error` by ensuring all data from the backend API is converted to JSON-safe types before being sent to the dashboard. This involved handling special numeric types from NumPy/Pandas and ensuring all dictionary keys were strings.
- **Dashboard Callback Errors:** Made the dashboard's rendering logic more robust to handle cases where the API returns null or incomplete data, preventing the UI from crashing.
- **Test Suite Regressions:** Fixed multiple bugs in the `pytest` suite that were introduced during major refactoring, bringing test coverage back to 100%.
- **Corrected VaR Calculation:** Fixed a logical error in the `RiskEngine` to ensure portfolio returns were correctly weighted by asset value before calculating VaR.
