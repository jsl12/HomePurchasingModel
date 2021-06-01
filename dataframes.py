import numpy as np
import pandas as pd

import formulas


def mortgage_amortization(principal, down_pmt, apr, payments_per_period, periods):
    apr = apr / 100 if apr >= 1.0 else apr
    t = np.arange(periods * payments_per_period + 1)
    single_payment = formulas.payment(principal, apr, payments_per_period, periods)

    payment = np.full(t.size, single_payment)
    payment[0] = 0

    balance = np.zeros(t.size)
    balance[0] = principal

    for i in t[1:]:
        balance_with_interest = formulas.compound_interest_amount(balance[i - 1], apr / payments_per_period, 1, 1)
        balance[i] = balance_with_interest - payment[i]

    payments = np.cumsum(payment)
    equity = principal - balance
    interest = payments - equity
    principal_paid = payments - interest

    df = pd.DataFrame(
        {
            'month': t,
            'mortgage balance': balance,
            # 'amount owed': amount,
            'mortgage payment': payment,
            'payments': payments,
            'equity': equity + down_pmt,
            'principal paid': principal_paid,
            'interest paid': interest,
        }
    )
    df = df.set_index('month')
    return df


def property_tax_amortization(appraisal_val, tax_rate, payments_n, duration, appraisal_growth_rate):
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
