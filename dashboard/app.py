from dash import Dash
from dash import dcc, html
from dash.dependencies import Input, Output

from model import HomeModel

# app = JupyterDash(__name__)
app = Dash(__name__)

server = app.server

marks = {n: f'${n / 10 ** 3:.0f}k' for n in range(0, 10 ** 6, 50 * 10 ** 3)}
marks[10 ** 6] = '$1M'
slider_home_val = dcc.Slider(
    id='home-val',
    min=0, max=10 ** 6, step=10 ** 4, value=350 * 10 ** 3,
    marks=marks
)

marks = {n: f'${n / 10 ** 3:.0f}k' for n in range(0, 10 ** 6, 50 * 10 ** 3)}
marks[10 ** 6] = '$1M'
slider_down_payment = dcc.Slider(
    id='down-pmt',
    min=0, max=500 * 10 ** 3, step=10 ** 4, value=50 * 10 ** 3,
    marks=marks
)

slider_loan_length = dcc.Slider(
    id='loan-term',
    min=5, max=30, step=5, value=15,
)

marks = {n: f'{n}%' for n in range(0, 20, 1)}
marks[20] = '20'
slider_property_value_growth = dcc.Slider(
    id='prop-growth',
    min=0, max=20, step=0.2, value=8.0,
    marks=marks
)

marks = {n: f'{n}%' for n in range(0, 10, 1)}
marks[10] = '10'
slider_loan_apr = dcc.Slider(
    id='apr',
    min=1.0, max=10.0, step=0.2, value=3.3,
    marks=marks
)

sliders = [
    html.Div(s, style={'display': 'flex', 'flex-flow': 'column nowrap', 'flex': '1 1 auto'})
    for s in [
        slider_home_val,
        slider_down_payment,
        slider_loan_length,
        slider_loan_apr,
        slider_property_value_growth,
    ]
]

labels = [
    'Home Value',
    'Down Payment',
    'Loan Term',
    'Loan APR',
    'Property Growth'
]

controls = html.Div([
    html.Div(
        [html.Label(label, style={'width': '100px'}), slider],
        style={'display': 'flex', 'flex-flow': 'row nowrap', 'flex': '1 1 auto', 'padding': '10px'}
    )
    for label, slider in zip(labels, sliders)
])

app.layout = html.Div(
    [controls, dcc.Graph(id='payments'), dcc.Graph(id='totals')],
    style={'display': 'flex', 'flex-flow': 'column nowrap', 'flex': '1 1 auto', 'overflow-y': 'hidden'}
)


@app.callback(
    Output('down-pmt', 'max'),
    Input('home-val', 'value')
)
def update_down_pmt(home_val):
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
    return hm.plot_payments()


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
def update_payments(home_val, down_pmt, loan_term, apr, growth):
    hm = HomeModel(
        initial_appraisal=home_val,
        down_pmt=down_pmt,
        years=loan_term,
        appraisal_growth_rate=growth / 100,
        loan_apr=apr / 100,
    )
    return hm.plot_totals()


if __name__ == '__main__':
    app.run_server(debug=True)
