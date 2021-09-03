import logging
from typing import Union

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model.dataframes import return_on_investment


def cagr_vs_growth(initial_value: Union[float, int],
                                loan_interest_rate: float,
                                closing_rate: float,
                                num_years: int = 30,
                                pmi_rate: float = .015,
                                property_tax_rate: float = 0.02, **kwargs):
    down_payments = np.arange(0.05, 0.45, 0.05) * initial_value
    growth_rates = np.arange(0.01, 0.15, 0.005)
    fig, ax = plt.subplots(**kwargs)
    ax.plot(pd.DataFrame({
        dp: pd.Series([
            return_on_investment(
                initial_value=initial_value,
                down_payment=dp,
                closing_rate=closing_rate,
                loan_interest_rate=loan_interest_rate,
                num_years=num_years,
                pmi_rate=pmi_rate,
                property_tax_rate=property_tax_rate,
                apprasial_growth=g)['cagr'].iloc[-1] * 100
            for g in growth_rates
        ],
            index=growth_rates * 100)
        for dp in down_payments
    }),
        label=[f'${dp / 10 ** 3:.0f}k' for dp in down_payments]
    )
    ax.set_title(f'${initial_value/10**3:.0f}k house, {num_years} year loan, {loan_interest_rate*100:.1f}% APR')
    ax.set_ylim(-3, ax.get_ylim()[1])
    ax.set_ylabel('Compound Annual Growth Rate')
    ax.xaxis.set_major_formatter('{x:.0f}%')
    ax.yaxis.set_major_formatter('{x:.0f}%')
    ax.grid(True)
    ax.set_xlim(0, ax.get_xlim()[1])
    ax.set_xlabel('Asset Appreciation APR')
    ax.legend(title='Down Payment')


def monthly_payment_vs_down_pmt(loan_interest_rate: float,
                                closing_rate: float,
                                num_years: int = 30,
                                pmi_rate: float = .015,
                                property_tax_rate: float = 0.02,
                                **kwargs):
    df = pd.DataFrame(columns=pd.Index(np.arange(200, 650, 50)),
                      index=pd.Index(np.arange(25, 205, 5), name='down_pmt'))

    for idx in np.arange(df.shape[0]):
        for col in np.arange(df.shape[1]):
            try:
                df.iloc[idx, col] = return_on_investment(
                    initial_value=df.columns[col] * 10 ** 3,
                    down_payment=df.index[idx] * 10 ** 3,
                    loan_interest_rate=loan_interest_rate,
                    closing_rate=closing_rate,
                    num_years=num_years,
                    pmi_rate=pmi_rate,
                    property_tax_rate=property_tax_rate,
                    apprasial_growth=0)['total monthly payment'].iloc[1] / 10 ** 3
            except Exception as e:
                logging.exception(e)
                print(idx, col)

    fig, ax = plt.subplots(**kwargs)
    ax.set_title(f'{num_years} year loan, {loan_interest_rate * 100:.1f}% APR, {pmi_rate*100:.1f}% PMI')
    ax.plot(df, label=[f'${v:.0f}k' for v in df.columns.values])
    ax.grid(True)
    ax.set_ylabel('Initial Monthly Payment')
    ax.xaxis.set_major_formatter('${x:.0f}k')
    ax.set_xlabel('Down Payment')
    ax.yaxis.set_major_formatter('${x:.1f}k')
    ax.legend(title='Home Value')
    return df
