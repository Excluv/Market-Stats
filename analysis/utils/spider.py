import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
from bs4 import BeautifulSoup

import os
import time
import pandas as pd


class FFSpider:
    def __init__(self, driver):
        self.driver = driver
        self.error_log = list()
        self.skipped_dates = list()

    def _get_calendar_table(self, url, start_date: str, end_date: str) -> str:
        self.driver.get(url)
        try:
            # Open date filter
            date_form = self.driver.find_element(By.CSS_SELECTOR, "a[class='highlight light options']")
            date_form.click()

            # Specify new input and apply
            user_input = start_date + " - " + end_date
            date_input = self.driver.find_element(
                By.CSS_SELECTOR,
                "input[type='text'][class='flexdatepicker__input']"
            )
            date_input.clear()
            date_input.send_keys(user_input)

            apply_btn = self.driver.find_element(
                By.CSS_SELECTOR,
                "input[type='submit'][value='Apply Settings']"
            )
            apply_btn.click()

            # Wait for the page to fully load
            time.sleep(5)

            # Scroll down to load new data on scroll
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            for num in range(10):
                time.sleep(1)
                start_position = num * (page_height / 10)
                end_position = (num + 1) * (page_height / 10)
                self.driver.execute_script(f"window.scrollTo({start_position}, {end_position})")

            # Retain only the calendar table, where the econ. news lie
            soup = BeautifulSoup(self.driver.page_source, "lxml")
            calendar_table = soup.find(name="table", attrs={"class": "calendar__table"})

            yield calendar_table.prettify()
            time.sleep(5)
        except (selenium.common.exceptions.ElementClickInterceptedException,
                selenium.common.exceptions.NoSuchElementException):
            self.skipped_dates.append(start_date + " - " + end_date)
        except Exception as error:
            self.error_log.append(error)
            self.skipped_dates.append(start_date + " - " + end_date)

    def scrape(self, directory, url, start_date: str, end_date: str):
        # Construct a list of the first and last dates of monthly intervals within the given date range
        start_dates = pd.date_range(start_date, end_date, freq="MS", tz="Asia/Bangkok") \
                        .strftime("%b %d, %Y") \
                        .tolist()
        end_dates = pd.date_range(start_date, end_date, freq="M", tz="Asia/Bangkok") \
                        .strftime("%b %d, %Y") \
                        .tolist()

        # Generate HTML data and save them to a local directory
        for start_date, end_date in zip(start_dates, end_dates):
            html_table = next(self._get_calendar_table(URL, start_date, end_date))
            file_name = f"{start_date} - {end_date}.txt"
            self.save(BASE_DIR + "Econ. News\\" + file_name, html_table)

        # Records of the errors and dates that have been skipped due to errors
        self.save(BASE_DIR + "Econ. News\\" + "error_log.txt", spider.error_log)
        self.save(BASE_DIR + "Econ. News\\" + "skipped_dates.txt", spider.skipped_dates)

    def save(self, file_dir: str, content: str or list) -> None:
        file_dir = os.path.abspath(file_dir)
        with open(file_dir, "w+") as file:
            if type(content) is not str:
                for element in content:
                    file.write(element)
            else:
                file.write(content)


if __name__ == "__main__":
    BASE_DIR = "C:\\Users\\jio\\Desktop\\"
    URL = "https://www.forexfactory.com/calendar"

    options = webdriver.ChromeOptions()
    driver_path = BASE_DIR + "chromedriver-win64\\chromedriver.exe"
    driver = uc.Chrome(driver_executable_path=driver_path, options=options)
    with driver:
        spider = FFSpider(driver)
        spider.scrape(BASE_DIR + "Econ. News", URL, "2024-02-01", "2024-02-29")

