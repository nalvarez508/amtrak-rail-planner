import time
import json
import traceback

from HelperClasses import Driver, Train

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
USE_TRAIN_CLASSES = True

class AmtrakSearch:
  def __init__(self, root, driver, origin="WAS", destination="NYP", departDate="03/29/2022", status=None):
    self.origin = origin
    self.destination = destination
    self.departDate = departDate
    self.root = root

    self.hasAlreadySearched = False
    self.driver = driver
    self.thisSearchResultsAsDict = dict()
    self.thisSearchResultsAsTrain = dict()
    self.numberTrainsFound = 0
    self.status = status
    self.progressbar = None

    self.returnedError = False

  def updateStatusMessage(self, message, amt=0):
    self.status.set(message)
    self.progressbar['value'] += amt*2
    #self.progressbar.step(amt)
    self.root.update_idletasks()

  def preSearchSetup(self, origin, destination, departDate, pb):
    self.origin = origin
    self.destination = destination
    self.departDate = departDate
    self.progressbar = pb

  def _test_returnSearchData(self):
    with open("TestTrainSearch.json", "r") as f:
      self.thisSearchResultsAsDict = json.loads(f.read())
    self.thisSearchResultsAsTrain.clear()
    for index, item in enumerate(self.thisSearchResultsAsDict):
      self.thisSearchResultsAsTrain.update({index : Train(self.thisSearchResultsAsDict[item])})
    return self.thisSearchResultsAsTrain

  # Retrives price information from search page
  def findPrice(self, searcher, xpath):
    try:
      area = searcher.find_element(By.XPATH, f".//button[@amt-test-id='{xpath}']")
      return area.find_element(By.XPATH, ".//span[@class='amount ng-star-inserted']").text
    except NoSuchElementException:
      return None
  
  def isSoldOut(self, c, b, s):
    if c == None:
      if b == None:
        if s == None:
          return True
        else:
          return False
      else:
        return False
    else:
      return False

  def findTrainInfo(self, trains):
    # Get info from each train in search
    for train in trains:
      try:
        data = train.find_element(By.XPATH, ".//div[@class='search-results-leg d-flex']")
        try:
          number, name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")
          if name == "NA":
            name = "Train"
        except:
          number = "N/A"
          name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")[0]
        depart = data.find_element(By.XPATH, ".//div[@class='departure-inner']")
        departTime = depart.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n","")
        potentialDelay = depart.find_element(By.XPATH, ".//div[@class='delay-alerts']")
        try:
          potentialDelay.find_element(By.XPATH, ".//span[@class='ng-star-inserted']").text # Train is canceled or delayed
        except:
          tripType = data.find_element(By.XPATH, ".//div[@class='travel-time d-flex flex-grow-1']")
          try:
            travelTime = tripType.find_element(By.XPATH, ".//span[@class='text-center']").text
            segmentType = tripType.find_element(By.XPATH, ".//span[@class='segment-display text-center font-semi mt-2 d-block ng-star-inserted']").text
          except:
            try:
              travelTime = tripType.text.split("\n")[1]
            except IndexError:
              travelTime = tripType.text.split("\n")[0]
            segmentType = "1"
          arrive = data.find_element(By.XPATH, ".//div[@class='arrival-inner']")
          arrivalTime = arrive.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n", "")
          arrivalDate = None
          try:
            arrivalInfo = arrive.find_element(By.XPATH, ".//div[@class='travel-next-day']").text
            arrivalDate = arrivalInfo
            if arrivalInfo == '': arrivalDate = self.departDate
          except NoSuchElementException:
            arrivalDate = self.departDate
          prices = data.find_element(By.XPATH, ".//div[@class='row col-12 p-0 m-0']")
          coachPrice = self.findPrice(prices, 'jl-0-op-0-coach')
          businessPrice = self.findPrice(prices, 'jl-0-op-0-business')
          sleeperPrice = self.findPrice(prices, 'jl-0-op-0-sleeper')

          if not(self.isSoldOut(coachPrice, businessPrice, sleeperPrice)):
            outputDict = {"Number":number, "Name":name, "Origin":self.origin, "Departure Time":departTime, "Departure Date":self.departDate, "Travel Time":travelTime, "Destination":self.destination, "Arrival Time":arrivalTime, "Arrival Date":arrivalDate, "Coach Price":coachPrice, "Business Price":businessPrice, "Sleeper Price":sleeperPrice, "Segment Type":segmentType}
            if USE_TRAIN_CLASSES:
              self.thisSearchResultsAsTrain.update({self.numberTrainsFound : (Train(outputDict))})
            else:
              self.thisSearchResultsAsDict[self.numberTrainsFound] = outputDict
            self.numberTrainsFound += 1
          #self.numberTrainsStringVar.set(self.numberTrainsFound)
      except Exception as e:
        print(traceback.format_exc())
        print(e) #Reached end of list but there is a second page

  def checkEveryPage(self, area, pages):
    for page in range(1,pages+1):
      self.updateStatusMessage(f"Searching - checking page {page}", 22./pages)
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
      area.find_element(By.XPATH, f".//*[text()='{page}']").click()
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f".//a[text()='{page}']//ancestor::li[@class='pagination-page page-item active ng-star-inserted']")))
      time.sleep(1)
      searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']")
      trainList = searchResultsTable.find_elements(By.XPATH, ".//div[@class='col-sm-6 col-lg-12 ng-tns-c6-1 ng-trigger ng-trigger-searchItems ng-star-inserted']")
      self.findTrainInfo(trainList)

  def enterStationInfo(self, area):
    # Entering departure station info
    fromStationSearchArea = area.find_element(By.XPATH, "//div[@class='from-station flex-grow-1']")
    fromStationSearchArea.find_element(By.XPATH, "//station-search[@amt-auto-test-id='fare-finder-from-station-field-page']").click()
    inputField1 = fromStationSearchArea.find_element(By.XPATH, "//input[@id='mat-input-0']")
    inputField1.clear()
    inputField1.send_keys(self.origin)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'From')]"))) # Station name autofilled

    # Entering destination station info
    toStationSearchArea = area.find_element(By.XPATH, "//div[@class='to-station flex-grow-1']")
    toStationSearchArea.find_element(By.XPATH, "//station-search[@amt-auto-test-id='fare-finder-to-station-field-page']").click()
    inputField2 = toStationSearchArea.find_element(By.XPATH, "//input[@id='mat-input-1']")
    inputField2.clear()
    inputField2.send_keys(self.destination)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'To')]"))) # Station name autofilled

  def enterDepartDate(self, area):
    departsArea = area.find_element(By.XPATH, "//div[@class='departs-container w-100']")
    departsArea.click()
    inputField3 = departsArea.find_element(by=By.XPATH, value="//input[@id='mat-input-2']")
    inputField3.clear()
    inputField3.send_keys(f"{self.departDate}\t") #Depart Date
    #searchArea.find_element(by=By.XPATH, value="//input[@id='mat-input-4']").send_keys("03/27/2022") #Return Date

  def oneWaySearch(self):
    self.numberTrainsFound = 0
    self.thisSearchResultsAsTrain.clear()
    self.thisSearchResultsAsDict.clear()
    #self.numberTrainsStringVar.set(self.numberTrainsFound)
    try: # Loading the page
      self.updateStatusMessage("Searching - loading page", 0)
      if (self.driver.current_url != SEARCH_URL) or self.returnedError:
        self.driver.get(SEARCH_URL)
      self.returnedError = False
      self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0)")
      # Make sure the page loads and the New Search button is available to us
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='am-btn btn--secondary btn--transparent-blue-border']")))

      try: # Clicking the new search button
        self.updateStatusMessage("Searching - opening input fields", 5)
        newSearchButton = self.driver.find_element(By.XPATH, "//button[@class='am-btn btn--secondary btn--transparent-blue-border']")
        newSearchButton.click()
        time.sleep(1)

        try: # Entering to/from stations
          self.updateStatusMessage("Searching - entering stations", 1)
          searchArea = self.driver.find_element(By.XPATH, "//div[@id='refineSearch']")
          searchArea = searchArea.find_element(By.XPATH, "//div[@class='row align-items-center']")
          self.enterStationInfo(searchArea)

          try: # Entering departure date
            self.updateStatusMessage("Searching - entering travel dates", 2)
            self.enterDepartDate(searchArea)

            # Wait until "Find Trains" button is enabled, then click it
            self.updateStatusMessage("Searching - retrieving results", 2)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']")))
            searchArea.find_element(By.XPATH, "//div[@class='amtrak-ff-body']").click() # Get calendar popup out of the way
            searchArea.find_element(by=By.XPATH, value="//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']").click() # Click search button

            # Search has been completed, but there is no service
            try:
              self.updateStatusMessage("Searching - loading results", 2)
              time.sleep(2)
              self.updateStatusMessage("Searching - checking results", 10)
              potentialError = self.driver.find_element(By.XPATH, "//div[@class='alert-yellow-text']").text
              print(potentialError)
              self.returnedError = True
              self.updateStatusMessage("Error")
              return potentialError

            # Search has been completed, but we didn't find any trains on that day
            except NoSuchElementException:
              try:
                potentialError = self.driver.find_element(By.XPATH, "//div[@amt-auto-test-id='am-dialog']")
                newDate = potentialError.find_element(By.XPATH, ".//div[@class='pb-0 mb-5 ng-star-inserted']").text
                newDateError = '\n'.join(newDate.split("\n")[0:2])
                print(newDateError)
                self.returnedError = True
                self.updateStatusMessage("Error")
                return newDateError

              # Search has been completed, and we found a train(s)
              except NoSuchElementException:
                try:
                  self.updateStatusMessage("Searching - parsing results page", 3)
                  WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']")))
                  searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']") # Table of results
                  nextPage = searchResultsTable.find_element(By.XPATH, ".//ul[@class='pagination paginator__pagination ng-tns-c6-1']") # Page links area
                  numberSearchPages = int((len(nextPage.find_elements(By.XPATH, ".//*"))-4)/2) # Find out how many pages exist
                  self.checkEveryPage(nextPage, numberSearchPages)
                  self.updateStatusMessage("Done", 100)
                  
                  #print(json.dumps(self.thisSearchResults, indent=4))
                  return self.thisSearchResultsAsTrain
                except Exception as e:
                  print("There was an error retrieving the search data.")
                  print(e)
                  self.returnedError = True
                  return e
          except Exception as e: # Entering departure date
            print("There was an error entering the departure date.")
            self.returnedError = True
            return e
        except Exception as e: # Entering to/from stations
          print("There was an error entering in station info.")
          self.returnedError = True
          return e
      except Exception as e: # Clicking the new search button
        print("There was an error clicking the search button.")
        self.returnedError = True
        return e
    except Exception as e: # Loading the page
      print("There was an issue with loading the search page.")
      self.returnedError = True
      return e

if __name__ == "__main__":
  origin = input("Origin code: ")
  destination = input("Destination code: ")
  departureDate = input("Depature date (MM/DD/YYYY): ")
  d = Driver(SEARCH_URL)
  a = AmtrakSearch(d.driver, origin, destination, departureDate)
  a.oneWaySearch()