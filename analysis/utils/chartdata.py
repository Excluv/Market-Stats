from analysis.utils.dboperator import DbController
from analysis.utils.metrics import MetricsCalculator

import pandas as pd
from functools import reduce


def transform_date_format(data: pd.DataFrame) -> list:
    """
    Formats date strings to m-yy
    """
    data["date"] = pd.to_datetime(data["date"], yearfirst=True).apply(lambda date: date.strftime("%b-%y"))
    return data


class DataMixer:
    def __init__(self, start_date: str, end_date: str, controller: DbController):
        self.controller = controller
        self.start_date = start_date
        self.end_date = end_date

    def _get_news_mixed(self, news_list: list) -> list:
        """
        Gets a nested dictionary of news data in a given time range
        Parameters:
            news_list: list
                The list of news whose release data are to be fetched
        Returns:
            list
                A list of DataFrames containing data associated with each news given in the parameter
        """
        dataframes_list = list()
        for news in news_list:
            release_data = self.controller.fetch_records("release data", self.start_date,
                                                         self.end_date, "abbreviation", news)
            release_data = \
                pd.DataFrame.from_records(release_data, columns=["date", "value"]) \
                    .rename(columns={"value": news})
            release_data = transform_date_format(release_data)
            dataframes_list.append(release_data)

        return dataframes_list

    def _get_price_mixed(self, product: str, news_list: list) -> dict:
        """
        Gets a nested dictionary of price records and news data in a given time range
        Parameters:
            product: str
                The product whose price records are to be fetched
            news_list: list
                The list of news whose release data are to be fetched
        Returns:
            list
                A list of DataFrames containing data associated with the product and each news given in the parameter
        """
        dataframes_list = list()
        price_records = self.controller.fetch_records("price record", self.start_date,
                                                      self.end_date, "product", product)
        price_records = pd.DataFrame.from_records(price_records, columns=["date", product])
        price_records = transform_date_format(price_records)
        dataframes_list.append(price_records)

        # Retrieves data associated with each headline and appends them to the list
        for df in self._get_news_mixed(news_list):
            dataframes_list.append(df)

        return dataframes_list

    def get_mixed_data(self, mix_type: str, *args) -> dict:
        method_dict = {
            "prices and news": self._get_price_mixed,
            "news": self._get_news_mixed,
        }
        dataframes_list = method_dict[mix_type](*args)
        result = \
            reduce(
                lambda left_df, right_df: pd.merge(left_df, right_df, on=["date"], how="inner"),
                dataframes_list
            )

        return result.to_dict(orient="list")
