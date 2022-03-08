import json
import datetime
import os
import logging

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

if os.name == 'nt':
  LOG_PATH = 'NUL'
elif os.name == 'posix':
  LOG_PATH = '/dev/null'

# Train class objects are used for individual segments of the trip, so there would be 10 total.
class Train:
  def __init__(self, key):
    self.origin = key["Origin"]
    self.destination = key["Destination"]
    self.number = int(key["Number"])
    self.name = key["Name"]
    self.departureTime = key["Departure Time"]
    self.departureDate = key["Departure Date"]
    self.departure = self.convertToDatetime(self.departureDate, self.departureTime)
    self.travelTime = key["Travel Time"]
    self.arrivalTime = key["Arrival Time"]
    self.arrivalDate = key["Arrival Date"]
    self.arrival = self.convertToDatetime(self.arrivalDate, self.arrivalTime)
    self.coachPrice = key["Coach Price"]
    self.businessPrice = key["Business Price"]
    self.sleeperPrice = key["Sleeper Price"]
  
  def convertToCsvRow(self):
    tempDict = dict()
    tempDict["Origin"] = self.origin
    tempDict["Destination"] = self.destination
    tempDict["Train"] = f"{self.name} {self.number}"
    tempDict["Departs"] = datetime.datetime.strftime(self.departure, "%a %d %I:%M%p")
    tempDict["Arrives"] = datetime.datetime.strftime(self.arrival, "%a %d %I:%M%p")
    tempDict["Duration"] = self.travelTime
    return tempDict

  def convertToDatetime(self, d, t):
    t = t.replace("p", "PM")
    t = t.replace("a", "AM")
    return datetime.datetime.strptime(f"{d} {t}", "%m/%d/%Y %I:%M%p")

# RailPass class objects hold Train objects and will assist with data display
class RailPass:
  def __init__(self):
    self.segments = dict()
  
  def createCsv(self):
    output = dict()
    for segment, train in enumerate(self.segments):
      output.update({segment:train.convertToCsvRow()})
    return output
  
  def createSegment(self):
    # Retrieve the user parameters and train selection
    # Create a train object
    # Add this train object to the segments var
    pass

class Driver:
  def __init__(self, url="about:blank"):
    # Chrome options to disable logging in terminal
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    self.driver = webdriver.Chrome(ChromeDriverManager().install(),service_log_path=LOG_PATH, options=chrome_options)
    self.driver.maximize_window()
    self.driver.get(url)