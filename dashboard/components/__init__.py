import pandas as pd
import requests
from bs4 import BeautifulSoup
from dash import dcc, html

from model import HomeModel
from .plots import plot_totals, plot_payments, plot_cagr


def get_rates():
    soup = BeautifulSoup(requests.get(r'https://www.nerdwallet.com/mortgages/mortgage-rates').content, 'lxml')
    idx = pd.Index(tag.text for tag in soup.select('table thead th'))
    df = pd.DataFrame(
        (
            pd.Series((cell.text for cell in tag.children), index=idx)
            for tag in soup.select('table tbody tr')
        )
    )
    return df


def inclusive_range(start, stop, *args):
    yield from range(start, stop, *args)
    yield stop


def create_controls(model: HomeModel):
    slider_home_val = dcc.Slider(
        id='home-val',
        value=model.initial_appraisal,
        min=0, max=10 ** 6, step=10 ** 4,
        marks={n: f'${n / 10 ** 3:.0f}k' for n in inclusive_range(0, 10 ** 6, 50 * 10 ** 3)}
    )

    slider_down_payment = dcc.Slider(
        id='down-pmt',
        value=model.down_pmt,
        min=0, max=500 * 10 ** 3, step=10 ** 4,
        marks={n: f'${n / 10 ** 3:.0f}k' for n in inclusive_range(0, 10 ** 6, 50 * 10 ** 3)}
    )

    slider_loan_length = dcc.Slider(
        id='loan-term',
        value=model.years,
        min=5, max=30, step=5,
    )

    slider_property_value_growth = dcc.Slider(
        id='prop-growth',
        value=model.appraisal_growth_rate * 100,
        min=0, max=20, step=0.2,
        marks={n: f'{n}%' for n in inclusive_range(0, 20, 1)}
    )

    slider_loan_apr = dcc.Slider(
        id='apr',
        value=model.loan_apr * 100,
        min=1.0, max=10.0, step=0.2,
        marks={n: f'{n}%' for n in inclusive_range(0, 10, 1)}
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
        'Property Value Growth Rate'
    ]

    controls = html.Div([
        html.Div(
            [
                html.Label(text, style={'width': '100px'}),
                slider
            ],
            style={'display': 'flex', 'flex-flow': 'row nowrap', 'flex': '1 1 auto', 'padding': '10px'}
        )
        for text, slider in zip(labels, sliders)
    ])
    return controls
