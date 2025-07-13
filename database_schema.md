# Database Schema and Query Design

This document outlines the database schema for the RiskDash application and provides examples of the complex SQL queries that are executed by the backend. While the application now uses the SQLAlchemy ORM for maintainability, these underlying queries showcase the core data retrieval logic.

## Schema Definition (DDL)

The following `CREATE TABLE` statements define the structure of the PostgreSQL database. Indexes are created on foreign keys and frequently filtered columns to ensure query performance.

```sql
CREATE TABLE instruments (
    instrument_id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) UNIQUE NOT NULL,
    company_name VARCHAR(255)
);

CREATE TABLE market_data (
    data_id SERIAL PRIMARY KEY,
    instrument_id INTEGER REFERENCES instruments(instrument_id),
    price_date DATE NOT NULL,
    open_price NUMERIC(10, 2),
    high_price NUMERIC(10, 2),
    low_price NUMERIC(10, 2),
    close_price NUMERIC(10, 2) NOT NULL,
    volume NUMERIC,
    UNIQUE(instrument_id, price_date)
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_market_data_instrument_id ON market_data (instrument_id);
CREATE INDEX IF NOT EXISTS idx_market_data_price_date ON market_data (price_date);
```

---

## Query Design Examples

### 1. Fetching Most Recent Prices for a Portfolio

**Goal:** To calculate the current market value of a portfolio, we need the single most recent price for each stock.

**SQL Logic:** This query uses a subquery with a `MAX()` aggregate function to find the latest `price_date` for each `instrument_id`. It then joins this result back to the `market_data` and `instruments` tables to retrieve the ticker and the closing price on that specific date. This is far more efficient than running a separate query for each stock in the portfolio.

```sql
SELECT
    i.ticker,
    m.close_price
FROM
    instruments i
JOIN (
    -- This subquery finds the most recent date for each instrument.
    SELECT
        instrument_id,
        MAX(price_date) as max_date
    FROM
        market_data
    GROUP BY
        instrument_id
) latest ON i.instrument_id = latest.instrument_id
JOIN
    market_data m ON latest.instrument_id = m.instrument_id AND latest.max_date = m.price_date
WHERE
    i.ticker IN ('AAPL', 'MSFT', 'GOOG'); -- Example tickers
```

### 2. Fetching Historical Time Series Data

**Goal:** To calculate historical VaR, we need the last 'N' days of price data for each stock in the portfolio.

**SQL Logic:** This query uses a Common Table Expression (CTE) with the `ROW_NUMBER()` window function. The window function partitions the data by ticker and orders it by date descending, assigning a rank (`rn`) to each row. The outer query then simply selects the rows where the rank is less than or equal to the desired number of days (e.g., 252). This approach is highly efficient for retrieving top-N records per group.

```sql
WITH ranked_prices AS (
    -- This CTE assigns a rank to each day's price for every stock.
    SELECT
        i.ticker,
        m.price_date,
        m.close_price,
        ROW_NUMBER() OVER(PARTITION BY i.ticker ORDER BY m.price_date DESC) as rn
    FROM
        instruments i
    JOIN
        market_data m ON i.instrument_id = m.instrument_id
    WHERE
        i.ticker IN ('AAPL', 'MSFT', 'GOOG') -- Example tickers
)
SELECT
    ticker,
    price_date,
    close_price
FROM
    ranked_prices
WHERE
    rn <= 252 -- Fetch the last 252 trading days
ORDER BY
    price_date ASC;
```
