import json
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from flask import Flask, request, jsonify
from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL

from src.portfolio import PortfolioManager
from src.risk_engine import RiskEngine
from src.models import get_all_tickers

# TODO: Maybe split this into two files later? One for the Flask API and one for the Dash app.
# For now, keeping it simple.
server = Flask(__name__)

@server.route('/api/risk', methods=['POST'])
def calculate_risk():
    """API endpoint to calculate risk for a given portfolio."""
    data = request.get_json()
    
    # Basic input validation
    if not data or 'portfolio' not in data or not data['portfolio']:
        return jsonify({"error": "Portfolio data is missing or empty."}), 400

    try:
        portfolio_dict = data['portfolio']
        
        # Let's see what we're getting from the frontend
        # print("Received portfolio for analysis:", portfolio_dict)

        pm = PortfolioManager(portfolio_dict)
        risk_engine = RiskEngine(pm)
        
        total_value = pm.calculate_total_market_value()
        if total_value == 0:
             return jsonify({"error": "Could not find market data for any of the selected tickers."}), 400

        var_value, simulated_pl = risk_engine.calculate_historical_var()
        
        # Let's build the response. If something is None or NaN, we'll just pass it as null.
        response_data = {
            "total_market_value": float(total_value),
            "var": float(var_value) if var_value is not None and not np.isnan(var_value) else None,
            "market_values_per_stock": {str(k): float(v) for k, v in pm.market_values.items()},
            "simulated_pl": [float(x) for x in simulated_pl]
        }

        return jsonify(response_data)

    except Exception as e:
        # Catch-all for any other unexpected errors.
        # This is better than letting it crash and show a generic server error.
        return jsonify({"error": f"An unexpected error occurred: {e}"}), 500

# --- DASH APP ---
# We're running the Dash app on top of our Flask server.
app = Dash(__name__, server=server, url_base_pathname='/dash/')
all_tickers = get_all_tickers()

app.layout = html.Div(style={'backgroundColor': '#f0f2f5', 'fontFamily': 'Arial'}, children=[
    html.Div(style={'backgroundColor': 'white', 'padding': '10px 20px', 'borderBottom': '1px solid #ddd'}, children=[
        html.H1("RiskDash: An Interactive Risk Analysis Tool", style={'textAlign': 'center', 'color': '#1a3d6d'})
    ]),
    
    html.Div(style={'display': 'flex', 'padding': '20px'}, children=[
        # Left-side control panel
        html.Div(style={'flex': '30%', 'padding': '10px', 'position': 'sticky', 'top': '20px', 'alignSelf': 'flex-start'}, children=[
            html.Div(style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px'}, children=[
                html.H4("Build Your Portfolio", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}),
                html.Label("Select stocks to include:"),
                dcc.Dropdown(
                    id='ticker-selector',
                    options=[{'label': t, 'value': t} for t in all_tickers],
                    multi=True,
                    placeholder="Search and select tickers..."
                ),
                html.Div(id='quantity-inputs', style={'marginTop': '20px'}),
                html.Div(style={'display': 'flex', 'marginTop': '20px'}, children=[
                    html.Button('Analyze Portfolio', id='analyze-button', n_clicks=0, style={'flex': '60%', 'backgroundColor': '#1a3d6d', 'color': 'white', 'border': 'none', 'padding': '10px', 'cursor': 'pointer'}),
                    html.Button('Clear', id='clear-button', n_clicks=0, style={'flex': '40%', 'marginLeft': '10px', 'backgroundColor': '#6c757d', 'color': 'white', 'border': 'none', 'padding': '10px', 'cursor': 'pointer'})
                ])
            ])
        ]),
        
        # Right-side analysis output
        html.Div(style={'flex': '70%', 'padding': '10px'}, children=[
            dcc.Loading(id="loading-icon", children=[html.Div(id='analysis-output')], type="default")
        ])
    ])
])

@app.callback(
    Output('quantity-inputs', 'children'),
    Input('ticker-selector', 'value')
)
def generate_quantity_inputs(selected_tickers):
    """Creates the quantity input boxes when a user selects tickers."""
    if not selected_tickers:
        return []
    
    # A bit of a list comprehension to generate the inputs dynamically.
    return [
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}, children=[
            html.Label(f"{ticker}:", style={'flex': '30%'}),
            dcc.Input(
                id={'type': 'quantity-input', 'index': ticker},
                type='number',
                placeholder='Enter quantity...',
                min=0,
                style={'flex': '70%'}
            )
        ]) for ticker in selected_tickers
    ]

