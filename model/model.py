from dataclasses import dataclass

import pandas as pd
import plotly.express as px

from .dataframes import property_tax_amortization, mortgage_amortization, return_on_investment


@dataclass
class HomeModel:
    initial_appraisal: float
    down_pmt: float
    years: int
    closing_pct: float = 0.034
    loan_apr = 0.033
    yearly_payments: int = 12
    property_tax_rate: float = 0.02
    appraisal_growth_rate: float = 0.08
    pmi_rate: float = 0.015
    extend_years: int = 0

    @property
    def principal(self) -> float:
        return self.initial_appraisal - self.down_pmt

    @property
    def tax_df(self) -> pd.DataFrame:
        return property_tax_amortization(
            appraisal_val=self.initial_appraisal,
            tax_rate=self.property_tax_rate,
            duration=self.years + self.extend_years + 1,
            appraisal_growth_rate=self.appraisal_growth_rate
        )

    @property
    def mortgage_df(self) -> pd.DataFrame:
        return mortgage_amortization(
            principal=self.principal,
            down_pmt=self.down_pmt,
            apr=self.loan_apr,
            num_years=self.years
        )

    @property
    def roi_df(self) -> pd.DataFrame:
        return return_on_investment(
            initial_value=self.initial_appraisal,
            down_payment=self.down_pmt,
            closing_rate=self.closing_pct,
            loan_interest_rate=self.loan_apr,
            num_years=self.years,
            extend_years=self.extend_years,
            pmi_rate=self.pmi_rate,
            property_tax_rate=self.property_tax_rate,
            apprasial_growth=self.appraisal_growth_rate
        )

    @property
    def cagr(self) -> float:
        return self.roi_df.iloc[-1].loc['cagr'] * 100

    @property
    def totals(self) -> pd.DataFrame:
        totals = self.roi_df[['principal paid', 'interest paid', 'tax paid', 'pmi paid']].copy()
        totals.columns = ['Prinicipal', 'Interest', 'Tax', 'PMI']
        return totals

    @property
    def payments(self) -> pd.DataFrame:
        return self.totals.diff().dropna(axis=0, how='all')

    def plot_payments(self):
        pmt = self.payments
        fig = px.bar(pmt, x=pmt.index, y=pmt.columns, title='Payments')
        return fig

    def plot_totals(self):
        fig = px.bar(self.totals, x=self.totals.index, y=self.totals.columns, title='Totals')
        fig.add_scatter(
            x=self.roi_df.index,
            y=self.roi_df['equity'] - self.down_pmt,
            name='Equity')
        return fig

    def plot_cagr(self):
        rdf = self.roi_df
        rdf = rdf[rdf['cagr'] >= 0] * 100
        fig = px.line(rdf, x=rdf.index, y=['cagr'])
        return fig
