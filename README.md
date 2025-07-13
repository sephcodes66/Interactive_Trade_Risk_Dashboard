# RiskDash: An Interactive Risk Analysis Tool

RiskDash is a prototype of a financial risk management system. It provides a suite of tools to help risk analysts and portfolio managers assess the market risk of equity portfolios using **Value at Risk (VaR)**.

This enhanced version of the project demonstrates a full-stack data application with a clear separation of concerns, featuring a backend API, an interactive web dashboard, and an automated reporting script.

## Table of Contents
- [System Architecture](#system-architecture)
- [Features](#features)
- [How to Use RiskDash](#how-to-use-riskdash)
  - [1. The REST API](#1-the-rest-api)
  - [2. The Interactive Dashboard](#2-the-interactive-dashboard)
  - [3. Automated Daily Reporting](#3-automated-daily-reporting)
- [Setup and Installation](#setup-and-installation)
- [Code Quality: Linting and Testing](#code-quality-linting-and-testing)

## System Architecture

The application is now composed of several decoupled components:

1.  **Data Ingestion Pipeline (`ingest_data.py`):** A script that sources historical stock price data from CSV files and loads it into a PostgreSQL database.
2.  **PostgreSQL Database:** Stores clean `instruments` and `market_data` information.
3.  **Backend Risk Engine (`portfolio.py`, `risk_engine.py`):** The core Python logic for managing portfolios and calculating historical VaR.
4.  **Flask REST API (`app.py`):** A robust API built with **Flask** that exposes the risk engine's functionality over HTTP, making it available to any client.
5.  **Interactive Dashboard (`app.py`):** A web application built with **Dash** and **Plotly**. It acts as a client to the Flask API to provide an interactive user interface for risk analysis.
6.  **Automation Script (`automate_report.py`):** A standalone script for generating scheduled, automated risk reports.


## Features

* **Decoupled API-First Design:** Core logic is exposed via a REST API for system integration.
* **Interactive Web Dashboard:** A user-friendly interface for ad-hoc risk analysis and visualization.
* **Automated Reporting:** Scriptable, automated generation of daily risk reports.
* **Historical VaR Calculation:** Implements the industry-standard historical simulation method for VaR.
* **Rich Data Visualization:** Includes interactive pie charts of portfolio composition.
* **Quality Assured:** The codebase includes a comprehensive suite of unit tests (`pytest`) and is formatted with a linter (`ruff`).

## How to Use RiskDash

There are three primary ways to use the RiskDash prototype.

### 1. The REST API

The Flask API is the core of the system. You can interact with it directly to get programmatic access to the risk engine.

**To run the API server:**
```bash
flask run
```
The API will be available at `http://127.0.0.1:5000`.

**Endpoint:** `POST /api/risk`

This endpoint accepts a JSON payload with a portfolio and returns the calculated risk metrics.

**Example Request (`curl`):**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"portfolio": {"AAPL": 10, "MSFT": 20, "TSLA": 5}}' \
  http://127.0.0.1:5000/api/risk
```

**Example Success Response:**
```json
{
  "market_values_per_stock": {
    "AAPL": 2143.5,
    "MSFT": 5930.2,
    "TSLA": 893.5
  },
  "total_market_value": 8967.2,
  "var": 253.81
}
```

### 2. The Interactive Dashboard

The dashboard provides a user-friendly, graphical interface for the API.

**To run the dashboard:**
```bash
python src.app
```
The dashboard will be available at `http://127.0.0.1:8050/dash/`.

**How to use it:**
1.  Select one or more stocks from the searchable dropdown.
2.  Enter the quantity for each selected stock.
3.  Click the "Analyze Portfolio" button.
4.  The dashboard will call the API and display the risk analysis, including the VaR, a risk concentration pie chart, and a smoothed density plot of potential profit and loss outcomes.

![Dashboard Screenshot](./screenshots/ss_1.png)

### 3. Automated Daily Reporting

The automation script generates a daily risk report for a pre-defined sample portfolio.

**To run the script:**
```bash
python -m src.automate_report
```

This will create a Markdown file at `reports/daily_risk_report.md` containing a summary of the analysis. This script can be scheduled to run automatically using tools like `cron`.

## Setup and Installation

### Prerequisites
* Python 3.9+
* PostgreSQL server running

### Steps
1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the database:**
    * Connect to PostgreSQL and create a new database (e.g., `risk_dash_db`).
    * Create a `.env` file in the project root by copying the example: `cp .env.example .env`.
    * Edit the `.env` file with your database credentials.

5.  **Run the data ingestion script:**
    This will populate your database with the required historical data.
    ```bash
    python src/ingest_data.py
    ```

## Code Quality: Linting and Testing

*   **To run the linter (Ruff):**
    ```bash
    ruff check .
    ```
*   **To run the unit tests (Pytest):**
    ```bash
    pytest
    ```
