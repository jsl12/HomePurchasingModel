import plotly.express as px
from plotly.graph_objects import Figure

from model import HomeModel


def plot_payments(model: HomeModel) -> Figure:
    pmt = model.payments.iloc[:, :-1]  # take all the columns except the last one, which is the Down Payment
    fig: Figure = px.bar(pmt, x=pmt.index, y=pmt.columns, title='Payments')
    fig.update_yaxes(title_text='Amount')
    fig.update_layout(yaxis_tickformat='$.2s')
    return fig


def plot_totals(model: HomeModel) -> Figure:
    totals = model.totals
    fig: Figure = px.bar(
        title='Total Amounts',
        data_frame=totals,
        x=totals.index, y=totals.columns,
    )
    equity = model.roi_df['equity'] - model.down_pmt
    fig.add_scatter(name='Equity', x=model.roi_df.index, y=equity)
    fig.update_xaxes(title_text='Month')
    fig.update_yaxes(title_text='Amount', range=[0, max((equity.iloc[-1], totals.max().sum()))])
    fig.update_layout(yaxis_tickformat='$.2s')
    return fig


def plot_cagr(model: HomeModel) -> Figure:
    rdf = model.roi_df
    rdf = rdf.rolling(12, center=True).max()
    rdf = rdf[rdf['cagr'] >= 0] * 100
    fig = px.line(rdf, x=rdf.index, y=['cagr'])
    return fig
