from typing import Union

import matplotlib.pyplot as plt
import pandas as pd

from dataframes import return_on_investment


def annualized_return_vs_growth(initial_value: Union[float, int],
                                down_payment: Union[float, int],
                                loan_interest_rate: float,
                                growth_rates,
                                num_years: int = 30,
                                pmi_rate: float = .015,
                                property_tax_rate: float = 0.02):
    fig, ax = plt.subplots()
    ax.plot(pd.Series(
        data=[
            return_on_investment(
                initial_value,
                down_payment,
                loan_interest_rate,
                num_years,
                pmi_rate,
                property_tax_rate,
                g
            )['annualized roi'].iloc[-1] * 100
            for g in growth_rates
        ],
        index=growth_rates * 100
    ))
    ax.set_title(f'${initial_value/10**3:.0f}k house, {num_years} year loan, {loan_interest_rate*100:.1f}% APR')
    ax.set_ylim(-3, ax.get_ylim()[1])
    ax.set_ylabel('Annualized Return')
    ax.xaxis.set_major_formatter('{x:.0f}%')
    ax.yaxis.set_major_formatter('{x:.0f}%')
    ax.grid(True)
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_xlabel('Annualized Growth Rate')


def monthly_payment_vs_down_pmt(initial_value: Union[float, int],
                                down_payments,
                                loan_interest_rate: float,
                                num_years: int = 30,
                                pmi_rate: float = .015,
                                property_tax_rate: float = 0.02,
                                apprasial_growth: float = 0.04):
    fig, ax = plt.subplots()
    ax.set_title(f'${initial_value/10**3:.0f}k house, {num_years} year loan, {loan_interest_rate*100:.1f}% APR')
    ax.plot(pd.Series(
        data=[
            return_on_investment(
                initial_value,
                d,
                loan_interest_rate,
                num_years,
                pmi_rate,
                property_tax_rate,
                apprasial_growth
            )['total monthly payment'].iloc[1] / 10**3
            for d in down_payments
        ],
        index=down_payments / 10**3
    ))
    ax.grid(True)
    ax.set_ylabel('Initial Monthly Payment')
    ax.xaxis.set_major_formatter('${x:.0f}k')
    ax.set_xlabel('Down Payment')
    ax.yaxis.set_major_formatter('${x:.1f}k')
