from dataclasses import dataclass

import numpy as np
import pandas as pd
import plotly.express as px

from .dataframes import property_tax_amortization, mortgage_amortization


@dataclass
class HomeModel:
    initial_appraisal: float
    down_pmt: float
    years: int
    closing_pct: float = 0.034
    loan_apr = 0.033
    yearly_payments: int = 12
    property_tax_rate: float = 0.02
    appraisal_growth_rate: float = 0.04
    pmi_rate: float = 0.015
    extend_years: int = 0

    def __post_init__(self):
        return

    @property
    def principal(self) -> float:
        return self.initial_appraisal - self.down_pmt

    def tax_df(self, years: int) -> pd.DataFrame:
        df = property_tax_amortization(
            appraisal_val=self.initial_appraisal,
            tax_rate=self.property_tax_rate,
            duration=years + 1,
            appraisal_growth_rate=self.appraisal_growth_rate
        )

        # convert index from years starting at 1 to months starting at 0
        df.index = pd.Index(data=(df.index - 1) * 12, name='month')
        df = df.reindex(np.arange(df.index[-1] + 1), method='pad')

        return df

    @property
    def mortgage_df(self) -> pd.DataFrame:
        df = mortgage_amortization(
            principal=self.principal,
            down_pmt=self.down_pmt,
            apr=self.loan_apr,
            num_years=self.years
        )

        df = pd.merge(df, self.tax_df(years=self.years), how='outer', left_index=True, right_index=True)

        # apply PMI where necessary, defined as when equity is less than 20% of the appraisal value
        df['pmi'] = 0
        if self.down_pmt < (self.initial_appraisal * 0.2):
            mask = df['equity'] < (df['appraisal value'] * 0.2)
            df.loc[mask, 'pmi'] = (df.loc[mask, 'mortgage balance'] * self.pmi_rate) / self.yearly_payments

        df['total monthly payment'] = df['mortgage payment'] + df['monthly tax payment'] + df['pmi']
        df['tax paid'] = df['monthly tax payment'].cumsum()
        df['pmi paid'] = df['pmi'].cumsum()
        df['total paid'] = df['total monthly payment'].cumsum() + \
                           self.down_pmt + \
                           (self.closing_pct * df['mortgage balance'].iloc[0])
        df['equity'] = df['appraisal value'] - df['mortgage balance']

        df['cagr'] = [
            np.exp(np.log(roi) / (n / self.yearly_payments)) - 1
            if n > 0 else 0
            for n, roi in enumerate(np.nditer(df['equity'] / df['total paid']))
        ]

        return df

    @property
    def cagr(self) -> float:
        return self.mortgage_df.iloc[-1].loc['cagr'] * 100

    @property
    def totals(self) -> pd.DataFrame:
        totals = self.mortgage_df[['principal paid', 'interest paid', 'tax paid', 'pmi paid']].copy()
        totals.columns = ['Prinicipal', 'Interest', 'Tax', 'PMI']

        if self.extend_years > 0:
            df = self.tax_df(years=self.years + self.extend_years)
            totals = totals.reindex(df.index).fillna(0)
            totals['Tax'] = df['monthly tax payment'].cumsum()

        return totals

    @property
    def payments(self) -> pd.DataFrame:
        return self.totals.diff()

    def plot_payments(self):
        fig = px.bar(self.payments, x=self.payments.index, y=self.payments.columns, title='Payments')
        return fig

    def plot_totals(self):
        fig = px.bar(self.totals, x=self.totals.index, y=self.totals.columns, title='Totals')
        fig.add_scatter(
            x=self.mortgage_df.index,
            y=self.mortgage_df['equity'] - self.down_pmt,
            name='Equity')
        return fig
