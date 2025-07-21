# RiskDash: An Interactive Risk Analysis Tool

> **Note:** This project was built as a collaborative effort between a human and an AI assistant for educational and demonstrative purposes.

I built this project to create a simple, hands-on prototype of a financial risk management system. The goal was to provide an interactive web dashboard to help assess the market risk of equity portfolios using the industry-standard **Value at Risk (VaR)** metric.

For a deeper dive into the "why" behind some of the technical decisions, check out the [[DESIGN_CHOICES.md]] file.

![Dashboard Screenshot](./screenshots/ss_1.png)

## Key Features

*   **Interactive Portfolio Builder:** Lets you construct a portfolio by selecting stocks and specifying quantities.
*   **Value at Risk (VaR) Calculation:** Calculates the 1-day 95% VaR using the Historical Simulation method.
*   **Risk Concentration Analysis:** A pie chart visualizes asset allocation.
*   **Profit/Loss Simulation:** A density plot shows the distribution of potential daily profit and loss.
*   **Backend:** I used a Flask API with a PostgreSQL database and the SQLAlchemy ORM.
*   **Testing:** The backend logic is verified with a suite of `pytest` unit tests.

## Setup and Installation

### Prerequisites
*   Python 3.9+
*   A running PostgreSQL server

### Steps

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/sephcodes66/Interactive_Trade_Risk_Dashboard.git
    cd Interactive_Trade_Risk_Dashboard
    ```

2.  **Set up a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    pip install -e .
    ```

4.  **Configure the database:**
    *   Create a new PostgreSQL database (e.g., `risk_dash_db`).
    *   Copy `.env.example` to `.env` and fill in your database credentials.

5.  **Load the data:**
    This script creates the tables and populates them with the sample data.
    ```bash
    python ingest_data.py
    ```

## How to Run

### Interactive Dashboard

To get the main web application running, execute the following from the project root:
```bash
python -m src.app
```
The dashboard should then be available at **http://127.0.0.1:8050/dash/**.

### Automated Report

You can also generate a sample risk report in Markdown format:
```bash
python automate_report.py
```
This will create a file in the `reports/` directory.

### Running Tests

To run the full suite of unit tests:
```bash
pytest
```
