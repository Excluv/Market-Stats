from datetime import datetime
from pathlib import Path
import yfinance as yf
import pandas as pd
import sqlite3
import os


class DbAdapter:
    """
    Provides functionalities to insert different types of data into DB
    """
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def _validate_data_format(self, table: str, data) -> Exception:
        """
        Checks if the types of data are of correct ones
        Parameters:
            table: str
                The name of the DB table, into which data is to be inserted
            data: list or DataFrame or Series
                The raw dataset
        Returns:
            Exception
                Raises Exceptions based on fed parameters
        """
        if table == "asset class":
            if type(data) is not list:
                raise Exception(f"Data to be inserted in this table '{table}' must be wrapped in a list")

        if table == "product":
            if type(data) is not pd.Series:
                raise Exception(f"Data to be inserted in this table '{table}' must be wrapped in a Series")

        if table == "price record":
            if type(data) is not pd.DataFrame:
                raise Exception(f"Data to be inserted in this table '{table}' must be wrapped in a Data Frame")

    def _validate_data_attribute(self, table: str, data) -> Exception or None:
        """
        Checks if the dataset contains the necessary attributes, such as name (used for data of product and
        price record types to identify the group to which it belongs), and if the name already exists in DB
        (which will be later used to create reference - foreign key)
        Parameters:
            table:
                The name of the DB table, into which data is to be inserted
            data: list or Series or DataFrame
                The dataset
        Returns:
            None if the required attribute is found and already existed in DB
            Raises Exception otherwise
        """
        if (data.name is None) or (data.name == ""):
            raise Exception(f"""
                The dataset must have a name representing the asset class or 
                product, to which it belongs. Current: {data.name}
            """)
        else:
            if table == "product":
                self.cursor.execute("SELECT name FROM rankingtable_assetclass WHERE name = ?",(data.name, ))

            if table == "price record":
                self.cursor.execute("SELECT symbol FROM rankingtable_product WHERE symbol = ?",(data.name, ))

            if self.cursor.fetchone()[0] is None:
                raise Exception(f"The specified product '{data.name}' does not exist in DB")

    def _remove_existing_records(self, table: str, data: list or pd.DataFrame) -> list or pd.DataFrame:
        """
        Removes records that are the duplicates of those in DB
            table:
                The name of the DB table, into which data is to be inserted
            data: list or DataFrame
                The dataset
        Returns:
            list
                A list of tuples containing either new product or new asset class records
            DataFrame
                A DataFrame containing new price records
        """
        if table == "price record":
            product_id = \
                self.cursor.execute(
                    "SELECT id FROM rankingtable_product WHERE symbol = ?", (data.name,)
                ).fetchone()[0]

            # Insert only the records whose dates are newer than those existing in DB
            last_existing_date = \
                self.cursor.execute(
                    "SELECT MAX(date) FROM rankingtable_pricerecord WHERE product_id = ?", (product_id,)
                ).fetchone()

            # Skip this step if the records of a particular product haven't been inserted yet
            if last_existing_date[0]:
                last_existing_date = pd.to_datetime(last_existing_date[0], yearfirst=True).date()
                data = data.query("date > @last_existing_date")

            return data
        else:
            query_dict = {
                "asset class": "SELECT name FROM rankingtable_assetclass",
                "product": "SELECT symbol FROM rankingtable_product",
            }
            existing_records = self.cursor.execute(query_dict[table]).fetchall()
            existing_records = list(map(lambda record: record[0], existing_records))

            # Pick records that are new into a list
            nonexisting_records = list()
            for record in data:
                if record not in existing_records:
                    nonexisting_records.append(record)

            return nonexisting_records

    def _get_last_index(self, table: str) -> int:
        """
        Gets the last index of a table in DB, new data must be concatenated from the tail of the dataset
        Parameters:
            table: str
                The name of the DB table, into which data is to be inserted
        Returns:
            int
                The index of the last record in a table, 0 if the table is empty
        """
        query_dict = {
            "asset class": "SELECT id FROM rankingtable_assetclass ORDER BY id DESC LIMIT 1",
            "product": "SELECT id FROM rankingtable_product ORDER BY id DESC LIMIT 1",
            "price record": "SELECT id FROM rankingtable_pricerecord ORDER BY id DESC LIMIT 1",
        }
        last_index = self.cursor.execute(query_dict[table]).fetchone()
        last_index = last_index[0] if last_index else 0

        return last_index

    def _insert_asset_class(self, table: str, asset_classes: list) -> None:
        """
        Inserts asset class data into DB
        Parameters:
            table: str
                The name of the DB table, into which data is to be inserted
            asset_classes: list
                A list containing asset class data
        Returns:
            None
                Data is inserted directly into DB
        """
        # Reconstruct the dataset with only non-existing records
        asset_classes = self._remove_existing_records(table, asset_classes)
        if len(asset_classes) < 1:
            return None

        # Transform the dataset into the appropriate format, ready for db-insertion
        asset_classes = pd.DataFrame({"name": asset_classes}).reset_index(names=["id"])

        # New records must continue from the last index
        asset_classes["id"] = asset_classes["id"] + 1 + self._get_last_index(table)

        asset_classes.to_sql(name="rankingtable_assetclass", con=self.connection, if_exists="append", index=False)

    def _insert_product(self, table: str, products: pd.Series) -> None:
        """
        Inserts product data into DB
        Parameters:
            table: str
                The name of the DB table, into which data is to be inserted
            products: list
                A list containing product data
        Returns:
            None
                Data is inserted directly into DB
        """
        # Reconstruct the dataset with only non-existing records
        asset_class = products.name
        products = pd.Series(self._remove_existing_records(table, products.values))
        products.name = asset_class
        if len(products) < 1:
            return None

        # Transform the dataset into the appropriate format, ready for db-insertion
        products = products.reset_index().rename(columns={"index": "id", f"{asset_class}": "symbol"})

        # New records must continue from the last index
        products["id"] = products["id"] + 1 + self._get_last_index(table)

        # Find and insert the corresponding foreign key
        products["assetclass_id"] = \
            self.cursor.execute(
                "SELECT id FROM rankingtable_assetclass WHERE name = ?", (asset_class, )
            ).fetchone()[0]

        products.to_sql(name="rankingtable_product", con=self.connection, if_exists="append", index=False)

    def _insert_price_record(self, table: str, price_records: pd.DataFrame) -> None:
        """
        Inserts price data into DB
        Parameters:
            table: str
                The name of the DB table, into which data is to be inserted
            price_records: list
                A list containing price records
        Returns:
            None
                Data is inserted directly into DB
        """
        # Reconstruct the dataset with only non-existing records
        product = price_records.name
        price_records = self._remove_existing_records(table, price_records)
        if len(price_records) < 1:
            return None

        # Transform the dataset into the appropriate format, ready for db-insertion
        price_records = price_records.reset_index(names=["id"])

        if price_records.loc[0, "id"] > 0:
            price_records["id"] -= price_records["id"].min()

        # New records must continue from the last index
        price_records["id"] = price_records["id"] + 1 + self._get_last_index(table)

        # Find and insert the corresponding foreign key
        price_records["product_id"] = \
            self.cursor.execute(
                "SELECT id FROM rankingtable_product WHERE symbol = ?", (product, )
            ).fetchone()[0]

        price_records.to_sql(name="rankingtable_pricerecord", con=self.connection, if_exists="append", index=False)

    def insert_into(self, table: str, data: list or pd.Series or pd.DataFrame) -> None:
        """
        Calls the appropriate method based on the given parameters
        Parameters:
             table: str
                The name of the DB table, into which data is to be inserted
             data: list or Series or DataFrame
                The dataset to be inserted into DB
        Returns:
            None
        """
        method_dict = {
            "asset class": self._insert_asset_class,
            "product": self._insert_product,
            "price record": self._insert_price_record,
        }
        if table not in method_dict:
            raise Exception("Specified table does not exist in DB")
        self._validate_data_format(table, data)

        if table != "asset class":
            self._validate_data_attribute(table, data)

        method_dict[table](table, data)


