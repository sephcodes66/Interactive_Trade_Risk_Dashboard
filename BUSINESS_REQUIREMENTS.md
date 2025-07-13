# Business Requirements: RiskDash (An Interactive Risk Analysis Tool)

## 1. Introduction

This document outlines the high-level business requirements for the RiskDash system. The primary goal of RiskDash is to provide a modern, efficient, and accessible platform for the Group Risk Management team to analyze portfolio risk, visualize data, and automate reporting.

## 2. Project Goals & Objectives

- **Improve Efficiency:** Reduce the manual effort required to perform daily risk calculations and generate reports.
- **Enhance Accessibility:** Provide a user-friendly web interface for risk analysis, making it accessible to non-technical users.
- **Standardize Risk Calculation:** Implement a consistent and verifiable method for calculating historical Value at Risk (VaR).
- **Provide Actionable Insights:** Offer clear visualizations of portfolio composition and risk exposure.
- **Enable System Integration:** Create an API to allow other internal systems to leverage the risk engine's capabilities.

## 3. Scope

### 3.1. In-Scope Features

- **Core Risk Calculation:** A risk engine capable of calculating 1-day historical VaR at a 95% confidence level.
- **Portfolio Management:** Ability to define and analyze a portfolio of stocks.
- **Data Ingestion:** Process historical stock price data from a provided data source.
- **API:** A RESTful API that accepts a portfolio and returns key risk metrics.
- **Interactive Dashboard:** A web-based dashboard to:
    - Input a portfolio.
    - Display calculated risk metrics (VaR, Market Value).
    - Visualize portfolio composition.
- **Automated Reporting:** A script to automatically generate a daily summary risk report for a predefined portfolio.

### 3.2. Out-of-Scope Features (for this version)

- Real-time data feeds.
- Advanced risk models (e.g., Monte Carlo VaR, Stress Testing).
- User authentication and management.
- Saving and managing multiple portfolios per user.
- Direct integration with external data providers.

## 4. Functional Requirements

| ID | Requirement | Description |
|---|---|---|
| **FR-01** | Calculate Historical VaR | The system must calculate the 1-day, 95% confidence historical VaR for a given stock portfolio. |
| **FR-02** | Calculate Market Value | The system must calculate the total current market value of a given portfolio. |
| **FR-03** | API Access | The system must expose an API endpoint that takes a portfolio definition and returns the VaR and market value. |
| **FR-04** | Interactive Dashboard | The user shall be able to input a portfolio into a web dashboard and view the calculated risk metrics and a portfolio composition chart. |
| **FR-05** | Automated Report | The system must be able to generate a daily risk report in Markdown format for a predefined sample portfolio. |

