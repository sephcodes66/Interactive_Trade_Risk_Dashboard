# Project Plan: RITA Pre-Trade Risk Prototype

This plan outlines the development of a functional prototype for a Real-time Interactive Trading and Analytics (RITA) system. The goal is to create a focused application that showcases skills in Python, PostgreSQL, data analysis, data visualization, and testing methodologies.

## Phase 1: Data Sourcing & Database Setup

**Objective:** Establish the project's data foundation.

### 1.1. Download Dataset
*   **Dataset:** Daily Prices of Major US Stocks
*   **Source:** Kaggle (https://www.kaggle.com/datasets/meetnagadia/daily-prices-of-major-us-stocks)
*   **Action:** The dataset is already available in the `data/` directory.

### 1.2. Setup PostgreSQL Database
*   **Tool:** PostgreSQL
*   **Action:** Create a new database named `rita_risk_db`. Connect to it and execute the following SQL to create the necessary tables:
    ```sql
    CREATE TABLE instruments (
        instrument_id SERIAL PRIMARY KEY,
        ticker VARCHAR(10) UNIQUE NOT NULL,
        company_name VARCHAR(255)
    );

    CREATE TABLE market_data (
        data_id SERIAL PRIMARY KEY,
        instrument_id INTEGER REFERENCES instruments(instrument_id),
        price_date DATE NOT NULL,
        close_price NUMERIC(10, 2) NOT NULL
    );
    ```

### 1.3. Ingest Data into PostgreSQL
*   **Tools:** Python, pandas, psycopg2 (or SQLAlchemy)
*   **Action:** Create a script (`ingest_data.py`) to:
    1.  Read `stock_prices.csv` into a pandas DataFrame.
    2.  Extract unique tickers and populate the `instruments` table.
    3.  Map the price data to the correct `instrument_id` and bulk-insert it into the `market_data` table.

## Phase 2: Backend Risk Engine

**Objective:** Build the core analytical logic of the application.

### 2.1. Establish Database Connection Module
*   **Tools:** Python, psycopg2 or SQLAlchemy
*   **Action:** Create a module (`db_connector.py`) to manage the database connection details and provide a reusable connection object.

### 2.2. Build the Portfolio Manager
*   **Tool:** Python
*   **Action:** Create a class (`PortfolioManager`) in a `portfolio.py` file. This class will manage a simulated portfolio (e.g., initialized with a dictionary like `{'AAPL': 50, 'MSFT': 30}`) and calculate its total market value by fetching current prices from the database.

### 2.3. Implement the VaR Risk Model
*   **Tools:** Python, pandas, numpy
*   **Action:** Create a class (`RiskEngine`) in a `risk_engine.py` file. Implement a method to calculate historical Value at Risk (VaR):
    1.  The method accepts a portfolio dictionary as input.
    2.  It queries the last 252 days of price data for the relevant tickers from `market_data`.
    3.  It uses pandas to calculate daily percentage returns.
    4.  It applies these historical returns to the input portfolio's current value to simulate daily Profit/Loss (P/L).
    5.  It uses numpy's percentile function to find the 5th percentile of the P/L distribution, which represents the 95% VaR.

## Phase 3: Interactive Frontend & Visualization

**Objective:** Create a user-friendly interface and showcase data visualization skills.

### 3.1. Setup the Web Application
*   **Tool:** Streamlit
*   **Action:** Create the main application file, `app.py`. Install Streamlit (`pip install streamlit`).

### 3.2. Build the UI Components
*   **Tool:** Streamlit
*   **Action:** In `app.py`, use Streamlit's simple components to build the interface:
    1.  `st.title("RITA - Pre-Trade Risk Analysis Prototype")`
    2.  `st.sidebar` to create a section for user input.
    3.  `st.sidebar.text_input("Ticker")` and `st.sidebar.number_input("Quantity")` for the proposed trade.
    4.  `st.sidebar.button("Calculate Pre-Trade Risk")` to trigger the analysis.

### 3.3. Add Data Visualization
*   **Tools:** Streamlit, Plotly Express
*   **Action:** Create a function that generates a histogram of the simulated P/L array from your VaR calculation. Use Plotly Express for this (`pip install plotly`). Display the chart in the main app area using `st.plotly_chart()` to visually represent the portfolio's risk distribution.

## Phase 4: Integration & Finalization

**Objective:** Connect the frontend and backend to deliver the core RITA feature.

### 4.1. Connect Frontend to Backend Logic
*   **Tools:** Python, Streamlit, your custom classes
*   **Action:** In `app.py`, implement the logic that runs when the "Calculate" button is clicked:
    1.  Instantiate your `PortfolioManager` and `RiskEngine`.
    2.  Calculate the **Current VaR** of the base portfolio.
    3.  Create a hypothetical portfolio that includes the proposed trade.
    4.  Calculate the **New VaR** for this hypothetical portfolio.

### 4.2. Display Analysis Results
*   **Tool:** Streamlit
*   **Action:** Use `st.metric` to clearly display the results:
    *   `st.metric("Current Portfolio VaR", f"{current_var:,.2f}")`
    *   `st.metric("New Portfolio VaR", f"{new_var:,.2f}", delta=f"{new_var - current_var:,.2f}")`
    *   Add a clear "Go / No-Go" recommendation based on whether the New VaR breaches a predefined risk limit (e.g., a 10% increase from the current VaR).

## Phase 5: User Acceptance Testing (UAT) Documentation

**Objective:** Formally document the testing process to showcase QA and UAT skills.

### 5.1. Create a Test Plan Document
*   **Tool:** Markdown
*   **Action:** Create a `TESTING.md` file in the root of your project.

### 5.2. Define Test Cases & Acceptance Criteria
*   **Tool:** Markdown
*   **Action:** In `TESTING.md`, create a table defining key UAT test cases.