class DataNormalization:
    """
    Normalizes raw data from CSV files to match that in DB
    """
    def __init__(self, data, columns=None):
        if type(data) is not pd.DataFrame:
            data = pd.DataFrame(data)
            if not columns:
                raise Exception(f"""
                    The dataset must be a Data Frame with columns specified, 
                    current type = '{type(data)}' with columns = '{columns}'
                """)
        self.data = data

    def _normalize_columns(self, columns_to_keep: list) -> None:
        """
        Removes unneeded columns and lower the names of others
        Parameters:
            columns_to_keep: list
                The list of wanted columns
        Returns:
            None
                Directly affects the original dataset
        """
        self.data.columns = self.data.columns.str.lower()
        self.data = self.data[columns_to_keep]

    def _normalize_date(self, default_start_date="2010-01-01") -> None:
        """
        Slices the dataset to begin from a specified date, then transforms strings into DateTime
        objects, but only retains the date part.
        Parameters:
            default_start_date: str
                The begin of the slice of the dataset to be retained
        Returns:
            None
                Directly affects the original dataset
        """
        default_start_date = pd.to_datetime(default_start_date, yearfirst=True, utc=True).date()

        # Since the raw date column often contains both date and time
        self.data.loc[:, "date"] = self.data["date"].str.split().str.get(0)

        # Convert date stings into datetime objects
        try:
            # Check if a date string is of yyyy-mm-dd format
            datetime.strptime(self.data.loc[0, "date"], "%Y-%m-%d")
            self.data.loc[:, "date"] = pd.to_datetime(self.data["date"], yearfirst=True, utc=True).dt.date
        except ValueError:
            self.data.loc[:, "date"] = pd.to_datetime(self.data["date"], dayfirst=True, utc=True).dt.date

        # Retain only records that are dated from the default_start_date onwards
        self.data = self.data.query("date >= @default_start_date")

    def _normalize_data_order(self) -> None:
        """
        Sorts the dataset by date
        Parameters:
            None
        Returns:
            None
                Directly affects the original dataset
        """
        self.data = self.data.sort_values(by=["date"])
        self.data = self.data.reset_index(drop=True)

    def _normalize_data_format(self, numeric_type_columns: list) -> None:
        """
        Transforms numeric data by nature but is currenty formatted as strings into numpy.float64,
        which is also the format of other numeric data in the current DB. Afther the data type conversion,
        rounds up the decimals to an appropriate place based on all of the records' values
        Parameters:
            numeric_type_columns: list
                The names of the columns containing numerical data
        Returns:
            None
                Directly affects the original dataset
        """
        # In case data is supposed to be numbers but was incorrectly formatted
        numeric_data = self.data.select_dtypes("number")

        if numeric_data.empty:
            for column in numeric_type_columns:
                if column not in self.data.columns:
                    raise Exception(f"Invalid column name '{column}'")
                self.data.loc[:, column] = self.data[column].str.split(",").str.join("")
                self.data.loc[:, column] = self.data[column].str.split(" ").str.join("")

        # Change the data types of columns to be the same to those in DB, should they be manually inserted
        for column in numeric_data.columns:
            self.data[column].astype("float64")

            # Round up the decimals to the appropriate nth place
            series = self.data[column].copy()
            for pow in range(6):
                series_min = series.min().astype("int16")
                series_max = series.max().astype("int16")
                if (series_min >= 1) or (series_min <= 1 and series_max >= 20):
                    self.data.loc[:, column] = series.round(decimals=2).where(series != 0, pd.NA)
                    break

                # For super small valued products
                if (series.min() * 10 ** pow) < 1:
                    self.data.loc[:, column] = series.round(decimals=abs(pow + 2)).where(series != 0, pd.NA)

    def _remove_duplicates(self) -> None:
        """
        Removes duplicated data rows based on the set of all five columns, date and OHLC
        Parameters:
            None
        Returns:
            None
                Directly affects the original dataset
        """
        self.data = self.data.drop_duplicates(subset=["date"])

    def _handle_missing_data(self) -> None:
        """
        Removes a data row if there's any of the cells in that row is empty, price data must be adaquate
        Parameters:
            None
        Returns:
            None
                Directly affects the original dataset
        """
        if self.data.isnull().values.any():
            self.data = self.data.dropna(how="any")

    def clean(self, default_start_date="2010-01-01") -> pd.DataFrame:
        """
        Calls a specific sequence of methods to normalize the dataset
        Parameters:
            None
        Returns:
            DataFrame
                The normalzied version of the original dataset
        """
        self._normalize_columns(["date", "open", "high", "low", "close"])
        self._normalize_date(default_start_date)
        self._normalize_data_order()
        self._normalize_data_format(["open", "high", "low", "close"])
        self._remove_duplicates()
        self._handle_missing_data()

        return self.data


