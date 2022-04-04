import logging
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd
import plotly.express as px
import yaml

from .dataframes import property_tax_amortization, mortgage_amortization, return_on_investment

LOGGER = logging.getLogger(__name__)


@dataclass
class HomeModel:
    initial_appraisal: float
    down_pmt: float
    years: int
    closing_pct: float = 0.034
    loan_apr: float = 0.033
    yearly_payments: int = 12
    property_tax_rate: float = 0.02
    appraisal_growth_rate: float = 0.08
    pmi_rate: float = 0.015
    extend_years: int = 0

    def to_yaml(self, path: Path):
        with path.open('w') as file:
            LOGGER.debug(f'Writing to {path.name}')
            file.writelines(f'{kwarg}: {val}\n' for kwarg, val in asdict(self).items())
            LOGGER.debug(asdict(self))

    @classmethod
    def from_yaml(cls, path: Path):
        if not path.exists():
            HomeModel(
                initial_appraisal=350 * 10 ** 3,
                down_pmt=50 * 10 ** 3,
                years=15
            ).to_yaml(path)

        with path.open('r') as file:
            LOGGER.debug(f'Loading from {path.name}')
            cfg = yaml.load(file, yaml.SafeLoader)
            LOGGER.debug(cfg)
            return HomeModel(**cfg)

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
        totals['Down Payment'] = self.down_pmt
        # totals = totals[['Down Payment', 'Prinicipal', 'Interest', 'Tax', 'PMI']]
        totals.index.name = 'Month'
        return totals

    @property
    def payments(self) -> pd.DataFrame:
        return self.totals.diff().dropna(axis=0, how='all')

    def plot_payments(self):
        pmt = self.payments.iloc[:, :-1]  # take all the columns except the last one, which is the Down Payment
        fig = px.bar(pmt, x=pmt.index, y=pmt.columns, title='Payments')
        fig.update_yaxes(title_text='Amount')
        fig.update_layout(yaxis_tickformat='$.2s')
        return fig

    def plot_totals(self):
        fig = px.bar(
            title='Total Amounts',
            data_frame=self.totals,
            x=self.totals.index, y=self.totals.columns,
        )
        equity = self.roi_df['equity'] - self.down_pmt
        fig.add_scatter(name='Equity', x=self.roi_df.index, y=equity)
        fig.update_xaxes(title_text='Month')
        fig.update_yaxes(title_text='Amount', range=[0, equity.iloc[-1]])
        fig.update_layout(yaxis_tickformat='$.2s')
        return fig

    def plot_cagr(self):
        rdf = self.roi_df
        rdf = rdf.rolling(12, center=True).max()
        rdf = rdf[rdf['cagr'] >= 0] * 100
        fig = px.line(rdf, x=rdf.index, y=['cagr'])
        return fig
