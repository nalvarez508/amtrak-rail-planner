from tkinter import messagebox

import logging
import os
import sys

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger

from views.config import APP_NAME
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import undetected_chromedriver as uc

if os.name == 'nt':
  LOG_PATH = 'NUL'
elif os.name == 'posix':
  LOG_PATH = '/dev/null'

class Driver:
  """
  A generalized class to create a webdriver.

  Attributes
  ----------
  chrome_options = Options
  driver : WebDriver
  """
  def __init__(self, url: str="about:blank", undetected: bool=False) -> None:
    """
    Initializes the webdriver and downloads one if necessary.

    Parameters
    ----------
    url : str, optional
        Starting page string, by default "about:blank"
    undetected : bool, optional
        If True, use the undetected chromedriver.
    """
    # Chrome options to disable logging in terminal
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=0")
    #chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    try:
      if undetected: self.driver = uc.Chrome(executable_path=ChromeDriverManager().install(), service_log_path=LOG_PATH)
      else: self.driver = webdriver.Chrome(ChromeDriverManager().install(),service_log_path=LOG_PATH, options=chrome_options)
      self.driver.maximize_window()
      self.driver.get(url)
    except WebDriverException as e:
      messagebox.showerror(title=APP_NAME, message=e)
      messagebox.showinfo(title=APP_NAME, message="Looks like your Chrome version does not match what the program is trying to use.\nPlease update your Chrome browser.\n\n1. Click the three dots at the top right of the browser.\n2. In the Help menu, click \"About Google Chrome.\"\nUpdates should begin installing automatically.")
      sys.exit(1)