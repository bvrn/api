import requests
from flask_api import status
import pandas as pd

from bvrnapi.lib.helper.responses.response_exception import ResponseException


def commusic_df(url):
    r = requests.get(url)
    if not status.is_success(r.status_code):
        raise ResponseException(r.text, r.status_code)

    tables = pd.read_html(r.text)
    if not isinstance(tables, list):
        raise ResponseException("Unkown Error - maybe no data found on ComMusic", 500)

    table = tables[0]
    table.columns = ["association", "address", "plz", "city", "homepage"]

    return table
