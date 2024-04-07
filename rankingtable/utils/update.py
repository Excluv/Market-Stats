import sqlite3
from rankingtable.utils.dboperator import DbController
from datetime import date, timedelta


# Config variable
BASE_DIR = ".\\"

def update() -> None:
    """
    Explicitly update CSV files and DB with the most recent records
    """
    with sqlite3.connect(BASE_DIR + "db.sqlite3") as connection:
        cursor = connection.cursor()

        # Check if DB is up to date
        latest_date_db = cursor.execute("SELECT MAX(date) FROM rankingtable_pricerecord").fetchone()[0]
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        if not latest_date_db == yesterday:
            controller = DbController(connection)
            controller.update_db("yfinance", BASE_DIR + "Data\\Price")
