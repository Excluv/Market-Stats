import os
import sqlite3
import pandas as pd
from datetime import datetime


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

    def _normalize_date(self, default_start_date="2010-01-01") -> None:
        default_start_date = pd.to_datetime(default_start_date, yearfirst=True).date()

        # Converts date stings into datetime objects
        try:
            # Checks if a date string is of yyyy-mm-dd format
            datetime.strptime(self.data.loc[0, "date"], "%Y-%m-%d")
            self.data.loc[:, "date"] = pd.to_datetime(self.data["date"], yearfirst=True).dt.date
        except ValueError:
            self.data.loc[:, "date"] = pd.to_datetime(self.data["date"], dayfirst=True).dt.date

        # Retains only records that are dated from the default_start_date onwards
        self.data = self.data.query("date >= @default_start_date")

    def _normalize_data_order(self) -> None:
        self.data = self.data.sort_values(by=["date"])

    def clean(self, default_start_date="2010-01-01") -> pd.DataFrame:
        self._normalize_date(default_start_date="2010-01-01")
        self._normalize_data_order()

        return self.data


class DbAdapter:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def _validate_columns(self, table: str, columns: list) -> None:
        table_columns_dict = {
            "headline": ["title", "region", "measurement", "sector"],
            "release data": ["date", "value"],
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

            # Removes existing records by checking news titles and regions
            existing_records = list(map(lambda record: [record[0], record[1]], existing_records))
            for headline, region in existing_records:
                index = data.index[(data["title"] == headline) & (data["region"] == region)].tolist()
                if len(index) > 0:
                    data = data.drop(index, axis=0)

            return data.reset_index(drop=True)
        else:
            dataset_name = list(map(str.strip, data.name.split("-")))

            headline_id = self.cursor.execute(
                "SELECT id FROM analysis_newsheadline WHERE title = ? AND region = ?",
                (dataset_name[0], dataset_name[1])
            ).fetchone()[0]

            # Inserts only the records whose dates are newer than those existing in DB
            last_existing_date = self.cursor.execute(
                "SELECT MAX(date) FROM analysis_newsreleasedata WHERE headline_id = ?", (headline_id,)
            ).fetchone()

            # Skips this step if the records of a particular product haven't been inserted yet
            if last_existing_date[0]:
                last_existing_date = pd.to_datetime(last_existing_date[0], yearfirst=True).date()
                data = data.query("date > @last_existing_date")

            return data.reset_index(drop=True), headline_id  # For later use

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

        # Adds id column to match that in DB, and the ids must start
        # from the number after the last index available in DB
        headlines["id"] = headlines.reset_index(names=["id"])["id"] + 1 + self._get_last_index(table)

        headlines.to_sql(name="analysis_newsheadline", con=self.connection, if_exists="append", index=False)

    def _insert_release_data(self, table: str, release_data: pd.DataFrame) -> None:
        release_data, headline_id = self._remove_existing_records(table, release_data)
        if release_data.shape[0] < 1:
            return None

        # Adds head line id to the dataset
        release_data.loc[:, "headline_id"] = headline_id

        # Adds id column to match that in DB, and the ids must start
        # from the number after the last index available in DB
        release_data["id"] = release_data.reset_index(names=["id"])["id"] + 1 + self._get_last_index(table)

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


class DataReader:
    def __init__(self, connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def fetch_headline_records(self, by="", arg="") -> list:
        query_dict = {
            "": "",
            "sector": "sector",
            "title": "title",
            "abbreviation": "abbreviation",
        }

        # Executes query with situational arguments
        query = f"WHERE {query_dict.get(by)} = ?" if by != "" else ""
        param = [arg] if arg != "" else []
        self.cursor.execute(f"""
            SELECT id, title, measurement, definition 
            FROM analysis_newsheadline 
            {query}
        """, param)

        return self.cursor.fetchall()

    def fetch_releasedata_records(self, start_date: str, end_date: str, by="", arg="") -> list:
        query_dict = {
            "": "",
            "title": "headline.title",
            "abbreviation": "headline.abbreviation"
        }
        query = f"{query_dict.get(by)} = ? AND" if by != "" else ""
        params_list = [arg, start_date, end_date] if by != "" else [start_date, end_date]
        self.cursor.execute(f"""
            SELECT record.date, record.value
            FROM
                analysis_newsheadline AS headline
                JOIN analysis_newsreleasedata AS record
            ON record.headline_id = headline.id
            WHERE
                {query}
                record.date >= ? AND record.date <= ?
            ORDER BY record.date ASC
        """, params_list)

        return self.cursor.fetchall()

    def fetch_price_records(self, start_date: str, end_date: str, by="", arg="") -> list:
        # Executes query with situational arguments
        query_dict = {
            "": "",
            "product": "product.name",
        }
        query = f"{query_dict.get(by)} = ? AND" if by != "" else ""
        params_list = [arg, start_date, end_date] if by != "" else [start_date, end_date]
        self.cursor.execute(f"""
            SELECT record.date, record.close
            FROM
                rankingtable_pricerecord AS record
                JOIN rankingtable_product AS product
            ON record.product_id = product.id
            WHERE
                {query}
                record.date >= ? AND record.date <= ?
            GROUP BY 
                strftime('%Y', record.date), 
                strftime('%m', record.date)
            HAVING MAX(record.close)
            ORDER BY record.date ASC
        """, params_list)

        return self.cursor.fetchall()


class DbController:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def fetch_records(self, record_type: str, *args):
        reader = DataReader(self.connection)
        method_dict = {
            "headline": reader.fetch_headline_records,
            "release data": reader.fetch_releasedata_records,
            "price record": reader.fetch_price_records,
        }
        return method_dict.get(record_type)(*args)

    def insert_records(self, table: str, dir: str) -> None:
        adapter = DbAdapter(self.connection)

        # Data associated with a head line is specified in the folder and file names
        if table == "headline":
            data = list()
            sector = dir.split("\\")[-1]
            for FILE_NAME in os.listdir(dir):
                strings = FILE_NAME.split("\\")[-1].split(".")[0].split("-")
                strings = list(map(str.strip, strings))
                title, region, measurement = strings[0], strings[1], strings[2]
                data.append([title, region, measurement, sector])

            data = pd.DataFrame(data, columns=["title", "region", "measurement", "sector"])

        if table == "release data":
            try:
                data = pd.read_csv(dir, names=["date", "value"], skiprows=[0])
            except UnicodeDecodeError:
                print(f"File must be of CSV format '{dir}'")
                return None

            data = DataNormalization(data).clean()
            data.name = dir.split("\\")[-1].split(".")[0]

        adapter.insert_into(table, data)
        print(f"Successfully inserted: {dir}")

    def batch_insert(self, source: str, dir=None) -> None:
        if source == "local":
            if dir is None:
                raise Exception("Please specify the local directory where data is stored")

            # Inserts news headlines
            self.insert_records("headline", dir)

            # Inserts product data
            for file in os.listdir(dir):
                file_dir = os.path.join(dir, file)
                self.insert_records("release data", file_dir)
