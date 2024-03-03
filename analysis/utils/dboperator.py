import re
import os
import sqlite3
import pandas as pd

import bs4
from bs4 import BeautifulSoup


class HTMLHandler:
    def __init__(self, html_page):
        self.html_page = BeautifulSoup(html_page, "lxml")

    def _direct_children_count(self, html_tag: bs4.element.Tag) -> int:
        return len((html_tag.find_all(recursive=False)))

    def _get_measurement(self, value: str) -> str or None:
        measure_unit_dict = {
            "%": "Percentage",
            "K": "Thousand",
            "M": "Million",
            "B": "Billion",
            "T": "Trillion",
            "|": "Pct|Ratio",
            "-.-": "Vote",
            "Pass": "Vote",
            "Yes": "Vote",
            "Stay": "Vote",
            "No": "Vote",
            "Rejec": "Vote",
            "Reject": "Vote",
            "Leave": "Vote"
        }
        if value:
            for shorthand, unit in measure_unit_dict.items():
                characters_found = re.findall(shorthand, value)
                if characters_found:
                    if characters_found[0] != "":
                        return unit
            return "Real number"
        else:
            return "None"

    def _get_impact(self, html_tag: bs4.element.Tag) -> str or None:
        impact_dict = {
            "gra": "None",
            "yel": "Low",
            "ora": "Medium",
            "red": "High",
        }
        impact = html_tag.find("img")
        if impact:
            src_url = impact["src"].split(".")[-2][-3::1]
            return impact_dict.get(src_url)

        return None

    def _get_string_content(self, parent_tag: bs4.element.Tag,
                    child_tag_name: str, child_tag_attrs: dict) -> str or None:
        content = parent_tag.find(name=child_tag_name, attrs=child_tag_attrs)
        if content:
            content = list(content.stripped_strings)
            if len(content) > 1:
                return content[1]
            if len(content) > 0:
                return content[0]

        return None

    def _get_content(self, parent_tag: bs4.element.Tag, children_tags_dict: dict) -> list:
        if self._direct_children_count(parent_tag) < 10:
            return None

        # Add all available data that is wrapped inside the tags specified in the given dictionary
        measurement = "None"
        content_list = list()
        for key, value in children_tags_dict.items():
            content = self._get_string_content(parent_tag, value[0], value[1])
            content_list.append(content)
            if key == "value_actual":
                measurement = self._get_measurement(content)

        # Add news impact and measurement
        content_list.append(self._get_impact(parent_tag))
        content_list.append(measurement)

        return content_list

    def extract(self, parent_tag: str, children_tags_dict: dict, col_names: list) -> pd.DataFrame:
        data = list()
        generator = map(
            lambda x: self._get_content(x, children_tags_dict),
            self.html_page.find_all(parent_tag)
        )
        for data_row in generator:
            if data_row:
                data.append(data_row)

        # Transform the list into a Data Frame and fill the empty dates with values obtained from
        # the rows above them, this is because multiple news are wrapped inside a single date row
        data = pd.DataFrame(data, columns=col_names) \
                 .dropna(axis=0, thresh=3) \
                 .reset_index(drop=True)
        data["date"] = data["date"].ffill()

        return data


class DataNormalization:
    def __init__(self, data: pd.DataFrame, columns=None):
        if type(data) is not pd.DataFrame:
            data = pd.DataFrame(data)
            if not columns:
                raise Exception(f"""
                    The dataset must be a Data Frame with columns specified, 
                    current type = '{type(data)}' with columns = '{columns}'
                """)
        self.data = data

    def _normalize_date(self, year: str) -> None:
        self.data["date"] = self.data["date"].apply(
            lambda row: pd.to_datetime(year + " " + row, yearfirst=True).date()
        )

    def _normalize_data_order(self) -> None:
        self.data = self.data.sort_values(by=["date"])

    def _normalize_number(self, numeric_columns: list) -> None:
        special_characters_list = "[<%KMBTkmbt]"
        for column in numeric_columns:
            self.data[column] = self.data[column].str.replace(special_characters_list, "", regex=True)
            self.data[column] = self.data[column].str.split("|").str.get(0)

        # Handle special news with 'vote' measurement
        special_news_headlines = [
            "MPC Asset Purchase Facility Votes",
            "MPC Official Bank Rate Votes",
        ]
        for headline in special_news_headlines:
            data_row = self.data.query("title == @headline")
            if not data_row.empty:
                row_index = data_row.index.values
                for column in numeric_columns:
                    self.data.loc[row_index, column] = \
                        self.data.loc[row_index, column].str.split("-").str.join("")

        # Handle special news with string data
        special_positive_strings_list = ["Pass", "Yes", "Stay"]
        for string in special_positive_strings_list:
            for column in numeric_columns:
                self.data[column] = self.data[column].str.replace(string, "1", regex=True)

        special_negative_strings_list = ["Rejec", "Reject", "No", "Leave"]
        for string in special_negative_strings_list:
            for column in numeric_columns:
                self.data[column] = self.data[column].str.replace(string, "0", regex=True)

        self.data[numeric_columns].astype("float32")

    def clean(self, year: str, numeric_columns: list) -> pd.DataFrame:
        self._normalize_date(year)
        self._normalize_data_order()
        self._normalize_number(numeric_columns)

        return self.data