class DataReader:
    """
    Provides functionalities to get data from the DB
    """
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.cursor = connection.cursor()

    def fetch_assetclass_records(self, name="") -> list:
        """
        Gets records of product categories available in DB
        Parameters:
            name: str
                The name of the category
        Returns:
            list
                A list containing tuples of data records
        """
        # Execute query with situational arguments
        query = "WHERE name = ?" if name != "" else ""
        param_list = [name] if name != "" else []
        self.cursor.execute(f"SELECT id, name FROM rankingtable_assetclass {query}", param_list)

        return self.cursor.fetchall()

    def fetch_product_records(self, symbol="") -> list:
        """
        Gets records of products available in DB
        Parameters:
            symbol: str
                The presentational symbol of a product
        Returns:
            list
                A list containing tuples of data records
        """
        # Execute query with situational arguments
        query = "WHERE symbol = ?" if symbol != "" else ""
        param_list = [symbol] if symbol != "" else []
        self.cursor.execute(f"""
            SELECT id, name, assetclass_id, symbol, alias 
            FROM rankingtable_product
            {query}
        """ , param_list)

        return self.cursor.fetchall()

    def fetch_price_records(self, start_date: str, end_date: str, by="", arg="") -> list:
        """
        Gets data records from DB using optional parameters
        Parameters:
            start_date: str
                The date from which price records are to be fetched
            end_date: str
                The date to which price records are to be fetched
            by: str
                The identifier of which group of price records should be fetched
            arg: str
                The value of the identifier
        Returns:
            list
                A list containing tuples of data records
        """
        # Execute query with situational arguments
        query_dict = {
            "": "",
            "asset class": "assetclass.name",
            "product": "product.symbol",
        }
        query = f"{query_dict.get(by)} = ? AND" if by != "" else ""
        params_list = [arg, start_date, end_date] if by != "" else [start_date, end_date]
        self.cursor.execute(f"""
            SELECT
                assetclass.name, product.name, product.symbol, record.date,
                record.open, record.high, record.low, record.close
            FROM
                rankingtable_pricerecord AS record
                JOIN rankingtable_product AS product
                JOIN rankingtable_assetclass AS assetclass
            ON
                record.product_id = product.id
                AND product.assetclass_id = assetclass.id
            WHERE
                {query}
                record.date >= ? AND record.date <= ?
        """, params_list)

        return self.cursor.fetchall()

    def fetch_latest_date_records(self) -> list:
        """
        Gets the most recent records available in DB
        Parameters:
            None
        Returns:
            list
                A list containing tuples of data records
        """
        self.cursor.execute(f"""
            SELECT assetclass.name, product.symbol, product.alias, MAX(record.date)
            FROM 
                rankingtable_assetclass AS assetclass
                JOIN rankingtable_pricerecord AS record
                JOIN rankingtable_product AS product 
            ON 
                assetclass.id = product.assetclass_id
                AND record.product_id = product.id 
            GROUP BY product.symbol 
        """)
        date_records = self.cursor.fetchall()

        return date_records