@app.callback(
    Output('ticker-selector', 'value'),
    Output('quantity-inputs', 'children', allow_duplicate=True),
    Output('analysis-output', 'children', allow_duplicate=True),
    Input('clear-button', 'n_clicks'),
    prevent_initial_call=True
)
def clear_inputs(n_clicks):
    """Clears all inputs when the 'Clear' button is clicked."""
    return None, [], None

@app.callback(
    Output('analysis-output', 'children'),
    Input('analyze-button', 'n_clicks'),
    State('ticker-selector', 'value'),
    State({'type': 'quantity-input', 'index': ALL}, 'id'),
    State({'type': 'quantity-input', 'index': ALL}, 'value'),
    prevent_initial_call=True
)
def update_dashboard(n_clicks, selected_tickers, input_ids, input_values):
    """The main callback that fires when the 'Analyze' button is clicked."""
    if not selected_tickers or not any(input_values):
        return html.Div("Please select some stocks and enter quantities.", style={'color': 'red'})

    # This feels a bit clunky, but it's how Dash gets data from dynamic inputs.
    portfolio = {
        p_id['index']: p_val
        for p_id, p_val in zip(input_ids, input_values)
        if p_val is not None and p_val > 0
    }

    if not portfolio:
        return html.Div("Please enter a quantity for at least one stock.", style={'color': 'red'})

    # The Dash app calls its own underlying Flask server.
    # This is a bit weird, but it cleanly separates the UI from the API.
    api_url = f"{request.host_url.strip('/')}/api/risk"
    try:
        response = requests.post(api_url, json={'portfolio': portfolio}, timeout=30)
        response.raise_for_status()  # Raises an exception for bad status codes (4xx or 5xx)
        data = response.json()
    except requests.exceptions.RequestException as e:
        return html.Div(f"Error connecting to the backend API: {e}", style={'color': 'red'})

    if 'error' in data:
        return html.Div(f"API Error: {data['error']}", style={'color': 'red'})

    # A little config to make the graphs cleaner
    graph_config = {
        'scrollZoom': False,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
    }
    
    # --- Build the results section ---
    
    # 1. Key Metrics
    summary_children = [html.H4("1. Key Risk Metrics", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'})]
    if data.get("total_market_value") is not None:
        summary_children.append(html.P(f"Total Portfolio Market Value: ${data['total_market_value']:,.2f}"))
    if data.get("var") is not None:
        var_value = data['var']
        summary_children.append(html.H5(f"Value at Risk (95%, 1-day): ${var_value:,.2f}", style={'color': '#c0392b'}))
        summary_children.append(html.P("This is the estimated maximum loss the portfolio could experience in a single day, with 95% confidence.", style={'fontSize': '0.9em', 'fontStyle': 'italic'}))
    
    # 2. Risk Concentration Pie Chart
    if data.get("market_values_per_stock"):
        summary_children.append(html.H4("2. Risk Concentration", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px', 'marginTop': '20px'}))
        summary_children.append(html.P("This chart shows where your portfolio's value is concentrated.", style={'fontSize': '0.9em'}))
        summary_children.append(dcc.Graph(
            figure=px.pie(
                pd.DataFrame(list(data['market_values_per_stock'].items()), columns=['Ticker', 'Market Value']),
                values='Market Value', names='Ticker', title='Portfolio Composition by Market Value'
            ),
            config=graph_config
        ))

    summary_tab = dcc.Tab(label='Risk Summary', children=html.Div(summary_children, style={'padding': '10px'}))

    # 3. P/L Simulation Plot
    pl_children = []
    if data.get("simulated_pl"):
        var_value = data.get("var") or 0
        # Create the density plot
        fig = ff.create_distplot([data["simulated_pl"]], ['P/L'], show_hist=False, show_rug=False, colors=['#1a3d6d'])
        fig.update_layout(title_text='Distribution of Simulated Daily P/L', xaxis_title='Simulated Daily Profit/Loss ($)', yaxis_title='Probability Density', xaxis_tickprefix='$', xaxis_tickformat=',.0f')
        # Add a line for the VaR
        fig.add_vline(x=-var_value, line_dash="dash", line_color="red", annotation_text=f"VaR: ${-var_value:,.0f}")
        
        pl_children.append(html.H4("3. Profit/Loss Simulation", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}))
        pl_children.append(html.P("This smooth curve shows the likelihood of different daily outcomes. The peak is the most likely result, and the left tail shows the risk of losses.", style={'fontSize': '0.9em'}))
        pl_children.append(dcc.Graph(figure=fig, config=graph_config))
    
    pl_tab = dcc.Tab(label='P/L Analysis', children=html.Div(pl_children, style={'padding': '10px'}))

    return dcc.Tabs([summary_tab, pl_tab])

if __name__ == '__main__':
    # Setting debug=True is great for development, but should be False in production.
    app.run(debug=True)
