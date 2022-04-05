import logging
import os
import sys

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
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
  driver : WebDriver
  """
  def __init__(self, url="about:blank", undetected=False):
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
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    try:
      if undetected: self.driver = uc.Chrome(executable_path=ChromeDriverManager().install(), service_log_path=LOG_PATH)
      else: self.driver = webdriver.Chrome(ChromeDriverManager().install(),service_log_path=LOG_PATH, options=chrome_options)
      self.driver.maximize_window()
      self.driver.get(url)
    except WebDriverException:
      sys.exit(1)