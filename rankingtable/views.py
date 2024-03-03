from .models import AssetClass, Product, PriceRecord
from .utils.metrics import MetricsCalculator
from .utils.dboperator import DbController

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta


## Utility functions
# Default request parameters
DEFAULT_START_DATE = "2024-01-01"
DEFAULT_END_DATE = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
DEFAULT_METRICS = ["expected_return", "volatility", "updown_ratio"]
DEFAULT_PERIODS = ["d", "w", "m", "y"]


# Append a period to the front of a column header
def add_period(period, column_head):
    return str(period) + "_" + str(column_head)


# Merge two dictionaries and returns dictionaries of single data records
def merge_dicts(records: pd.DataFrame, metrics: list) -> list:
    for dictionary in metrics:
        for key, value in dictionary.items():
            dictionary[key] = pd.DataFrame.from_records(value)

            # Special case when relative_change is calculated on multiple periods
            if "relative_change" in dictionary[key].columns:
                dictionary[key].columns = [add_period(key, column) for column in dictionary[key].columns]

            # Reset index and merges with the records DataFrame
            dictionary[key] = dictionary[key].reset_index(names=["product"])
            records = pd.merge(records, dictionary[key], on=["product"]).rename(columns={"close": "value"})

    return records.to_dict(orient="records")


# Add data points used for graphing to the response
def add_graphing_data(response: dict, start_date: str, end_date: str) -> dict:
    date_range = pd.to_datetime([start_date, end_date], yearfirst=True)
    if (date_range[1] - date_range[0]).days >= 30:
        start_date = (date_range[1] - pd.to_timedelta(30, unit="D")).strftime("%Y-%m-%d")

    DIR = ".\\db.sqlite3"
    with sqlite3.connect(DIR) as connection:
        controller = DbController(connection)
        for dictionary in response:
            graphing_data = controller.fetch_records("price record",
                                                     start_date, end_date,
                                                     "product", dictionary.get("product"))
            graphing_data = pd.DataFrame.from_records(graphing_data, exclude=[0, 1, 3, 4, 5]) \
                                        .rename(columns={2: "time", 6: "value"}) \
                                        .to_dict(orient="records")
            dictionary.update({"graphing_data": graphing_data})

        return response


# Explicitly update CSV files and DB with the most recent records
def update_records(connection: sqlite3.Connection) -> None:
    BASE_DIR = ".\\"
    cursor = connection.cursor()

    # Check if DB is up to date
    latest_date_db = cursor.execute("SELECT MAX(date) FROM rankingtable_pricerecord").fetchone()[0]
    if not latest_date_db == DEFAULT_END_DATE:
        controller = DbController(connection)
        controller.update_db("yfinance", BASE_DIR + "Data")


# Get records of specified asset classes and their corresponding metrics
def get_records(start_date: str, end_date: str, metrics: list, periods: list, by="", arg="") -> dict:
    DIR = ".\\db.sqlite3"
    with sqlite3.connect(DIR) as connection:
        update_records(connection)
        controller = DbController(connection)
        records = controller.fetch_records("price record", start_date, end_date, by, arg)

        # In case there are no records that match the specified arguments
        if not records:
            return []

        # Calculate required metrics
        calculator = MetricsCalculator(
            records,
            columns=["type", "product", "date", "open", "high", "low", "close"]
        )

        # Exclude the user-specified metrics set when it is empty
        if metrics:
            # Accept empty period
            metrics = calculator.calc(["relative_change"], periods) \
                      + calculator.calc(["absolute_change"], ["d"]) \
                      + calculator.calc(metrics, ["d"])
        else:
            metrics = calculator.calc(["relative_change"], periods) \
                      + calculator.calc(["absolute_change"], ["d"])

        # Retrieve latest records available
        latest_records = calculator.data \
                                .groupby(["type", "product"])\
                                .last().reset_index()

        # Merge the two datasets into a single response of dictionary type
        response = merge_dicts(latest_records, metrics)

        response = add_graphing_data(response, start_date, end_date)

        return response


## View classes
class Index(APIView):
    def get(self, request):
        response = get_records(DEFAULT_START_DATE, DEFAULT_END_DATE, DEFAULT_METRICS, DEFAULT_PERIODS)

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        response = get_records(request.data["date_range"]["from"],
                               request.data["date_range"]["to"],
                               request.data["metrics"],
                               request.data["periods"])

        return Response(response, status=status.HTTP_200_OK)


class AssetClass(APIView):
    def get(self, request, **kwargs):
        response = get_records(DEFAULT_START_DATE, DEFAULT_END_DATE,
                               DEFAULT_METRICS, DEFAULT_PERIODS,
                               by="asset class", arg=self.kwargs["assetclass"])

        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        response = get_records(request.data["date_range"]["from"],
                               request.data["date_range"]["to"],
                               request.data["metrics"],
                               request.data["periods"],
                               by="asset class", arg=self.kwargs["assetclass"])

        return Response(response, status=status.HTTP_200_OK)
