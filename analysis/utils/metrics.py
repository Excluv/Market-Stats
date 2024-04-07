import numpy as np
import pandas as pd


class MetricsCalculator:
    def __init__(self, records: pd.DataFrame, columns=None, set_name=None):
        # If the records are not wrapped as a Data Frame
        if type(records) is not pd.DataFrame:
            # Ensure column names are of lower cases
            records = pd.DataFrame.from_records(records)
            if columns:
                records.columns = map(str.lower, columns)
            if set_name:
                records.name = set_name

        self.data = records

    def _validate_metrics(self, metrics: list) -> dict:
        if type(metrics) is not list:
            raise Exception(f"metrics must be a list: {type(metrics)}")

        metrics_dict = {
            "cumulative_change": self._cumulative_change,
            "correlation": self._correlation,
        }
        for measurement in metrics:
            if measurement not in metrics_dict:
                raise Exception(f"Desired metric does not exist: {measurement}")

        return metrics_dict

    def _cumulative_change(self, data: pd.DataFrame) -> pd.DataFrame:
        cumulative_change = \
            data["value"].rolling(2).apply(
                lambda s: ((s.tail(1).values - s.head(1).values) / s.head(1).values) * 100
            ).cumsum().round(decimals=2).fillna(0)
        return cumulative_change

    def _correlation(self, data: pd.DataFrame) -> pd.DataFrame:
        correlation = data.corr(numeric_only=True).round(decimals=3)
        return correlation.reset_index()

    def _autocorrelation(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def _w_relative_change_distribution(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def _linear_regression(self, data: pd.DataFrame) -> pd.DataFrame:
        pass

    def calc(self, metrics: list) -> pd.DataFrame:
        metrics_dict = self._validate_metrics(metrics)
        result = dict()
        for measurement in metrics:
            result.update({
                measurement: metrics_dict[measurement](self.data)
            })
        return result
