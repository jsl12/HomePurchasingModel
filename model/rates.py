import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_rates():
    soup = BeautifulSoup(requests.get(r'https://www.nerdwallet.com/mortgages/mortgage-rates').content, 'lxml')
    idx = pd.Index(tag.text for tag in soup.select('table thead th'))
    df = pd.DataFrame(
        (
            pd.Series((cell.text for cell in tag.children), index=idx)
            for tag in soup.select('table tbody tr')
        )
    )
    return df
