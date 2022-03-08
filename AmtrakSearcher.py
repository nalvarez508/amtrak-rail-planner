import logging
import signal
import time
import os

from selenium.webdriver.remote.remote_connection import LOGGER as seleniumLogger
seleniumLogger.setLevel(logging.WARNING)
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from webdriver_manager.chrome import ChromeDriverManager

SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
if os.name == 'nt':
  LOG_PATH = 'NUL'
elif os.name == 'posix':
  LOG_PATH = '/dev/null'

# Keyboard interrupts
def exitHandler(signum, frame):
  exit(0)

class Driver:
  def __init__(self, url=SEARCH_URL):
    # Chrome options to disable logging in terminal
    signal.signal(signal.SIGINT, exitHandler)
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    self.driver = webdriver.Chrome(ChromeDriverManager().install(),service_log_path=LOG_PATH, options=chrome_options)
    self.driver.maximize_window()
    self.driver.get(url)

class Amtrak:
  def __init__(self, driver, origin="WAS", destination="NYP", departDate="03/29/2022"):
    self.origin = origin
    self.destination = destination
    self.departDate = departDate

    self.hasAlreadySearched = False
    self.driver = driver
    self.thisSearchResults = dict()
    self.numberTrainsFound = 0

  # Retrives price information from search page
  def findPrice(self, searcher, xpath):
    try:
      area = searcher.find_element(By.XPATH, f".//button[@amt-test-id='{xpath}']")
      return area.find_element(By.XPATH, ".//span[@class='amount ng-star-inserted']").text
    except NoSuchElementException:
      return None
  
  def findTrainInfo(self, trains):
    # Get info from each train in search
    for train in trains:
      try:
        data = train.find_element(By.XPATH, ".//div[@class='search-results-leg d-flex']")
        try:
          number, name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")
        except:
          name = 0
          number = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")[0]
        depart= data.find_element(By.XPATH, ".//div[@class='departure-inner']")
        departTime = depart.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n","")
        travelTime = data.find_element(By.XPATH, ".//div[@class='travel-time d-flex flex-grow-1']").text.split("\n")[1]
        arrive = data.find_element(By.XPATH, ".//div[@class='arrival-inner']")
        arrivalTime = arrive.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n", "")
        try:
          arrivalInfo = arrive.find_element(By.XPATH, ".//div[@class='travel-next-day']").text
          if arrivalInfo == '': arrivalDate = self.departDate
        except NoSuchElementException:
          arrivalDate = self.departDate
        prices = data.find_element(By.XPATH, ".//div[@class='row col-12 p-0 m-0']")
        coachPrice = self.findPrice(prices, 'jl-0-op-0-coach')
        businessPrice = self.findPrice(prices, 'jl-0-op-0-business')
        self.thisSearchResults[self.numberTrainsFound] = {"Number":number, "Name":name, "Departure Time":departTime, "Departure Date":self.departDate, "Travel Time":travelTime, "Arrival Time":arrivalTime, "Arrival Date":arrivalDate, "Coach Price":coachPrice, "Business Price":businessPrice}
        self.numberTrainsFound += 1
      except:
        pass #Reached end of list but there is a second page

  def checkEveryPage(self, area, pages):
    for page in range(1,pages+1):
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
      area.find_element(By.XPATH, f".//*[text()='{page}']").click()
      #time.sleep(1)
      #self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0)")
      searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']")
      trainList = searchResultsTable.find_elements(By.XPATH, ".//div[@class='col-sm-6 col-lg-12 ng-tns-c6-1 ng-trigger ng-trigger-searchItems ng-star-inserted']")
      self.findTrainInfo(trainList)

  def enterStationInfo(self, area):
    # Entering departure station info
    fromStationSearchArea = area.find_element_by_xpath("//div[@class='from-station flex-grow-1']")
    fromStationSearchArea.find_element_by_xpath("//station-search[@amt-auto-test-id='fare-finder-from-station-field-page']").click()
    fromStationSearchArea.find_element_by_xpath("//input[@id='mat-input-0']").send_keys(self.origin)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'From')]"))) # Station name autofilled

    # Entering destination station info
    toStationSearchArea = area.find_element_by_xpath("//div[@class='to-station flex-grow-1']")
    toStationSearchArea.find_element_by_xpath("//station-search[@amt-auto-test-id='fare-finder-to-station-field-page']").click()
    toStationSearchArea.find_element_by_xpath("//input[@id='mat-input-1']").send_keys(self.destination)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'To')]"))) # Station name autofilled

  def enterDepartDate(self, area):
    departsArea = area.find_element(By.XPATH, "//div[@class='departs-container w-100']")
    departsArea.click()
    departsArea.find_element(by=By.XPATH, value="//input[@id='mat-input-2']").send_keys(f"{self.departDate}\t") #Depart Date
    #searchArea.find_element(by=By.XPATH, value="//input[@id='mat-input-4']").send_keys("03/27/2022") #Return Date

  def oneWaySearch(self):

    try: # Loading the page
      if self.driver.current_url != SEARCH_URL:
        self.driver.get(SEARCH_URL)
      # Make sure the page loads and the New Search button is available to us
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='am-btn btn--secondary btn--transparent-blue-border']")))

      try: # Clicking the new search button
        newSearchButton = self.driver.find_element_by_xpath("//button[@class='am-btn btn--secondary btn--transparent-blue-border']")
        newSearchButton.click()
        time.sleep(1)

        try: # Entering to/from stations
          searchArea = self.driver.find_element_by_xpath("//div[@id='refineSearch']")
          searchArea = searchArea.find_element_by_xpath("//div[@class='row align-items-center']")
          self.enterStationInfo(searchArea)

          try: # Entering departure date
            self.enterDepartDate(searchArea)

            # Wait until "Find Trains" button is enabled, then click it
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']")))
            searchArea.find_element(By.XPATH, "//div[@class='amtrak-ff-body']").click() # Get calendar popup out of the way
            searchArea.find_element(by=By.XPATH, value="//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']").click() # Click search button

            # Search has been completed, but there is no service
            try:
              time.sleep(3)
              potentialError = self.driver.find_element(By.XPATH, "//div[@class='alert-yellow-text']").text
              print(potentialError)

            # Search has been completed, but we didn't find any trains on that day
            except NoSuchElementException:
              try:
                #time.sleep(3)
                potentialError = self.driver.find_element(By.XPATH, "//div[@amt-auto-test-id='am-dialog']")
                newDate = potentialError.find_element(By.XPATH, ".//div[@class='pb-0 mb-5 ng-star-inserted']").text
                newDateError = '\n'.join(newDate.split("\n")[0:2])
                print(newDateError)
                #if potentialError.text.split("\n")[0] == "No Trips on Your Selected Date":
                #  print(True)
                #else:
                #  print(potentialError.text)


              # Search has been completed, and we found a train(s)
              except NoSuchElementException:
                try:
                  WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']")))
                  searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']") # Table of results
                  nextPage = searchResultsTable.find_element(By.XPATH, ".//ul[@class='pagination paginator__pagination ng-tns-c6-1']") # Page links area
                  numberSearchPages = int((len(nextPage.find_elements(By.XPATH, ".//*"))-4)/2) # Find out how many pages exist
                  self.checkEveryPage(nextPage, numberSearchPages)
                  print(self.thisSearchResults)
                  for train in self.thisSearchResults:
                    print(self.thisSearchResults[train]["Number"])
                except Exception as e:
                  print("There was an error retrieving the search data.")
                  print(e)
          except Exception as e: # Entering departure date
            print("There was an error entering the departure date.")
            print(e)
        except Exception as e: # Entering to/from stations
          print("There was an error entering in station info.")
          print(e)
      except Exception as e: # Clicking the new search button
        print("There was an error clicking the search button.")
        print(e)
    except IOError as e: # Loading the page
      print("There was an issue with loading the search page.")
      print(e)

if __name__ == "__main__":
  origin = input("Origin code: ")
  destination = input("Destination code: ")
  departureDate = input("Depature date (MM/DD/YYYY): ")
  d = Driver()
  a = Amtrak(d.driver, origin, destination, departureDate)
  a.oneWaySearch()