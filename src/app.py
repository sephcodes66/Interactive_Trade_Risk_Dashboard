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

# --- FLASK API SERVER ---
server = Flask(__name__)

@server.route('/api/risk', methods=['POST'])
def calculate_risk():
    """
    API endpoint to calculate risk for a given portfolio.
    It computes market value, VaR, and historical performance.
    """
    data = request.get_json()
    if not data or 'portfolio' not in data:
        return jsonify({"error": "Invalid input: 'portfolio' key is required."}), 400

    portfolio_dict = data.get('portfolio', {})
    if not portfolio_dict:
        return jsonify({"error": "Portfolio cannot be empty."}), 400

    try:
        pm = PortfolioManager(portfolio_dict)
        risk_engine = RiskEngine(pm)
        
        total_value = pm.calculate_total_market_value()
        if total_value == 0:
             return jsonify({"error": "Could not find market data for any of the selected tickers."}), 400

        var_value, simulated_pl = risk_engine.calculate_historical_var()
        
        # --- Prepare all data for JSON serialization with individual error handling ---
        response_data = {}
        
        try:
            response_data["total_market_value"] = float(total_value)
        except (ValueError, TypeError):
            response_data["total_market_value"] = None

        try:
            response_data["var"] = float(var_value) if var_value is not None and not np.isnan(var_value) else None
        except (ValueError, TypeError):
            response_data["var"] = None

        try:
            response_data["market_values_per_stock"] = {str(k): float(v) for k, v in pm.market_values.items()}
        except (ValueError, TypeError):
            response_data["market_values_per_stock"] = {}

        try:
            response_data["simulated_pl"] = [float(x) for x in simulated_pl]
        except (ValueError, TypeError):
            response_data["simulated_pl"] = []

        return jsonify(response_data)

    except TypeError as e:
        return jsonify({"error": f"A data type error occurred: {e}"}), 400
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred on the server: {e}"}), 500

# --- DASHBOARD ---
app = Dash(__name__, server=server, url_base_pathname='/dash/')
all_tickers = get_all_tickers()

app.layout = html.Div(style={'backgroundColor': '#f0f2f5', 'fontFamily': 'Arial'}, children=[
    html.Div(style={'backgroundColor': 'white', 'padding': '10px 20px', 'borderBottom': '1px solid #ddd'}, children=[
        html.H1("RiskDash: An Interactive Risk Analysis Tool", style={'textAlign': 'center', 'color': '#1a3d6d'})
    ]),
    
    html.Div(style={'display': 'flex', 'padding': '20px'}, children=[
        # Left Panel: Inputs
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
        
        # Right Panel: Outputs
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
    if not selected_tickers:
        return []
    
    inputs = []
    for ticker in selected_tickers:
        inputs.append(html.Div(style={'display': 'flex', 'alignItems': 'center', 'marginTop': '10px'}, children=[
            html.Label(f"{ticker}:", style={'flex': '30%'}),
            dcc.Input(
                id={'type': 'quantity-input', 'index': ticker},
                type='number',
                placeholder='Enter quantity...',
                min=0,
                style={'flex': '70%'}
            )
        ]))
    return inputs

@app.callback(
    Output('ticker-selector', 'value'),
    Output('quantity-inputs', 'children', allow_duplicate=True),
    Output('analysis-output', 'children', allow_duplicate=True),
    Input('clear-button', 'n_clicks'),
    prevent_initial_call=True
)
def clear_inputs(n_clicks):
    """Clears all input fields and the output section."""
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
    if not selected_tickers or not any(input_values):
        return html.Div("Please select tickers and enter quantities.", style={'color': 'red'})

    portfolio = {}
    for i, val in zip(input_ids, input_values):
        if val is not None and val > 0:
            portfolio[i['index']] = val

    if not portfolio:
        return html.Div("Please enter a quantity for at least one stock.", style={'color': 'red'})

    # Use a relative path for the API call to connect to the same server.
    api_url = "/api/risk"
    try:
        # The request needs the full URL including the server address.
        # We can get this from the request context.
        host = request.host_url
        response = requests.post(f"{host.strip('/')}{api_url}", json={'portfolio': portfolio}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return html.Div(f"Error connecting to API: {e}", style={'color': 'red'})

    if 'error' in data:
        return html.Div(f"API Error: {data['error']}", style={'color': 'red'})

    # --- Build Tab Content ---
    graph_config = {
        'scrollZoom': False,
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'resetScale2d']
    }
    
    # Tab 1: Risk Summary
    summary_children = [html.H4("1. Key Risk Metrics", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'})]
    if data.get("total_market_value") is not None:
        summary_children.append(html.P(f"Total Portfolio Market Value: ${data['total_market_value']:,.2f}"))
    if data.get("var") is not None:
        var_value = data['var']
        summary_children.append(html.H5(f"Value at Risk (95%, 1-day): ${var_value:,.2f}", style={'color': '#c0392b'}))
        summary_children.append(html.P("This is the estimated maximum loss the portfolio could experience in a single day, with 95% confidence.", style={'fontSize': '0.9em', 'fontStyle': 'italic'}))
    
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

    # Tab 2: Profit/Loss Analysis
    pl_children = []
    if data.get("simulated_pl"):
        var_value = data.get("var") or 0
        fig = ff.create_distplot([data["simulated_pl"]], ['P/L'], show_hist=False, show_rug=False, colors=['#1a3d6d'])
        fig.update_layout(title_text='Distribution of Simulated Daily P/L', xaxis_title='Simulated Daily Profit/Loss ($)', yaxis_title='Probability Density', xaxis_tickprefix='$', xaxis_tickformat=',.0f')
        fig.add_vline(x=-var_value, line_dash="dash", line_color="red", annotation_text=f"VaR: ${-var_value:,.0f}")
        pl_children.append(html.H4("3. Profit/Loss Simulation", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}))
        pl_children.append(html.P("This smooth curve shows the likelihood of different daily outcomes. The peak is the most likely result, and the left tail shows the risk of losses.", style={'fontSize': '0.9em'}))
        pl_children.append(dcc.Graph(figure=fig, config=graph_config))
    
    pl_tab = dcc.Tab(label='P/L Analysis', children=html.Div(pl_children, style={'padding': '10px'}))

    return dcc.Tabs([summary_tab, pl_tab])

if __name__ == '__main__':
    app.run(debug=True)
