import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype

# Transforms pd.DateTimeIndex into pd.PeriodIndex
def to_week(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").week

def to_month(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").month

def to_year(date: pd.Series) -> pd.PeriodIndex:
    return pd.PeriodIndex(date, freq="D").year


def add_period(data: pd.DataFrame, period: str) -> pd.DataFrame:
    """
    Adds columns containing the time periods associated with data dates
    """
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
    """
    Provides a calculator to a set of given metrics
    """
    def __init__(self, records: pd.DataFrame, columns=None):
        # If the records are not wrapped as a Data Frame
        if type(records) is not pd.DataFrame:
            # Ensure column names are of lower cases
            columns = map(str.lower, columns)
            records = pd.DataFrame.from_records(records, columns=columns)

        # Sorts data records by date and assign
        self.data = records.sort_values(by=["date"])

    def _validate_period(self, period: str) -> str:
        """
        Checks if the period parameter is given correctly
        Parameters:
            period: str
                The period being examined
        Returns:
            str
                The lower case version of the given argument
        """
        allowed_periods_list = ["d", "w", "m", "y"]
        if period.lower() not in allowed_periods_list:
            raise Exception(f"Specified period is not allowed: {period}")

        return period.lower()

    def _validate_datetime(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Checks if the dataset contains a date column and it is of correct date format
        Parameters:
            data: pd.DataFrame
                The entire dataset being examined
        Returns:
            pd.DataFrame
                The dataset whose date column is of datetime data type
        """
        if (data["date"] != pd.Timestamp(0)).any():
            if not is_datetime64_any_dtype(data["date"]):
                data["date"] = pd.to_datetime(data["date"], yearfirst=True)
            return data
        else:
            raise Exception(f"Date column does not exist: {data.columns}")

    def _validate_metrics(self, metrics: list) -> dict:
        """
        Provides a mapping to a set of given metrics
        Parameters:
            metrics: list
                The set of metrics to be calculated
        Returns:
            dict
                A mapping to the methods where calculations will be made
        """
        if type(metrics) is not list:
            raise Exception(f"metrics must be a list: {type(metrics)}")

        metrics_dict = {
            "relative_change": self._relative_change,
            "absolute_change": self._absolute_change,
            "updown_ratio": self._updown_ratio,
            "volatility": self._volatility,
            "expected_return": self._expected_return,
        }
        for measurement in metrics:
            if measurement not in metrics_dict:
                raise Exception(f"Desired metric does not exist: {measurement}")

        return metrics_dict

    def _transform_data_period(self, period: str) -> pd.DataFrame:
        """
        Intermediary method. Adds the time period, asset class (type) and the product to each record in the original
        dataset. Then derives new data from each group of records that share the same set of some criteria.
        Parameters:
            period: str
                The period to be appended to the dataset (the original set)
        Returns:
            pd.DataFrame
                A transformed, grouped dataset with its columns containing new records derived from each of the groups
        """
        period = self._validate_period(period)
        data = self._validate_datetime(self.data)

        # Only adds columns if period is not daily
        if period == "d":
            return data.copy() # Calculations should only be performed on copies of the original dataset
        if period not in data.columns:
            data = add_period(data, period)

        # Groups data by product and period
        group = ["type", "product", "y", period] if period != "y" else ["type", "product", "y"]
        data = data.groupby(group).aggregate({"low": "min", "high": "max",
                                              "open": "first", "close": "last",
                                              "date": "last"})
        return data

    def _relative_change(self, data: pd.DataFrame) -> dict:
        """
        Calculates the mean daily relative change in a period of time
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        data["relative_change"] = (data["close"] - data["open"]) / data["open"]
        relative_change = \
            data.groupby(by=["product"])["relative_change"] \
                .mean(numeric_only=True) \
                .fillna(value=0) \
                .round(decimals=2) \
                .to_dict()
        return relative_change

    def _absolute_change(self, data: pd.DataFrame) -> dict:
        """
        Calculates the daily absolute change
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        grouped_data = data.groupby(by=["product"]).tail(2).groupby(by=["product"])["close"]
        absolute_change = (grouped_data.last() - grouped_data.first()).round(decimals=8).to_dict()
        return absolute_change

    def _updown_ratio(self, data: pd.DataFrame) -> dict:
        """
        Calculates the ratio between upward/downward daily changes
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        # Marks the days of upward prices as 1s and the others as 0s
        grouped_data = data.groupby(["product"])["close"]
        up_down = grouped_data.rolling(2).apply(
            lambda s: 1 if (s.tail(1).values - s.head(1).values) > 0 else 0
        )

        # Calculates the ratio
        updown_ratio = \
            up_down.groupby(["product"]) \
                .apply(
                    lambda s:
                        (s.where(s == 1).count() / abs(s.where(s == 0).count() - 1))
                        # Only perform calculation if the denominator is greater than 0
                        if  abs(s.where(s == 0).count() - 1) > 0 else 0
                ).fillna(value=0) \
                .round(decimals=2) \
                .to_dict()
        return updown_ratio

    def _log_return(self, data: pd.DataFrame) -> dict:
        """
        Calculates the daily logarithmic return rates
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        log_ror = \
            data.groupby(["product"])["close"] \
                .rolling(window=2) \
                .apply(
                    lambda s: np.log(s.tail(1).values / s.head(1).values)
                ).reset_index() \
                .rename(columns={"level_1": "index", "close": "log_ror"})
        return log_ror

    def _volatility(self, data: pd.DataFrame) -> dict:
        """
        Calculates the annual volatility of daily logarithmic return rates with the assumption that there are 252
        trading days for every product being calculated
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        log_ror = self._log_return(data)
        data = pd.merge(log_ror, data.reset_index(), on=["product", "index"])
        volatility = \
            data.groupby(["product"])["log_ror"] \
                .apply(lambda x: x.std() * np.sqrt(252)) \
                .fillna(value=0) \
                .round(decimals=2) \
                .to_dict()
        return volatility

    def _expected_return(self, data: pd.DataFrame) -> dict:
        """
        Calculates the annual expected logarithmic return rate
        Parameters:
            data: pd.DataFrame
                A dataset where its records are associated with appropriate asset classes, products, and time periods
        Returns:
            dict
                A nested dictionary of the calculation results
        """
        log_ror = self._log_return(data)
        data = pd.merge(log_ror, data.reset_index(), on=["product", "index"])
        expected_return = \
            data.groupby(["product"])["log_ror"] \
                .apply(lambda x: x.mean() * 252) \
                .fillna(value=0) \
                .round(decimals=2) \
                .to_dict()
        return expected_return

    def calc(self, metrics: list, periods: list) -> list:
        """
        Intermediary method. Calculates a set of metrics based on a set of time periods.
        Parameters:
            metrics: list
                The list of metrics to be calculated
            periods: list
                The time periods in which metrics are to be calculated
        Returns:
            list
                A list of nested dictionaries, each of which represents the calculation result according to a metric
        """
        metrics_dict = self._validate_metrics(metrics)
        results = list()
        for period in periods:
            data = self._transform_data_period(period)

            # Calculates and stores the results in a dictionary
            calculations = dict()
            for measurement in metrics:
                calculations.update({
                    measurement: metrics_dict[measurement](data),
                })
            results.append({period: calculations})

        return results
