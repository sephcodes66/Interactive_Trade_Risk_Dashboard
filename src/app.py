import json
import requests
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.figure_factory as ff
from flask import Flask, request, jsonify
from dash import Dash, dcc, html, Input, Output, State, callback_context, ALL

from portfolio import PortfolioManager
from risk_engine import RiskEngine
from db_connector import get_all_tickers

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

        var_value, simulated_pl, hist_prices = risk_engine.calculate_historical_var()
        hist_performance = risk_engine.calculate_historical_performance(hist_prices)
        
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
            response_data["market_values_per_stock"] = {k: float(v) for k, v in pm.market_values.items()}
        except (ValueError, TypeError):
            response_data["market_values_per_stock"] = {}

        try:
            response_data["simulated_pl"] = [float(x) for x in simulated_pl]
        except (ValueError, TypeError):
            response_data["simulated_pl"] = []

        try:
            hist_perf_df = hist_performance.reset_index()
            hist_perf_df.columns = ['price_date', 'value']
            hist_perf_df['price_date'] = hist_perf_df['price_date'].dt.strftime('%Y-%m-%d')
            response_data["historical_performance"] = hist_perf_df.to_dict('records')
        except Exception:
            response_data["historical_performance"] = []

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
                html.Button('Analyze Portfolio', id='analyze-button', n_clicks=0, style={'marginTop': '20px', 'width': '100%', 'backgroundColor': '#1a3d6d', 'color': 'white', 'border': 'none', 'padding': '10px', 'cursor': 'pointer'}),
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

    api_url = "http://127.0.0.1:5000/api/risk"
    try:
        response = requests.post(api_url, json={'portfolio': portfolio}, timeout=30)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        return html.Div(f"Error connecting to API: {e}", style={'color': 'red'})

    if 'error' in data:
        return html.Div(f"API Error: {data['error']}", style={'color': 'red'})

    # Build the output display dynamically and safely.
    output_children = []
    graph_config = {'staticPlot': True}
    graph_style = {'height': '450px'}

    # --- Risk Summary Card ---
    summary_children = [html.H4("1. Key Risk Metrics", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'})]
    if data.get("total_market_value") is not None:
        summary_children.append(html.P(f"Total Portfolio Market Value: ${data['total_market_value']:,.2f}"))
    else:
        summary_children.append(html.P("Total Portfolio Market Value: Could not be calculated."))

    if data.get("var") is not None:
        var_value = data['var']
        summary_children.append(html.H5(f"Value at Risk (95%, 1-day): ${var_value:,.2f}", style={'color': '#c0392b'}))
        summary_children.append(html.P("This is the estimated maximum loss the portfolio could experience in a single day, with 95% confidence, based on historical data.", style={'fontSize': '0.9em', 'fontStyle': 'italic'}))
    else:
        summary_children.append(html.P("Value at Risk (VaR): Could not be calculated.", style={'fontWeight': 'bold', 'color': '#c0392b'}))
    
    output_children.append(html.Div(summary_children, style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 'marginBottom': '20px'}))

    # --- Charts ---
    charts_children = []
    # Portfolio Composition Pie Chart
    if data.get("market_values_per_stock"):
        pie_chart_card = html.Div([
            html.H4("2. Risk Concentration", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}),
            html.P("This chart shows where your portfolio's value is concentrated. High concentration in a single asset increases risk.", style={'fontSize': '0.9em'}),
            dcc.Graph(
                figure=px.pie(
                    pd.DataFrame(list(data['market_values_per_stock'].items()), columns=['Ticker', 'Market Value']),
                    values='Market Value', names='Ticker', title='Portfolio Composition by Market Value'
                ),
                config=graph_config,
                style=graph_style
            )
        ], style={'flex': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 'marginRight': '10px'})
        charts_children.append(pie_chart_card)
    
    # P/L Distribution Chart
    if data.get("simulated_pl"):
        var_value = data.get("var") or 0
        simulated_pl_data = data["simulated_pl"]
        
        # Create the density plot
        fig = ff.create_distplot(
            [simulated_pl_data],
            ['P/L'],
            show_hist=False,
            show_rug=False,
            colors=['#1a3d6d']
        )
        
        fig.update_layout(
            title_text='Distribution of Simulated Daily P/L',
            xaxis_title='Simulated Daily Profit/Loss ($)',
            yaxis_title='Probability Density',
            xaxis_tickprefix='$',
            xaxis_tickformat=',.0f'
        )
        
        # Add the VaR line
        fig.add_vline(
            x=-var_value, 
            line_dash="dash", 
            line_color="red", 
            annotation_text=f"VaR: ${-var_value:,.0f}"
        )

        pl_dist_card = html.Div([
            html.H4("3. Profit/Loss Simulation", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}),
            html.P("This smooth curve shows the likelihood of different daily outcomes. The peak is the most likely result, and the left tail shows the risk of losses.", style={'fontSize': '0.9em'}),
            dcc.Graph(
                figure=fig,
                config=graph_config,
                style=graph_style
            )
        ], style={'flex': '50%', 'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px', 'marginLeft': '10px'})
        charts_children.append(pl_dist_card)
    
    output_children.append(html.Div(charts_children, style={'display': 'flex', 'marginBottom': '20px'}))

    # Historical Performance Chart
    if data.get("historical_performance"):
        hist_perf_card = html.Div([
            html.H4("4. Historical Performance Analysis", style={'borderBottom': '1px solid #eee', 'paddingBottom': '10px'}),
            html.P("This chart shows how this exact portfolio would have performed over the last year, giving insight into its behavior during past market conditions.", style={'fontSize': '0.9em'}),
            dcc.Graph(
                figure=px.line(
                    pd.DataFrame(data['historical_performance']), x='price_date', y='value', title='Simulated Historical Portfolio Value'
                ).update_layout(
                    xaxis_title='Date', 
                    yaxis_title='Portfolio Value ($)',
                    yaxis_tickprefix='$',
                    yaxis_tickformat=',.0f'
                ),
                config=graph_config,
                style=graph_style
            )
        ], style={'backgroundColor': 'white', 'padding': '20px', 'borderRadius': '5px'})
        output_children.append(hist_perf_card)

    return html.Div(output_children)

if __name__ == '__main__':
    app.run(debug=True)