class DbAdapter:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def _validate_columns(self, table: str, columns: list) -> None:
        table_columns_dict = {
            "headline": ["title", "region", "measurement"],
            "release data": [
                "title", "region", "date", "value_actual",
                "value_previous", "value_forecast", "impact"
            ],
        }
        for col in table_columns_dict.get(table):
            if col not in columns:
                raise Exception(f"Missing data column '{col}'")

    def _remove_existing_records(self, table: str, data: pd.DataFrame) -> pd.DataFrame or None:
        if table == "headline":
            existing_records = self.cursor.execute(
                "SELECT title, region FROM analysis_newsheadline"
            ).fetchall()
            if len(existing_records) == 0:
                return data

            # Remove existing records by checking news titles and regions
            existing_records = list(map(lambda record: [record[0], record[1]], existing_records))
            for headline, region in existing_records:
                index = data.index[(data["title"] == headline) & (data["region"] == region)].tolist()
                if len(index) > 0:
                    data = data.drop(index, axis=0)
        else:
            for release_date in data["date"].unique():
                existing_record = self.cursor.execute(
                    "SELECT date FROM analysis_newsreleasedata WHERE date = ?", (release_date.strftime("%Y-%m-%d"), )
                ).fetchone()

                # Remove existing records by checking news date
                if existing_record:
                    data = data.query("date != @release_date")

        return data.reset_index(drop=True)

    def _get_last_index(self, table: str) -> int:
        query_dict = {
            "headline": "SELECT id FROM analysis_newsheadline ORDER BY id DESC LIMIT 1",
            "release data": "SELECT id FROM analysis_newsreleasedata ORDER BY id DESC LIMIT 1",
        }
        last_index = self.cursor.execute(query_dict[table]).fetchone()
        last_index = last_index[0] if last_index else 0

        return last_index

    def _insert_headline(self, table: str, headlines: pd.DataFrame) -> None:
        headlines = self._remove_existing_records(table, headlines)
        if headlines.shape[0] < 1:
            return None

        # Add id column to match that in DB, and the ids must start
        # from the number after the last index available in DB
        headlines = headlines.reset_index(names=["id"])
        headlines["id"] = headlines["id"] + 1 + self._get_last_index(table)

        headlines.to_sql(name="analysis_newsheadline", con=self.connection, if_exists="append", index=False)

    def _insert_release_data(self, table: str, release_data: pd.DataFrame) -> None:
        release_data = self._remove_existing_records(table, release_data)
        if release_data.shape[0] < 1:
            return None

        # Find and add headline id to every data record
        release_data["headline_id"] = release_data[["title", "region"]].apply(
            lambda record: self.cursor.execute(
                "SELECT id FROM analysis_newsheadline WHERE title = ? AND region = ?",
                (record.iloc[0], record.iloc[1])
            ).fetchone()[0],
            axis=1
        )

        release_data = release_data.drop(["title", "region"], axis=1)

        # Add id column to match that in DB, and the ids must start
        # from the number after the last index available in DB
        release_data = release_data.reset_index(names=["id"])
        release_data["id"] = release_data["id"] + 1 + self._get_last_index(table)

        release_data.to_sql(name="analysis_newsreleasedata", con=self.connection, if_exists="append", index=False)

    def insert_into(self, table: str, data: pd.DataFrame):
        method_dict = {
            "headline": self._insert_headline,
            "release data": self._insert_release_data,
        }
        if table not in method_dict:
            raise Exception("Specified table does not exist in DB")
        self._validate_columns(table, data.columns)

        method_dict[table](table, data)


class DbController:
    def __init__(self, connection):
        self.connection = connection

    def batch_insert(self, base_dir: str, tags_dict: dict, columns: list):
        base_dir = os.path.abspath(base_dir)
        for folder in os.listdir(base_dir):
            folder = os.path.join(base_dir, folder)
            for file in os.listdir(folder):

                with open(os.path.join(folder, file), "r+") as html_file:
                    data = HTMLHandler(html_file).extract("tr", tags_dict, columns)
                data = DataNormalization(data).clean(
                    year=file.split(".")[0][-4::1],
                    numeric_columns=["value_actual", "value_previous", "value_forecast"]
                )

                adapter = DbAdapter(self.connection)
                adapter.insert_into("headline", data[["title", "region", "measurement"]])
                adapter.insert_into(
                    "release data",
                    data[["title", "region", "value_actual", "value_forecast",
                          "impact", "date", "value_previous"]]
                )


if __name__ == "__main__":
    TAGS_DICT = {
        "date": ["td", {"class": "calendar__cell calendar__date"}],
        "title": ["span", {"class": "calendar__event-title"}],
        "region": ["td", {"class": "calendar__cell calendar__currency"}],
        "value_actual": ["td", {"class": "calendar__cell calendar__actual"}],
        "value_previous": ["td", {"class": "calendar__cell calendar__previous"}],
        "value_forecast": ["td", {"class": "calendar__cell calendar__forecast"}],
    }
    COLUMNS = [
        "date", "title", "region", "value_actual",
        "value_previous", "value_forecast", "impact", "measurement"
    ]
    DIR = ".\\Econ. News"

    with sqlite3.connect("db.sqlite3") as connection:
        controller = DbController(connection)
    controller.batch_insert(DIR, TAGS_DICT, COLUMNS)
