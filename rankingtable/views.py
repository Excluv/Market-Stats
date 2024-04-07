from rankingtable.utils.metrics import MetricsCalculator
from rankingtable.utils.dboperator import DbController

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import json
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta


# Config variables
with open(".\\rankingtable\\defaultconfig.json") as file:
    config = json.load(file)

DB_DIR = config["db_directory"]
START_DATE = config["start_date"]
END_DATE = date.today().strftime("%Y-%m-%d")
METRICS = config["metrics"]
PERIODS = config["periods"]

def add_period(period, column_head):
    """
    Utilility function: Appends a period to the front of a column header
    """
    return str(period) + "_" + str(column_head)


def merge_dicts(records: pd.DataFrame, metrics: list) -> list:
    """
    Merges two datasets into a nested dictionary of records
    """
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


def add_graphing_data(response: dict, start_date: str, end_date: str) -> dict:
    """
    Retrieves and adds data points (used for graphing purpose) of products given in the response to itself
    """
    date_range = pd.to_datetime([start_date, end_date], yearfirst=True)
    if (date_range[1] - date_range[0]).days >= 30:
        start_date = (date_range[1] - pd.to_timedelta(30, unit="D")).strftime("%Y-%m-%d")

    with sqlite3.connect(DB_DIR) as connection:
        controller = DbController(connection)
        for dictionary in response:
            graphing_data = \
                controller.fetch_records(
                    "price record", start_date, end_date,
                    "product", dictionary.get("symbol")
                )
            graphing_data = \
                pd.DataFrame.from_records(
                    graphing_data, exclude=[0, 1, 2, 4, 5, 6]
                ).rename(columns={3: "time", 7: "value"}) \
                .drop_duplicates(subset=["time"]) \
                .to_dict(orient="records")

            dictionary.update({"graphing_data": graphing_data})

        return response


def get_response(start_date: str, end_date: str, metrics: list, periods: list, by="", arg="") -> dict:
    """
    Gets all price records in a given time range or price records of a specified asset class and
    derives statistics metrics from these records. Returns the final result as the reponse.
    """
    with sqlite3.connect(DB_DIR) as connection:
        controller = DbController(connection)
        records = controller.fetch_records("price record", start_date, end_date, by, arg)

        # In case there are no records that match the specified arguments
        if not records: return []

        # Calculate required metrics
        calculator = MetricsCalculator(
            records, columns=["type", "product", "symbol", "date", "open", "high", "low", "close"]
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
        latest_records = calculator.data.groupby(["type", "product"]).last().reset_index()

        # Merge the datasets into a single response of dictionary structure
        response = merge_dicts(latest_records, metrics)
        response = add_graphing_data(response, start_date, end_date)

        return response


class Index(APIView):
    """
    Index Page
    """
    def get(self, request):
        response = get_response(START_DATE, END_DATE, METRICS, PERIODS)
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request):
        response = \
            get_records(
                request.data["date_range"]["from"], request.data["date_range"]["to"],
                request.data["metrics"], request.data["periods"]
            )
        return Response(response, status=status.HTTP_200_OK)


class AssetClass(APIView):
    """
    Data filtered by asset class
    """
    def get(self, request, **kwargs):
        response = \
            get_response(
                START_DATE, END_DATE, METRICS, PERIODS,
                by="asset class", arg=self.kwargs["assetclass"]
            )
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request, **kwargs):
        response = \
            get_records(
                request.data["date_range"]["from"], request.data["date_range"]["to"],
                request.data["metrics"], request.data["periods"],
                by="asset class", arg=self.kwargs["assetclass"]
            )
        return Response(response, status=status.HTTP_200_OK)
