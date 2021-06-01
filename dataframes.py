from typing import Union

import numpy as np
import pandas as pd

import formulas


def mortgage_amortization(principal: Union[float, int],
                          down_pmt: Union[float, int],
                          apr: float,
                          num_years: int = 30,
                          payments_per_year: int = 12) -> pd.DataFrame:
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
    payments_per_year : int

    Returns
    -------
    pd.DataFrame
    """
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
        balance[i] = ((balance[i - 1] * period_interest_multiplier) - payment[i])

    total_paid = np.cumsum(payment)
    equity = principal - balance
    interest = total_paid - equity
    principal_paid = total_paid - interest

    df = pd.DataFrame(
        {
            'month': t,
            'mortgage balance': balance,
            # 'amount owed': amount,
            'mortgage payment': payment,
            'total paid': total_paid,
            'equity': equity + down_pmt,
            'principal paid': principal_paid,
            'interest paid': interest,
        }
    )
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
            'year': t,
            'appraisal value': avalue,
            'annual tax owed': annual_tax_owed,
            'monthly tax payment': monthly_tax_owed,
        }
    )
    return df.set_index('year')
