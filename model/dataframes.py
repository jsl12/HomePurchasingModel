import itertools
import logging
import math
from typing import Union

import numpy as np
import pandas as pd

import formulas


def mortgage_amortization(principal: Union[float, int],
                          down_pmt: Union[float, int],
                          apr: float,
                          num_years: int = 30) -> pd.DataFrame:
    """
    Creates a `pd.DataFrame` of the mortgage amortization with the following columns:
     - mortgage balance
     - mortgage payment
     - total paid
     - equity
     - principal paid
     - interest paid

    Parameters
    ----------
    principal : float or int
    down_pmt : float or int
    apr : float
    num_years : int

    Returns
    -------
    pd.DataFrame
    """
    payments_per_year: int = 12
    apr = apr / 100 if apr >= 1.0 else apr
    t = np.arange(num_years * payments_per_year + 1)
    single_payment = formulas.mortgage_payment(loan_amount=principal,
                                               interest_rate=apr,
                                               num_years=num_years,
                                               payments_per_year=payments_per_year)

    payment = np.full(t.size, single_payment)
    payment[0] = 0

    balance = np.zeros(t.size)
    balance[0] = principal

    period_interest_multiplier = (1 + (apr / payments_per_year))
    for i in np.nditer(t[1:]):
        balance[i] = (balance[i - 1] * period_interest_multiplier) - payment[i]

    total_paid = np.cumsum(payment)
    equity = principal - balance
    interest = total_paid - equity
    principal_paid = total_paid - interest

    df = pd.DataFrame({
        'month': t,
        'mortgage balance': balance,
        'mortgage payment': payment,
        'total paid': total_paid,
        'equity': equity + down_pmt,
        'principal paid': principal_paid,
        'interest paid': interest,
    })
    df = df.set_index('month')
    return df


def property_tax_amortization(appraisal_val: Union[float, int],
                              tax_rate: float,
                              duration: int,
                              appraisal_growth_rate: float) -> pd.DataFrame:
    """

    Parameters
    ----------
    appraisal_val : float or int
    tax_rate : float
    duration : int
    appraisal_growth_rate : float

    Returns
    -------
    pd.DataFrame
    """

    t = np.arange(duration)

    vectorized_tax_growth = np.vectorize(
        lambda x: formulas.compound_interest_amount(appraisal_val, appraisal_growth_rate, 1, x))
    # avalue = np.full(t.size, appraisal_val)
    avalue = vectorized_tax_growth(t)
    annual_tax_owed = avalue * tax_rate
    monthly_tax_owed = annual_tax_owed / 12

    df = pd.DataFrame(
        {
            'year': t + 1,
            'appraisal value': avalue,
            'annual tax owed': annual_tax_owed,
            'monthly tax payment': monthly_tax_owed,
        }
    )
    return df.set_index('year')


def amortization_summary(ma_df, tax_df):
    df = ma_df.copy()
    years = (df.index - 1) / 12 + 1
    df['year'] = years.astype(int)
    df.at[0, 'year'] = 0
    # print(df.keys())
    df = df.merge(tax_df[['monthly tax payment', 'appraisal value']], how='left', left_on='year', right_index=True,
                  copy=False)
    df['monthly payment'] = df['mortgage payment'] + df['monthly tax payment']
    df['payments'] = np.cumsum(df['monthly payment'])
    df['tax paid'] = np.cumsum(df['monthly tax payment'])
    df['mortgage payment principal'] = df['principal paid'] / (df['principal paid'] + df['interest paid']) * \
                                       df['mortgage payment']
    df['mortgage payment interest'] = df['interest paid'] / (df['principal paid'] + df['interest paid']) * \
                                      df['mortgage payment']
    # df = df.drop(columns=['year'])
    return df


