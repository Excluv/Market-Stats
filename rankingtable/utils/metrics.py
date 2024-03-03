import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

# Transform pd.DateTimeIndex into pd.PeriodIndex
def to_week(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").week

def to_month(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").month

def to_year(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").year

# Add columns of specified periods
def add_period(data: pd.DataFrame, period: str) -> pd.DataFrame:
    period_dict = {
        "w": to_week,
        "m": to_month,
        "y": to_year,
    }
    data["y"] = period_dict["y"](data["date"])
    if period != "y":
        data[period] = period_dict[period](data["date"])

    return data


class MetricsCalculator:
    def __init__(self, records: pd.DataFrame, columns=None):
        # If the records are not wrapped as a Data Frame
        if type(records) is not pd.DataFrame:
            records = pd.DataFrame.from_records(records)

            # Ensure column names are of lower cases
            columns = map(str.lower, columns)
            records.columns = columns

        # Sort data records by date and assign
        self.data = records.sort_values(by=["date"])

    def _validate_period(self, period: str) -> str:
        allowed_periods_list = ["d", "w", "m", "y"]
        if period.lower() not in allowed_periods_list:
            raise Exception(f"Specified period is not allowed: {period}")

        return period.lower()

    def _validate_datetime(self, data: pd.DataFrame) -> pd.DataFrame:
        if (data["date"] != pd.Timestamp(0)).any():
            if not is_datetime64_any_dtype(data["date"]):
                data["date"] = pd.to_datetime(data["date"], yearfirst=True)

            return data
        else:
            raise Exception(f"Date column does not exist: {data.columns}")

    def _validate_metrics(self, metrics: list) -> dict:
        if type(metrics) is not list:
            raise Exception(f"metrics must be a list: {type(metrics)}")

        metrics_dict = {
            "relative_change": self._relative_change,
            "absolute_change": self._absolute_change,
            "updown_ratio": self._updown_ratio,
            "volatility": self._volatility,
            "expected_return": self._expected_return,
            # "beta_measure": self._beta_measure,
            # "nearest_extremes": self._nearest_extremes,
        }
        for measurement in metrics:
            if measurement not in metrics_dict:
                raise Exception(f"Desired metric does not exist: {measurement}")

        return metrics_dict

    def _transform_data_period(self, period: str) -> pd.DataFrame:
        period = self._validate_period(period)
        data = self._validate_datetime(self.data)

        # Only add columns if period is not daily
        if period == "d":
            return data.copy() # Calculations should only be performed on copies of the original dataset
        if period not in data.columns:
            data = add_period(data, period)

        # Group data by product and period
        group = ["type", "product", "y", period] if period != "y" else ["type", "product", "y"]
        data = data.groupby(group).aggregate(
            {"low": "min", "high": "max", "open": "first", "close": "last", "date": "last"}
        )

        return data

    def _relative_change(self, data: pd.DataFrame) -> dict:
        data["relative_change"] = data.groupby(by=["product"])["close"].diff().div(data["close"])
        relative_change = data.groupby(by=["product"]) \
                            .mean(numeric_only=True)["relative_change"] \
                            .fillna(value=0) \
                            .round(decimals=2) \
                            .to_dict()

        return relative_change

    def _absolute_change(self, data: pd.DataFrame) -> dict:
        # Calculate 24h change
        grouped_data = data.groupby(by=["product"]).tail(2).groupby(by=["product"])["close"]
        absolute_change = (grouped_data.last() - grouped_data.first()).round(decimals=4).to_dict()

        return absolute_change

    def _updown_ratio(self, data:pd.DataFrame) -> dict:
        # Find the up and down days and marks them as 1 and 0, respectively
        grouped_data = data.groupby(["product"])["close"]
        up_down = grouped_data.rolling(2).apply(lambda s: 1 if (s.head(1).values - s.tail(1).values) > 0 else 0)

        # Calculate the ratio of up/down
        updown_ratio = up_down.groupby(["product"]) \
                            .apply(lambda s: \
                                     (s.where(s == 1).count() / abs(s.where(s == 0).count() - 1)) if \
                                     # Only perform calculation if the denominator is greater than 0
                                     abs(s.where(s == 0).count() - 1) > 0 else 0
                            ).fillna(value=0) \
                            .round(decimals=2) \
                            .to_dict()

        return updown_ratio

    def _volatility(self, data: pd.DataFrame) -> dict:
        # Calculate the daily logarithmic rate of return
        log_ror = data.groupby(["product"])["close"] \
                    .rolling(window=2) \
                    .apply(lambda s: np.log(s.tail(1).values / s.head(1).values))
                    # .apply(lambda s: np.log(s.tail(1).values / s.head(1).values))
        log_ror = log_ror.reset_index().rename(columns={"level_1": "index", "close": "log_ror"})

        # Merge the result with the original dataset and calculate
        data = pd.merge(log_ror, data.reset_index(), on=["product", "index"])
        volatility = data.groupby(["product"])["log_ror"] \
                        .apply(lambda x: x.std() * np.sqrt(252)) \
                        .fillna(value=0) \
                        .round(decimals=2) \
                        .to_dict()

        return volatility

    def _expected_return(self, data: pd.DataFrame) -> dict:
        # Calculate the daily logarithmic rate of return
        log_ror = data.groupby(["product"])["close"] \
                    .rolling(window=2) \
                    .apply(lambda s: np.log(s.tail(1).values / s.head(1).values))
        # .apply(lambda s: np.log(s.tail(1).values / s.head(1).values))
        log_ror = log_ror.reset_index().rename(columns={"level_1": "index", "close": "log_ror"})

        # Merge the result with the original dataset and calculate
        data = pd.merge(log_ror, data.reset_index(), on=["product", "index"])
        expected_return = data.groupby(["product"])["log_ror"] \
                        .apply(lambda x: x.mean() * 252) \
                        .fillna(value=0) \
                        .round(decimals=2) \
                        .to_dict()

        return expected_return

    # def _beta_measure(self, data: pd.DataFrame) -> dict:
    #     grouped_data = data.groupby(["product"])["close"]
    #     return_rate = (grouped_data.last() - grouped_data.first()) / grouped_data.first()
    #
    #     # Declares default parameters and calculate
    #     RISKFREE = 0.06 * grouped_data.size().max() / 365
    #     BENCHMARK = 0.1 * grouped_data.size().max() / 365
    #     beta_measure = ((return_rate - RISKFREE) / (BENCHMARK - RISKFREE)).round(decimals=2).to_dict()
    #
    #     return beta_measure

    # def _nearest_extremes(self, data: pd.DataFrame) -> dict:
    #     # Find the extremes
    #     grouped_data = data.groupby(["product"])
    #     nearest_extremes = grouped_data.aggregate({"low": "min", "high": "max"})
    #
    #     # Calculate the differences from the current price to the extremes
    #     current_value = grouped_data["close"].last()
    #     relative_decrease = ((current_value - nearest_extremes["high"]) / nearest_extremes["high"]) \
    #                             .mul(100).round(decimals=2) \
    #                             .rename("relative_decrease")
    #     relative_increase = ((current_value - nearest_extremes["low"]) / nearest_extremes["low"]) \
    #                             .mul(100).round(decimals=2) \
    #                             .rename("relative_increase")
    #     nearest_extremes = pd.merge(relative_decrease, relative_increase, on=["product"]) \
    #                             .apply(lambda x: str(x[0]) + " / " + str(x[1]), axis=1, raw=True) \
    #                             .rename("nearest_extremes") \
    #                             .to_dict()
    #
    #     return nearest_extremes

    def calc(self, metrics: list, periods: list) -> list:
        metrics_dict = self._validate_metrics(metrics)
        results = list()
        for period in periods:
            data = self._transform_data_period(period)

            # Calculate and store the results in a dictionary
            calculations = dict()
            for measurement in metrics:
                calculations.update({
                    measurement: metrics_dict[measurement](data),
                })
            results.append({
                period: calculations,
            })

        return results