class DbController:
    """
    The interface between the App and DB operations
    """
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def _is_empty(self, FILE_DIR: str) -> bool:
        """
        Checks if the specified file is empty or does not exist
        Parameters:
            FILE_DIR: str
                The directory of the file
        Returns
            False if there's data in the file
            True otherwise
        """
        try:
            file = pd.read_csv(FILE_DIR)
            if file.shape[0] < 2:
                return True
            return False
        except pd.errors.EmptyDataError:
            return True
        except FileNotFoundError:
            return True

    def _up_to_date(self, FILE_DIR: str, asset_class: str, end_date: datetime) -> bool or None:
        """
        Checks whether the CSV file contains up-to-date records
        Parameters:
            FILE_DIR: str
                The directory of the file containing data records
            asset_class: str
                The category of data records
            end_date: str
                The end date of the range of records to be downloaded when download_csv
                is called, represents the current date (today) by default
        Returns:
            None
                If no end date is specified
            bool
                True if the dataset is up to date
                False otherwise
        """
        if not end_date:  # Only perform the check if end_date is explicitly specified
            return None

            # The last record in the CSV file has the most recent date
        last_date_csv = pd.read_csv(FILE_DIR).tail(1)["Date"].values
        last_date_csv = pd.to_datetime(last_date_csv, utc=True).date[0]

        # Cryptocurrency data is continuously updated everyday, while other
        # asset classes stop trading on every Saturday and Sunday
        last_trading_day = end_date - pd.to_timedelta(1, unit="D")
        if asset_class != "Cryptocurrency":
            timedelta_dict = {
                0: pd.to_timedelta(2, unit="D"),
                6: pd.to_timedelta(1, unit="D"),
            }
            weekday = end_date.weekday()
            if weekday in timedelta_dict:
                last_trading_day = last_trading_day - timedelta_dict.get(weekday)

        if last_date_csv == last_trading_day:
            return True

        return False

    def fetch_records(self, record_type: str, *args) -> list:
        """
        Creates a DataReader object and fetch records of a specified category from DB
        Parameters:
            record_type: str
                The category of data records to be fetched
            *args:
                Varies upon the call of a particular method
        Returns:
            list
                A list of tuples containing records fetched from DB
        """
        reader = DataReader(self.connection)
        method_dict = {
            "asset class": reader.fetch_assetclass_records,
            "product": reader.fetch_product_records,
            "price record": reader.fetch_price_records,
            "latest date": reader.fetch_latest_date_records,
        }
        return method_dict.get(record_type)(*args)

    def insert_records(self, table: str, dir: str) -> None:
        """
        Inserts data of a specified type that is stored inside a directory into DB
        Parameters:
            table: str
                The DB table into which data is inserted
            dir: str
                The CSV file directory, where data is stored
        Returns:
            None
        """
        adapter = DbAdapter(self.connection)

        # Only price records are stored in CSV/Excel files, the asset class data and
        # product data are collected via the folder names and file names, respectively
        if table == "asset class":
            data = os.listdir(dir)

        if table == "product":
            data = os.listdir(dir)

            # Remove file extension
            data = pd.Series(data).str.split(".").str.get(0)
            data.name = dir.split("\\")[-1]

        if table == "price record":
            try:
                data = pd.read_csv(dir)[["Date", "Open", "High", "Low", "Close"]]
            except UnicodeDecodeError:
                print(f"File must be of CSV format '{dir}'")
                return None

            data = DataNormalization(data).clean()
            data.name = dir.split("\\")[-1].split(".")[0]

        adapter.insert_into(table, data)

    def batch_insert(self, BASE_DIR: str) -> None:
        """
        Inserts all types of data and data records that are available in a directory into DB at once
        Parameters:
            BASE_DIR: str
                The data directory, which has two levels of depth, the first level contains folders
                whose names represent the asset classes, the second level contains a list of files,
                in each of which are the price records.
        Returns:
            None
                Data is inserted directly into DB
        """
        # Insert asset class data
        self.insert_records("asset class", BASE_DIR)

        # Insert product data
        for FOLDER in os.listdir(BASE_DIR):
            FOLDER_DIR = os.path.join(BASE_DIR, FOLDER)
            self.insert_records("product", FOLDER_DIR)

            # Insert price record data
            for FILE in os.listdir(FOLDER_DIR):
                FILE_DIR = os.path.join(FOLDER_DIR, FILE)
                self.insert_records("price record", FILE_DIR)

    def update_db(self, SOURCE: str, BASE_DIR: str) -> None:
        """
        Updates DB with new price records that are available and span up to the current date - 1 (yesterday)
        !! Attention !!
            This method only works properly with DB that contains sufficient
            information in rankingtable_product (id, assetclass_id, symbol and alias)
        Parameters:
            SOURCE: str
                The source from where data is obtained
            BASE_DIR: str
                The same as that in batch_insert method
        Returns:
            None
                Data is updated directly into CSV files and DB
        """
        if SOURCE == "yfinance":
            date_records = self.fetch_records("latest date")
            for asset_class, symbol, alias, record_date in date_records:
                # Set the start date to be the day after the latest date available in DB
                start_date = pd.to_datetime(record_date, yearfirst=True, utc=True) \
                             + pd.to_timedelta(1, unit="d")
                end_date = pd.Timestamp.today().date()

                # Download new a CSV file and append new data to the existing file
                DIR = os.path.join(os.path.abspath(BASE_DIR), asset_class)
                self.download_csv(DIR, asset_class, symbol, alias, None, start_date, end_date)

            self.batch_insert(BASE_DIR)

    def download_csv(self, BASE_DIR: str, asset_class: str,
                     symbol: str, alias: str, period: str,
                     start_date: datetime, end_date: datetime) -> None:
        """
        Downloads price records of a particular product and asset class in CSV file format from yahoo-finance,
        appends new data to the existing files or creates new ones
        Parameters:
            BASE_DIR: str
                The same as that in batch_insert and update_db methods
            asset_class: str
                The category of a particular product
            symbol: str
                The presentational symbol of a product
            alias: str
                The trading symbol of a product
            period: str
                The time interval of the price records
            start_date: str
                The start of the date range of the price records
            end_date: str
                The end of the date range of the price records
        Returns:
            None
                Data is inserted directly to CSV files
        """
        FILE_DIR = os.path.join(BASE_DIR, symbol + ".csv")
        if self._is_empty(FILE_DIR):
            period = "max"
            insert_header = True
        else:
            if self._up_to_date(FILE_DIR, asset_class, end_date):
                print(f"{symbol} is up to date")
                return None
            insert_header = False

        try:
            # Download daily price records within a given period
            if period:
                historical_data = yf.Ticker(alias).history(period=period).reset_index()
            # Download daily price records within a specified time interval
            else:
                historical_data = yf.Ticker(alias).history(start=start_date, end=end_date).reset_index()
            historical_data["Date"] = pd.to_datetime(historical_data["Date"], yearfirst=True, utc=True)

            # Datasets originate from different timezones, so that their dates might appear different,
            # but the actual records are the same as those existing in DB
            if not historical_data.query("Date >= @start_date").empty:
                historical_data.to_csv(FILE_DIR, header=insert_header, mode="a", index=False)
        except IndexError:  # When yfinance returns an empty Data Frame
            print(f"No new data records {symbol} from yfinance")
