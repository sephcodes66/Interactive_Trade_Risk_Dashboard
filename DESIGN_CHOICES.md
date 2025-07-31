# Dev Notes: Why I Built It This Way

This document is basically my developer journal. It's where I'm jotting down the "why" behind some of the technical decisions I made while building RiskDash. Hope it gives you some context!

## 1. Monolith vs. Microservices: Why a Single `app.py`?

When I started this, I was tempted to go all-in with a "proper" microservices architecture. But then I took a step back and asked myself: "Do I really need that?" For this prototype, the answer was a clear "no."

**My Rationale:**
*   **Keep It Simple, Stupid (KISS):** For a small app like this, managing a single `app.py` is just so much easier. No wrestling with Docker Compose or figuring out inter-service communication. I wanted to build a risk tool, not a distributed systems masterpiece.
*   **Speed:** My goal was to get a working prototype up and running fast. Sticking everything in one place let me focus on the fun stuff (the risk calculations and the UI) instead of getting bogged down in infrastructure.
*   **Simulating a Real-World Setup:** The Dash app makes a call to its own Flask server. I know, it feels a bit like a network call to yourself, but it's a clean way to separate the UI from the backend logic. It also means that if I ever *do* want to split them, the frontend code is already set up to call an API.

**If This Were a "Real" Project:**
If this project were to grow into something bigger, I'd absolutely split them. The Flask API would become its own service, and the Dash app (or maybe a React/Vue frontend) would be another. That way, they could be scaled, developed, and deployed independently. But for now, one file is plenty.

## 2. The Database Query Dilemma: An Honest Look at a "Good Enough" Solution

When you're fetching data, there's always a tension between writing code that's easy to understand and code that's lightning-fast. I hit this problem head-on.

**The `get_current_prices` Method:**
My first version of this function was super simple: loop through each stock ticker and make a separate database call to get its latest price. It worked, it was easy to read, but it was also a classic example of the "N+1 query problem" – very inefficient.

I did refactor it later to use a much faster single-query approach with a SQL subquery. But for this "human-built" version of the project, I actually decided to revert to the simpler, iterative approach. Why? Because it's a perfect example of a "good enough" solution that a real developer might write when they're focused on getting a feature out the door. It's a trade-off, and sometimes readability wins.

**The `get_historical_data` Method:**
For this function, I went the other way. I used a more advanced SQL window function (`row_number()`) to grab the last N days of data for all tickers in one shot. This was a conscious optimization. Fetching a year of daily prices for a dozen stocks can be slow, and I didn't want the dashboard to feel sluggish.

## 3. Dealing with Messy Data: `ffill` to the Rescue

In `src/risk_engine.py`, I used the pandas `ffill()` (forward-fill) method to handle gaps in the historical stock data.

**Why `ffill`?**
*   Real-world financial data is messy. You get gaps for weekends, holidays, or just weird data issues.
*   `ffill` is a simple, pragmatic way to handle it. It just assumes that if a price is missing, the price from the previous day is the best guess.
*   It's way better than just dropping the missing days, which would mess up the time series and ruin the VaR calculation.

Is it the most scientifically rigorous method? Probably not. An academic paper might call for linear interpolation or some other fancy statistical technique. But for a practical tool like this, `ffill` is a solid, battle-tested choice. It gets the job done.