import os
import sqlite3
from analysis.utils.dboperator import DbController


# Config variable
BASE_DIR = ".\\"

def update() -> None:
    with sqlite3.connect(BASE_DIR + "db.sqlite3") as connection:
        controller = DbController(connection)
        data_dir = os.path.abspath(BASE_DIR + "Data\\News")
        for folder in os.listdir(data_dir):
            folder_dir = os.path.join(data_dir, folder)
            controller.batch_insert("local", os.path.abspath(folder_dir))
