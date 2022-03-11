import time
import json
import traceback

from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By

from .driver import Driver
from traintracks.train import Train
from views import config as cfg

USE_TRAIN_CLASSES = True

class AmtrakSearch:
  """
  A class to search for an Amtrak journey(s). Results are overwritten with each run of the search function. Exists for the lifetime of the application.

  Attributes
  ----------
  origin : str
  destination : str
  departDate : str
  root : Tk
  hasAlreadySearched : bool
  driver : WebDriver
  thisSearchResultsAsDict : dict
  thisSearchResultsAsTrain : dict
  numberTrainsFound : int
  status : tk.Label
  progressbar : ttk.Progressbar
  numberTrainsLabel : StringVar
  returnedError : bool
      True if the search function exits on an exception of some kind. Reloads the page.
  
  Methods
  -------
  preSearchSetup(origin, destination, departDate, pb, l)
      Initializes search variables in the class
  oneWaySearch()
      Performs a search for the requested journey.
  """
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
    self.numberTrainsLabel = None

    self.returnedError = False

  def __updateStatusMessage(self, message, amt=0):
    self.status.set(message)
    self.progressbar['value'] += amt*2
    #self.progressbar.step(amt)
    self.root.update_idletasks()

  def __updateNumberTrainsLabel(self):
    self.numberTrainsLabel.set(self.numberTrainsFound)
    self.root.update_idletasks()

  def preSearchSetup(self, origin, destination, departDate, pb, l):
    """
    Initializes variables to begin a search.

    Parameters
    ----------
    origin : str
        Amtrak station code of origin.
    destination : str
        Amtrak station code of destination.
    departDate : str
        Date of the format mm/dd/yyyy
    pb : ttk.Progressbar
        Progressbar object to update during search.
    l : tk.StringVar
        Number of trains label to update during search.
    """
    self.origin = origin
    self.destination = destination
    self.departDate = departDate
    self.progressbar = pb
    self.numberTrainsLabel = l

  def __test_returnSearchData(self):
    with open("TestTrainSearch.json", "r") as f:
      self.thisSearchResultsAsDict = json.loads(f.read())
    self.thisSearchResultsAsTrain.clear()
    for index, item in enumerate(self.thisSearchResultsAsDict):
      self.thisSearchResultsAsTrain.update({index : Train(self.thisSearchResultsAsDict[item])})
    return self.thisSearchResultsAsTrain

  # Retrives price information from search page
  def __findPrice(self, searcher, xpath):
    """
    Finds the value of a given element in the price area (coach, business, etc).

    Parameters
    ----------
    searcher : WebElement
        Area of the page to search for child elements in.
    xpath : str
        XPath of element.

    Returns
    -------
    str
        Price.
    
    Raises
    ------
    NoSuchElementException
        Price was not found, either it was sold out or isn't available to begin with. Returns None for that price.
    """
    try:
      area = searcher.find_element(By.XPATH, f".//button[@amt-test-id='{xpath}']")
      return area.find_element(By.XPATH, ".//span[@class='amount ng-star-inserted']").text
    except NoSuchElementException:
      return None
  
  def __isSoldOut(self, c, b, s):
    """
    Determines if a certain fare bracket is sold out.

    Parameters
    ----------
    c : str or None
        Coach price.
    b : str or None
        Business price.
    s : str or None
        Sleeper price.

    Returns
    -------
    bool
        True if all prices are None, otherwise False.
    """
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

  def __findTrainInfo(self, trains):
    """
    Finds information about each result on the search page.

    Parameters
    ----------
    trains : list
        List of WebElements on the page.

    Yields
    ------
    outputDict : dict
        All train information to be added to AmtrakSearch variable for results.
    
    Raises
    ------
    Exception
        Usually, the end of the page was reached. Otherwise a blanket catch.
    """
    # Get info from each train in search
    for train in trains:
      try:
        data = train.find_element(By.XPATH, ".//div[@class='search-results-leg d-flex']")

        try: # Named train service
          number, name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")
          if name == "NA":
            name = "Train"
        except: # Mixed Service/Multiple Trains
          number = "N/A"
          name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")[0]

        depart = data.find_element(By.XPATH, ".//div[@class='departure-inner']") # Search area
        departTime = depart.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n","")

        potentialDelay = depart.find_element(By.XPATH, ".//div[@class='delay-alerts']") # Search area
        try: # Train is canceled or delayed
          potentialDelay.find_element(By.XPATH, ".//span[@class='ng-star-inserted']").text

        except: # Train is running
          tripType = data.find_element(By.XPATH, ".//div[@class='travel-time d-flex flex-grow-1']") # Search area
          try: # Found trip duration and service level (direct, 2 segments, etc)
            travelTime = tripType.find_element(By.XPATH, ".//span[@class='text-center']").text
            segmentType = tripType.find_element(By.XPATH, ".//span[@class='segment-display text-center font-semi mt-2 d-block ng-star-inserted']").text
          except:
            try: # Get trip duration and skip Covid info
              travelTime = tripType.text.split("\n")[1]
            except IndexError: # Couldn't find Covid info, duration must be at [0]
              travelTime = tripType.text.split("\n")[0]
            segmentType = "1"

          arrive = data.find_element(By.XPATH, ".//div[@class='arrival-inner']") # Search area
          arrivalTime = arrive.find_element(By.XPATH, ".//div[@class='time mt-2 pt-1 d-flex align-items-baseline']").text.replace("\n", "")
          arrivalDate = None
          try: # Multi-day trip
            arrivalInfo = arrive.find_element(By.XPATH, ".//div[@class='travel-next-day']").text
            arrivalDate = arrivalInfo
            if arrivalInfo == '': arrivalDate = self.departDate # One day trip
          except NoSuchElementException: # One day trip
            arrivalDate = self.departDate

          prices = data.find_element(By.XPATH, ".//div[@class='row col-12 p-0 m-0']") # Search area
          coachPrice = self.__findPrice(prices, 'jl-0-op-0-coach')
          businessPrice = self.__findPrice(prices, 'jl-0-op-0-business')
          sleeperPrice = self.__findPrice(prices, 'jl-0-op-0-sleeper')

          if not(self.__isSoldOut(coachPrice, businessPrice, sleeperPrice)):
            outputDict = {"Number":number, "Name":name, "Origin":self.origin, "Departure Time":departTime, "Departure Date":self.departDate, "Travel Time":travelTime, "Destination":self.destination, "Arrival Time":arrivalTime, "Arrival Date":arrivalDate, "Coach Price":coachPrice, "Business Price":businessPrice, "Sleeper Price":sleeperPrice, "Segment Type":segmentType}
            if USE_TRAIN_CLASSES:
              self.thisSearchResultsAsTrain.update({self.numberTrainsFound : (Train(outputDict))})
            else:
              self.thisSearchResultsAsDict[self.numberTrainsFound] = outputDict
            self.numberTrainsFound += 1
            self.__updateNumberTrainsLabel()

      except Exception as e:
        print(traceback.format_exc())
        print(e) #Reached end of list but there is a second page

  def __checkEveryPage(self, area, pages):
    """
    Checks every page of search results. If there is one, it does not loop.

    Parameters
    ----------
    area : WebElement
        Search area at the bottom of the page where the page links are located.
    pages : int
        Number of pages of results.
    """
    for page in range(1,pages+1): # Starts at 1 (page 1) and goes up to pages
      self.__updateStatusMessage(f"Searching - checking page {page}", 22./pages)
      self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") # Puts page links in view
      
      # Loads next page and waits until elements load
      area.find_element(By.XPATH, f".//*[text()='{page}']").click()
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f".//a[text()='{page}']//ancestor::li[@class='pagination-page page-item active ng-star-inserted']")))
      time.sleep(1)

      searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']") # Search area
      trainList = searchResultsTable.find_elements(By.XPATH, ".//div[@class='col-sm-6 col-lg-12 ng-tns-c6-1 ng-trigger ng-trigger-searchItems ng-star-inserted']") # List of train results
      self.__findTrainInfo(trainList)

  def __enterStationInfo(self, area):
    """
    Fills in origin and destination fields.

    Parameters
    ----------
    area : WebElement
        Area that contains input fields.
    """
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

  def __enterDepartDate(self, area):
    """
    Fills in departure date.

    Parameters
    ----------
    area : WebElement
        Area that contains the departure date input field.
    """
    departsArea = area.find_element(By.XPATH, "//div[@class='departs-container w-100']")
    departsArea.click()
    inputField3 = departsArea.find_element(by=By.XPATH, value="//input[@id='mat-input-2']")
    inputField3.clear()
    inputField3.send_keys(f"{self.departDate}\t") #Depart Date
    #searchArea.find_element(by=By.XPATH, value="//input[@id='mat-input-4']").send_keys("03/27/2022") #Return Date

  def oneWaySearch(self):
    """
    Performs a search for Amtrak trains on a one-way journey.

    Returns
    -------
    dict or str
        If the search is successful, returns a dict of trains, otherwise a string of the error message.
    
    Raises
    ------
    Exception
        Catch-all for any failed searches, returns the error message.
    """

    # Resets/clears elements to begin new search
    self.numberTrainsFound = 0
    self.thisSearchResultsAsTrain.clear()
    self.thisSearchResultsAsDict.clear()
    
    try: # Loading the page
      self.__updateStatusMessage("Searching - loading page", 0)
      if (self.driver.current_url != cfg.SEARCH_URL) or self.returnedError: # If not at the page or an error occurred last time, reload
        self.driver.get(cfg.SEARCH_URL)
      self.returnedError = False
      self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0)") # Reset after previous search

      # Make sure the page loads and the New Search button is available to us
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='am-btn btn--secondary btn--transparent-blue-border']")))

      try: # Clicking the new search button
        self.__updateStatusMessage("Searching - opening input fields", 5)
        newSearchButton = self.driver.find_element(By.XPATH, "//button[@class='am-btn btn--secondary btn--transparent-blue-border']")
        newSearchButton.click()
        time.sleep(1)

        try: # Entering to/from stations
          self.__updateStatusMessage("Searching - entering stations", 1)
          searchArea = self.driver.find_element(By.XPATH, "//div[@id='refineSearch']")
          searchArea = searchArea.find_element(By.XPATH, "//div[@class='row align-items-center']")
          self.__enterStationInfo(searchArea)

          try: # Entering departure date
            self.__updateStatusMessage("Searching - entering travel dates", 2)
            self.__enterDepartDate(searchArea)

            # Wait until "Find Trains" button is enabled, then click it
            self.__updateStatusMessage("Searching - retrieving results", 2)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']")))
            searchArea.find_element(By.XPATH, "//div[@class='amtrak-ff-body']").click() # Get calendar popup out of the way
            searchArea.find_element(by=By.XPATH, value="//button[@class='search-btn ng-star-inserted' and @aria-disabled='false']").click() # Click search button

            # Search has been completed, but there is no service
            try:
              self.__updateStatusMessage("Searching - loading results", 2)
              time.sleep(2)
              self.__updateStatusMessage("Searching - checking results", 10)
              potentialError = self.driver.find_element(By.XPATH, "//div[@class='alert-yellow-text']").text
              print(potentialError)
              self.returnedError = True
              self.__updateStatusMessage("Error")
              return potentialError

            # Search has been completed, but we didn't find any trains on that day
            except NoSuchElementException:
              try:
                potentialError = self.driver.find_element(By.XPATH, "//div[@amt-auto-test-id='am-dialog']")
                newDate = potentialError.find_element(By.XPATH, ".//div[@class='pb-0 mb-5 ng-star-inserted']").text
                newDateError = '\n'.join(newDate.split("\n")[0:2])
                print(newDateError)
                self.returnedError = True
                self.__updateStatusMessage("Error")
                return newDateError

              # Search has been completed, and we found a train(s)
              except NoSuchElementException:
                try:
                  self.__updateStatusMessage("Searching - parsing results page", 3)
                  WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']")))
                  searchResultsTable = self.driver.find_element(By.XPATH, "//div[@class='row ng-tns-c6-1 ng-trigger ng-trigger-searchList ng-star-inserted']") # Table of results
                  nextPage = searchResultsTable.find_element(By.XPATH, ".//ul[@class='pagination paginator__pagination ng-tns-c6-1']") # Page links area
                  numberSearchPages = int((len(nextPage.find_elements(By.XPATH, ".//*"))-4)/2) # Find out how many pages exist
                  self.__checkEveryPage(nextPage, numberSearchPages)
                  self.__updateStatusMessage("Done", 100)
                  
                  #print(json.dumps(self.thisSearchResults, indent=4))
                  return self.thisSearchResultsAsTrain

                except Exception as e: # Search parsing
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
  d = Driver(cfg.SEARCH_URL)
  a = AmtrakSearch(d.driver, origin, destination, departureDate)
  a.oneWaySearch()