from pathlib import Path

from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from components import create_controls, get_rates
from components import plot_totals, plot_payments
from model import HomeModel

MODEL_PATH = Path('model.yaml').resolve()

# app = JupyterDash(__name__)
app = Dash(__name__)

server = app.server

rate_df = get_rates()

app.layout = html.Div(
    [
        create_controls(HomeModel.from_yaml(MODEL_PATH)),
        dcc.Graph(id='payments'),
        dcc.Graph(id='totals'),
        dcc.Markdown('## [NerdWallet Mortagage Rates](https://www.nerdwallet.com/mortgages/mortgage-rates)'),
        dcc.Markdown(rate_df.set_index(rate_df.columns[0]).to_markdown()),
    ],
    style={'display': 'flex', 'flex-flow': 'column nowrap', 'flex': '1 1 auto', 'overflow-y': 'hidden'}
)


@app.callback(
    Output('down-pmt', 'max'),
    Input('home-val', 'value')
)
def update_home_val(home_val):
    return home_val


@app.callback(
    Output('home-val', 'min'),
    Input('down-pmt', 'value')
)
def update_down_pmt(down_pmt):
    return down_pmt


@app.callback(
    Output('payments', 'figure'),
    [
        Input('home-val', 'value'),
        Input('down-pmt', 'value'),
        Input('loan-term', 'value'),
        Input('apr', 'value'),
        Input('prop-growth', 'value')
    ]
)
def update_payments(home_val, down_pmt, loan_term, apr, growth):
    hm = HomeModel(
        initial_appraisal=home_val,
        down_pmt=down_pmt,
        years=loan_term,
        appraisal_growth_rate=growth / 100,
        loan_apr=apr / 100,
    )
    hm.to_yaml(MODEL_PATH.resolve())
    return plot_payments(hm)


@app.callback(
    Output('totals', 'figure'),
    [
        Input('home-val', 'value'),
        Input('down-pmt', 'value'),
        Input('loan-term', 'value'),
        Input('apr', 'value'),
        Input('prop-growth', 'value')
    ]
)
def update_totals(home_val, down_pmt, loan_term, apr, growth):
    hm = HomeModel(
        initial_appraisal=home_val,
        down_pmt=down_pmt,
        years=loan_term,
        appraisal_growth_rate=growth / 100,
        loan_apr=apr / 100,
    )
    return plot_totals(hm)


if __name__ == '__main__':
    import logging

    logging.basicConfig(level=logging.DEBUG)

    app.run_server(debug=True)
