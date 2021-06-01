from typing import Union

import numpy as np


def compound_interest_amount(p, r, n, t):
    """
    >>> '%.2f' % compound_interest_amount(100, 0.1, 1, 1)
    '110.00'
    >>> compound_interest_amount(100, 0.03875, 12, 7.5)
    133.66370154434335
    """
    return p * np.power((1 + r/n), n*t)


def mortgage_payment(loan_amount: Union[float, int],
                     interest_rate: float,
                     num_years: int,
                     payments_per_year: int = 12) -> float:
    """
    Calculates a monthly mortgage payment

    Parameters
    ----------
    loan_amount : float or int
    interest_rate : float
    num_years : int
    payments_per_year : int

    Returns
    -------
    float
        Monthly payment amount

    Notes
    -----
    https://www.thebalance.com/calculate-mortgage-315668

    >>> mortage_payment(100*10**3, 0.07, 30, 12)
    665.3024951791823
    """
    period_interest = interest_rate / payments_per_year
    period_multiplier = (1 + period_interest)**(num_years * payments_per_year)
    return (loan_amount * period_interest * period_multiplier) / (period_multiplier - 1)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
