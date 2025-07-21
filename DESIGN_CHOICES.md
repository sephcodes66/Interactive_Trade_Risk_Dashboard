# Design Choices and Development Notes

This document provides some insight into why certain architectural and design decisions were made during the development of RiskDash. It's meant to feel like a developer's journal, capturing the thought process behind the code.

## 1. Monolith vs. Microservices: Why a Single `app.py`?

For this prototype, I decided to keep the Flask API server and the Dash UI application in the same file (`src/app.py`).

**The Rationale:**
*   **Simplicity:** For a small-scale application, managing a single process is far simpler. There's no need for complex inter-service communication, separate deployments, or managing multiple environments.
*   **Rapid Prototyping:** The goal was to build a functional prototype quickly. Keeping everything together allowed me to focus on the core features (risk calculations, UI interactivity) without getting bogged down in infrastructure.
*   **Shared Context:** The Dash app makes a call to its own Flask server. While this feels a bit like a network call to yourself, it cleanly separates the UI from the calculation logic. It also mimics how a real, decoupled frontend would work.

**Future Considerations:**
If this project were to grow, I would absolutely split them. The Flask API would become its own microservice, and the Dash app (or a React/Vue frontend) would be a separate service. This would allow them to be scaled, developed, and deployed independently.

## 2. The Database Query Dilemma: Iteration vs. Optimization

When fetching data, there's often a trade-off between code that is easy to write/understand and code that is highly performant.

**The `get_current_prices` Method:**
The first version of this function was written to be simple: loop through each ticker and make a database call to get its latest price. It's clean, easy to follow, but very inefficient (the N+1 query problem).

I later refactored this to use a more complex, but much faster, single-query approach using a SQL subquery. However, for this "human-built" version of the project, I've reverted to the iterative approach to better reflect a common development journey. It's a good example of a "good enough" solution that a developer might write under time pressure.

**The `get_historical_data` Method:**
This function uses a more advanced window function (`row_number()`) to get the last N days of data for all tickers in one go. This was a conscious decision to optimize what could be a very heavy query, as fetching a year of data for dozens of stocks could otherwise be very slow.

## 3. Data Handling: `ffill` for Missing Data

In `src/risk_engine.py`, I used `ffill()` (forward-fill) to handle gaps in the historical data.

**Why?**
*   Financial data often has gaps, especially for weekends and holidays.
*   `ffill` is a simple and standard way to address this. It assumes the price from the previous day is the best estimate for the missing day.
*   It's much better than just dropping the dates, which would distort the time series.

This is a pragmatic choice. A more rigorous, academic model might use linear interpolation or another statistical method, but `ffill` is a solid, practical choice for a production-oriented prototype.