def return_on_investment(initial_value: Union[float, int],
                         down_payment: Union[float, int],
                         closing_rate: float,
                         loan_interest_rate: float,
                         extend_years: int = 15,
                         num_years: int = 15,
                         pmi_rate: float = .015,
                         property_tax_rate: float = 0.02,
                         apprasial_growth: float = 0.04) -> pd.DataFrame:
    tax_df = property_tax_amortization(
        appraisal_val=initial_value,
        tax_rate=property_tax_rate,
        duration=num_years + extend_years + 1,
        appraisal_growth_rate=apprasial_growth
    )

    # convert index from years starting at 1 to months starting at 0, so it can be merged with the other DataFrame
    tax_df.index = pd.Index(data=(tax_df.index - 1) * 12, name='Month')
    tax_df = tax_df.reindex(np.arange(tax_df.index[-1] + 1), method='pad')

    mortgage_df = mortgage_amortization(principal=initial_value - down_payment,
                                        down_pmt=down_payment,
                                        apr=loan_interest_rate,
                                        num_years=num_years)

    df = pd.merge(mortgage_df, tax_df,
                  left_index=True,
                  right_index=True,
                  how='outer')

    df[['principal paid', 'interest paid']] = df[['principal paid', 'interest paid']].fillna(method='ffill')
    df = df.fillna(0)

    # apply PMI where necessary, defined as when equity is less than 20% of the appraisal value
    df['pmi'] = 0
    if down_payment < (initial_value * 0.2):
        mask = df['equity'] < (df['appraisal value'].iloc[0] * 0.2)
        df.loc[mask, 'pmi'] = (df.loc[mask, 'mortgage balance'].iloc[0] * pmi_rate) / 12

    df['total monthly payment'] = df['mortgage payment'] + df['monthly tax payment'] + df['pmi']
    df['tax paid'] = df['monthly tax payment'].cumsum()
    df['pmi paid'] = df['pmi'].cumsum()
    df['total paid'] = df['total monthly payment'].cumsum() + \
                       down_payment + \
                       (closing_rate * df['mortgage balance'].iloc[0])
    df['equity'] = df['appraisal value'] - df['mortgage balance']
    df['cagr'] = [
        np.exp(np.log(roi) / (n / 12)) - 1
        if n > 0 else 0
        for n, roi in enumerate(np.nditer(df['equity'] / df['total paid']))
    ]
    return df


def crossover(crossover: float,
              loan_interest_rate: float,
              closing_rate: float,
              num_years: int = 30,
              pmi_rate: float = .015,
              property_tax_rate: float = 0.02) -> pd.DataFrame:
    """

    Parameters
    ----------
    crossover : float
    loan_interest_rate : float
    num_years : int
    pmi_rate : float
    property_tax_rate : float

    Returns
    -------

    """
    down_payments = np.arange(25, 205, 5)
    initial_values = np.arange(200, 650, 50)
    asset_growths = np.arange(0, 0.16, 0.01)

    df = pd.DataFrame(
        columns=pd.MultiIndex.from_product([asset_growths, initial_values], names=['Growth Rate', 'Purchase Price']),
        index=pd.Index(down_payments, name='Down Payment')
    )
    for growth, down_pmt, price in itertools.product(asset_growths, down_payments, initial_values):
        s = f'Initial value: {down_pmt}, down pmt: {price}, growth: {growth * 100:.1f}%'
        try:
            res = return_on_investment(
                initial_value=price * 10 ** 3,
                down_payment=down_pmt * 10 ** 3,
                closing_rate=closing_rate,
                loan_interest_rate=loan_interest_rate,
                num_years=num_years,
                pmi_rate=pmi_rate,
                property_tax_rate=property_tax_rate,
                apprasial_growth=growth
            )
        except Exception as e:
            logging.exception(e)
            logging.error(s)
            break
        else:
            # print(s)
            try:
                df.loc[down_pmt, (growth, price)] = res[res['cagr'] > crossover].index[0]
            except Exception as e:
                df.loc[down_pmt, (growth, price)] = -1

    return df
