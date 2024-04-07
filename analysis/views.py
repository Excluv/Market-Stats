from analysis.utils.dboperator import DbController
from analysis.utils.chartdata import DataMixer
from analysis.utils.metrics import MetricsCalculator

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

import json
import sqlite3
import pandas as pd
from datetime import datetime


# Get configs from file
with open(".\\analysis\\exportdata.json") as file:
    config = json.load(file)

# Config variables
DB_DIR = config["db_directory"]
START_DATE = config["start_date"]
END_DATE = config["end_date"]
DATA_CFG = config["sector_mapping"]

def get_chart_data(controller: DbController,
                   start_date: str, end_date: str,
                   product: str, sector: str) -> dict:
    chart_data = dict()
    mixer = DataMixer(start_date, end_date, controller)
    mix_sets = DATA_CFG[sector]
    for key, value in mix_sets.items():
        if key == "price_mixed_set":
            mixed_data = mixer.get_mixed_data("prices and news", product, value)
        else:
            mixed_data = mixer.get_mixed_data("news", value)
        chart_data.update({key: mixed_data})

    return chart_data


def get_table_data(data: dict, product: str, metric: str) -> dict:
    data = pd.DataFrame.from_records(data)
    data.name = product
    metric_calculation_result = MetricsCalculator(data).calc([metric])
    return metric_calculation_result[metric]


def get_response(start_date: str, end_date: str,
                 product: str, sector: str,
                 data_category: str, metric=None) -> dict:
    """
    Gets records from DB and wrap them into a dictionary as response
    """
    with sqlite3.connect(DB_DIR) as connection:
        controller = DbController(connection)

        if data_category == "chart":
            chart_data = get_chart_data(controller, start_date, end_date, product, sector)
            return chart_data

        if data_category == "table" and metric:
            # The given dates in URL are of yyyymmdd format, converts them into %Y-%m-%d to perform query
            start_date = pd.to_datetime(start_date, yearfirst=True).strftime("%Y-%m-%d")
            end_date = pd.to_datetime(end_date, yearfirst=True).strftime("%Y-%m-%d")

            chart_data = get_chart_data(controller, start_date, end_date, product, sector)["price_mixed_set"]
            table_data = get_table_data(chart_data, product, metric)

            return {
                "header": [""] + table_data.columns[1:].to_list(),
                "body": table_data.to_dict(orient="records")
            }


class ChartData(APIView):
    def get(self, request, **kwargs):
        response = get_response(start_date=START_DATE, end_date=END_DATE,
                                product=kwargs["product"], sector=kwargs["sector"],
                                data_category="chart")
        return Response(response, status=status.HTTP_200_OK)


class TableData(APIView):
    def get(self, request, **kwargs):
        response = get_response(start_date=kwargs["startdate"], end_date=kwargs["enddate"],
                                product=kwargs["product"], sector=kwargs["sector"],
                                data_category="table", metric=kwargs["metric"])
        return Response(response, status=status.HTTP_200_OK)
