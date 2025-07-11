import streamlit as st
import plotly.express as px
import pandas as pd
from portfolio import PortfolioManager
from risk_engine import RiskEngine

def plot_pl_histogram(pl_array, title):
    """Generates and displays a histogram of the Profit/Loss distribution."""
    if pl_array is None or pl_array.size == 0:
        st.write(f"No data available to plot for {title}.")
        return
        
    fig = px.histogram(
        pd.DataFrame({'P/L': pl_array}), 
        x='P/L', 
        title=title,
        labels={'P/L': 'Profit/Loss ($)'},
        nbins=50
    )
    fig.update_layout(
        xaxis_title="Simulated 1-Day Profit/Loss ($)",
        yaxis_title="Frequency",
        title_x=0.5
    )
    st.plotly_chart(fig, use_container_width=True)

def main():
    """
    Main function to run the Streamlit application.
    """
    st.set_page_config(layout="wide")
    html.H1(children='Interactive_Trade_Risk_Dashboard'),

    html.Div(children='''
        An Interactive Trade and Risk Dashboard
    '''),

    # --- Sidebar for User Input ---
    st.sidebar.header("Portfolio & Trade Input")

    # Define a larger, more diverse base portfolio of 10 assets
    base_portfolio = {
        'AAPL': 50, 
        'MSFT': 40,
        'AMZN': 10,
        'TSLA': 15,
        'JPM': 100,
        'V': 80,
        'PFE': 200,
        'DIS': 60,
        'ACN': 70, # Accenture
        'AGG': 150 # iShares Core U.S. Aggregate Bond ETF
    }
    
    st.sidebar.subheader("Current Portfolio")
    st.sidebar.json(base_portfolio)

    st.sidebar.subheader("Proposed Trade")
    trade_ticker = st.sidebar.text_input("Ticker", "MSFT").upper()
    trade_quantity = st.sidebar.number_input("Quantity", value=20, step=1)

    calculate_button = st.sidebar.button("Calculate Pre-Trade Risk")

    # --- Main Area for Results ---
    st.header("Risk Analysis Results")

    if calculate_button:
        # --- Calculations ---
        # 1. Analyze the base portfolio
        pm_base = PortfolioManager(base_portfolio)
        risk_engine_base = RiskEngine(pm_base)
        current_var, pl_base = risk_engine_base.calculate_historical_var()
        current_value = pm_base.calculate_total_market_value()

        # 2. Create and analyze the hypothetical new portfolio
        new_portfolio = base_portfolio.copy()
        new_portfolio[trade_ticker] = new_portfolio.get(trade_ticker, 0) + trade_quantity
        
        pm_new = PortfolioManager(new_portfolio)
        risk_engine_new = RiskEngine(pm_new)
        new_var, pl_new = risk_engine_new.calculate_historical_var()
        new_value = pm_new.calculate_total_market_value()

        # --- Display Results ---
        st.subheader("Portfolio Value")
        col1, col2 = st.columns(2)
        col1.metric("Current Portfolio Value", f"${current_value:,.2f}")
        col2.metric("New Portfolio Value", f"${new_value:,.2f}", delta=f"${new_value - current_value:,.2f}")

        st.subheader("Value at Risk (VaR) - 95% Confidence, 1-Day")
        col1, col2 = st.columns(2)
        col1.metric("Current Portfolio VaR", f"${current_var:,.2f}")
        col2.metric("New Portfolio VaR", f"${new_var:,.2f}", delta=f"${new_var - current_var:,.2f}")
        
        # 4. Go/No-Go Recommendation
        st.subheader("Recommendation")
        var_increase_pct = ((new_var - current_var) / current_var) * 100 if current_var > 0 else 0
        risk_limit = 10.0

        if new_var < current_var:
            st.success("**Go!** The proposed trade reduces the portfolio's VaR.")
        elif var_increase_pct <= risk_limit:
            st.success(f"**Go!** The proposed trade increases VaR by {var_increase_pct:.2f}%, which is within the {risk_limit:.0f}% tolerance.")
        else:
            st.error(f"**No-Go!** The proposed trade increases VaR by {var_increase_pct:.2f}%, which exceeds the {risk_limit:.0f}% tolerance.")

        # --- Data Visualization ---
        st.subheader("Simulated Profit/Loss Distribution")
        col1, col2 = st.columns(2)
        with col1:
            plot_pl_histogram(pl_base, "Current Portfolio P/L Distribution")
        with col2:
            plot_pl_histogram(pl_new, "New Portfolio P/L Distribution")

if __name__ == "__main__":
    main()
