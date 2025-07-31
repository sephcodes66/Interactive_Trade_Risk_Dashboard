# Project Goals: What I'm Building Here

This file is basically my personal checklist and brain-dump for what I wanted to accomplish with this RiskDash project. It started as a simple idea and grew from there.

## The Big Idea

The main goal was to build something that could answer a seemingly simple question: **"How much money could my stock portfolio lose on a bad day?"**

I knew the answer was related to the "Value at Risk" (VaR) metric, but I wanted to build a tool that made it tangible. I didn't want to just calculate a number; I wanted to see it, interact with it, and understand it.

## My Core Feature Wishlist:

*   **A Way to Build a Portfolio:** I needed a simple UI where I could pick a few stocks (like AAPL, GOOGL, etc.) and say how many shares I "owned."
*   **Calculate Historical VaR:** This was the heart of the project. The tool had to take my portfolio, look at past price movements, and calculate the 1-day 95% VaR.
*   **Visualize the Risk:** A single number is boring. I wanted charts!
    *   A pie chart to see how my portfolio was allocated.
    *   A distribution plot (a density chart) to visualize the range of potential profits and losses. This is way more intuitive than just a number.
*   **A Simple API:** I wanted the calculation engine to be separate from the UI. This way, I could theoretically use it for other things later. A simple Flask API seemed like the perfect fit.
*   **Automated Report:** I thought it would be cool to have a script that could generate a daily risk report in a simple format like Markdown.

## What I'm NOT Building (At Least Not Yet)

To keep things manageable for a first version, I decided to leave a few things out:

*   **Real-time data:** This is a prototype, so I'm using a static dataset of historical prices.
*   **Fancy risk models:** I'm sticking to Historical VaR for now. No Monte Carlo simulations or stress testing... yet.
*   **User accounts:** There's no login or way to save your portfolio. It's all in-the-moment analysis.

This project is all about learning and building a cool, practical tool. If you have ideas for how to make it better, feel free to share them!