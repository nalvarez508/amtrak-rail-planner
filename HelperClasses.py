import json
import datetime
import os
import logging
import requests
from bs4 import BeautifulSoup

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
    self.prettyDeparture, self.prettyArrival = self.makePrettyDates()
    self.coachPrice = key["Coach Price"]
    self.businessPrice = key["Business Price"]
    self.sleeperPrice = key["Sleeper Price"]

    self.organizationalUnit = {
      "Origin":self.origin,
      "Destination":self.destination,
      "Number":self.number,
      "Name":self.name,
      "Departure Time":self.departureTime,
      "Departure Date":self.departureDate,
      "Departs":self.prettyDeparture,
      "Duration":self.travelTime,
      "Arrival Time":self.arrivalTime,
      "Arrival Date":self.arrivalDate,
      "Arrives":self.prettyArrival,
      "Coach Price":self.coachPrice,
      "Business Price":self.businessPrice,
      "Sleeper Price":self.sleeperPrice
    }
  
  def __str__(self):
    return self.organizationalUnit
  
  def makePrettyDate(self, dt, compare=False):
    def doDayStringPrettification(doDate=""):
      suffix = ""
      if doDate:
        day = dt.day % 10
        if day == 1: suffix = "st"
        elif day == 2: suffix = "nd"
        elif day == 3: suffix = "rd"
        else: suffix = "th"
      return datetime.datetime.strftime(dt, f"{doDate}{suffix} %I:%M%p").strip()
    
    if compare == True:
      if self.departure.day == self.arrival.day:
        return doDayStringPrettification()
      elif self.departure.day < self.arrival.day:
        return doDayStringPrettification("%a. %d")
    elif compare == False:
      return doDayStringPrettification()
  
  def makePrettyDates(self):
    def doDayStringPrettification(dt, doDate=""):
      suffix = ""
      if doDate:
        day = dt.day % 10
        if day == 1: suffix = "st"
        elif day == 2: suffix = "nd"
        elif day == 3: suffix = "rd"
        else: suffix = "th"
      return datetime.datetime.strftime(dt, f"{doDate}{suffix} %I:%M%p").strip()

    if self.departure.day == self.arrival.day:
      return [doDayStringPrettification(self.departure), doDayStringPrettification(self.arrival)]
    elif self.departure.day < self.arrival.day:
      return [doDayStringPrettification(self.departure, "%a. %d"), doDayStringPrettification(self.arrival, "%a. %d")]

  def returnSelectedElements(self, cols):
    temp = list()
    for col in cols:
      try:
        temp.append(self.organizationalUnit[col])
      except KeyError:
        temp.append('')
        print(f"Attribute {col} is not recognized.")
    return temp

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

class Stations:
  def __init__(self):
    self.stations = dict()
    self.getAmtrakStations()
    #self._test_writeToFile()
  
  def getAmtrakStations(self):
    wiki = requests.get("https://en.wikipedia.org/wiki/List_of_Amtrak_stations").text
    soup = BeautifulSoup(wiki, 'xml')
    table = soup.find('table', {'class': 'wikitable collapsible sortable'})
    table_rows = table.find_all('tr')

    for row in table_rows:
      rowData = row.find_all('td')
      if len(rowData) > 0:
        name = rowData[0].text.strip().replace("\u2013","-")
        code = rowData[1].text.strip()
        city = rowData[2].text.strip()
        state = rowData[3].text.strip()
        self.stations[f"{code} | {name}, {state}"] = {"Code":code, "Name":name, "City":city, "State":state}

  def returnStationKeys(self):
    return list(self.stations.keys())
  
  def returnCityState(self, key):
    return f"{self.stations[key]['City']}, {self.stations[key]['State']}"
  
  def returnStationNameAndState(self, key):
    return f"{self.stations[key]['Name']}, {self.stations[key]['State']}"
  
  def getStationCode(self, key):
    return self.stations[key]["Code"]

  def _test_writeToFile(self):
    with open("Stations.json", "w") as f:
      f.write(json.dumps(self.stations, indent=4))

class UserSelections:
  def __init__(self):
    self.origin = None
    self.destination = None
    self.departDate = None

    self.userSelections = RailPass()
  
  def set(self, city, side):
    if side == 1:
      self.setOrigin(city)
    elif side == 2:
      self.setDestination(city)

  def setOrigin(self, o):
    self.origin = o
  def getOrigin(self):
    return self.origin
  
  def setDestination(self, d):
    self.destination = d
  def getDestination(self):
    return self.destination
  
  def addSegment(self, t):
    self.userSelections.createSegment(t)