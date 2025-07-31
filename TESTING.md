# How I Approached Testing

Testing for a project like this is a mix of automated checks and just playing around with the UI to make sure it feels right. Here's a quick rundown of how I made sure RiskDash wasn't completely broken.

## Backend Unit Tests (`pytest`)

The most critical part of this project is the risk calculation engine. If that's wrong, the whole thing is useless. So, I spent most of my "formal" testing time here.

I used `pytest` to write unit tests for the core backend logic:
*   **`test_risk_engine.py`:** This is the big one. I wrote tests to make sure the VaR calculation was correct for a simple, predictable dataset. I also tested the profit/loss simulation logic.
*   **`test_portfolio.py`:** These tests check the `Portfolio` class. I wanted to make sure it correctly calculated market values and handled different portfolio compositions.
*   **`test_api.py`:** I wrote a few tests to check the Flask API endpoints. These tests make sure the API returns the right data structure and handles bad inputs gracefully (e.g., sending a request with no stocks).

To run them, just fire up `pytest` in the terminal.

## "Eyeball" Testing the Dashboard

For the frontend, my testing was much more informal. I basically just tried to break it. Here are some of the scenarios I ran through manually:

*   **The "Does it even work?" Test:**
    1.  Pick a few stocks (usually `AAPL`, `MSFT`, `TSLA`).
    2.  Enter some quantities.
    3.  Click "Analyze Portfolio."
    4.  Expected: The dashboard updates and shows me some numbers and charts. Success!

*   **The "What if I change my mind?" Test:**
    1.  Analyze a portfolio.
    2.  Remove a stock from the dropdown.
    3.  Click "Analyze" again.
    4.  Expected: The dashboard updates correctly, showing the analysis for the new, smaller portfolio.

*   **The "Fat Finger" Test (Invalid Inputs):**
    1.  Select a stock but don't enter a quantity.
    2.  Click "Analyze."
    3.  Expected: I should see a friendly error message, not a scary crash.

*   **The "Weird Stock" Test:**
    1.  Pick a less common stock that might have spotty data.
    2.  Analyze it.
    3.  Expected: The app should handle it gracefully. Maybe a chart won't load, but the rest of the app should still work.

This manual approach felt right for a small project. It's quick, intuitive, and helps me get a feel for the user experience in a way that automated tests can't.

## Known Gaps

I know my testing isn't exhaustive. For example, I haven't done any serious performance testing with huge portfolios. But for a prototype, I'm confident that the core logic is solid and the UI is reasonably stable.