import time
import json
import traceback
from datetime import datetime
from math import trunc
from random import randint
from tkinter import StringVar, Tk, Label, ttk

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
  oneWaySearch
      Performs a search for the requested journey.
  """
  def __init__(self, root: Tk, driver: Driver, origin: str="WAS", destination: str="NYP", departDate: str="03/29/2022", status: Label=None) -> None:
    """
    Initializes a searcher.

    Parameters
    ----------
    root : tk.Tk
        Parent window.
    driver : WebDriver
        The searching driver.
    origin : str, optional
        Origin station, by default "WAS"
    destination : str, optional
        Destination station, by default "NYP"
    departDate : str, optional
        Departure date as 'mm/dd/yyyy', by default "03/29/2022"
    status : tk.Label, optional
        Status bar object, by default None
    """
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

  def __updateStatusMessage(self, message: str, amt: int=0) -> None:
    """
    Updates the parent window's status bar.

    Parameters
    ----------
    message : str
        Message to display
    amt : int, optional
        Amount out of 50 to increment the progress bar, by default 0
    """
    self.status.set(message)
    self.progressbar['value'] += amt*2
    #self.progressbar.step(amt)
    self.root.update_idletasks()

  def __updateNumberTrainsLabel(self) -> None:
    """Updates the number of trains found in the main window."""
    if self.numberTrainsFound == 1:
      self.numberTrainsLabel.set(f"{self.numberTrainsFound} train found")
    else:
      self.numberTrainsLabel.set(f"{self.numberTrainsFound} trains found")
    self.root.update_idletasks()

  def preSearchSetup(self, origin: str, destination: str, departDate: str, pb: ttk.Progressbar, l: StringVar) -> None:
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

  def _test_search(self):
    self.numberTrainsFound = 0
    self.thisSearchResultsAsTrain.clear()
    self.thisSearchResultsAsDict.clear()

    _suffix = ['single', 'multiple', 'triservice', 'segments']
    fileToUse = trunc(datetime.now().timestamp()) % 4
    with open(f"_retrieved/searchresults_{_suffix[fileToUse]}.json", "r") as f:
      temp = json.loads(f.read())
    self.__processTrainJson(temp)
    self.__updateStatusMessage("Done", 100)
    return self.thisSearchResultsAsTrain

  # Retrives price information from search page
  def __findPrice(self, searcher, xpath: str) -> str:
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
      area = searcher.find_element(By.XPATH, f".//button[contains(@amt-test-id, '{xpath}')]")
      return area.find_element(By.XPATH, ".//span[starts-with(@class, 'amount ng-star-inserted')]").text
    except NoSuchElementException:
      return None
  
  def __isSoldOut(self, c: str=None, b: str=None, s: str=None) -> bool:
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
  
  def __checkTripDetails(self, xpath) -> list[str]:
    try:
      xpath.find_element(By.XPATH, ".//button[@amt-auto-test-id='trip-details-link']").click()
      dropdown = xpath.find_element(By.XPATH, "//div[contains(@class, 'am-dropdown-content am-dropdown-content--bottom-right')]")
      trainSegs = dropdown.find_elements(By.XPATH, "//div[@class='travel-type-service']")
      _names = []
      for train in trainSegs:
        _this = train.find_element(By.XPATH, "//span[@class='ng-star-inserted']").text
        _names.append(_this.split(' ', 1)[1])

      dropdown.find_element(By.XPATH, "//button[@class='close pull-right']").click()
      return _names
    except NoSuchElementException:
      return []

  def __findTrainInfo(self, trains: list) -> None:
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
        data = train.find_element(By.XPATH, ".//div[starts-with(@class, 'search-results-leg d-flex')]")

        try: # Named train service
          number, name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")
          if name == "NA":
            name = "Train"
        except: # Mixed Service/Multiple Trains
          number = "N/A"
          name = data.find_element(By.XPATH, ".//div[@amt-auto-test-id='search-result-train-name']").text.split("\n")[0]

        depart = data.find_element(By.XPATH, ".//div[starts-with(@class, 'departure-inner')]") # Search area
        departTime = depart.find_element(By.XPATH, ".//div[contains(@class, 'align-items-baseline')]").text.replace("\n","")

        potentialDelay = depart.find_element(By.XPATH, ".//div[starts-with(@class, 'delay-alerts')]") # Search area
        try: # Train is canceled or delayed
          potentialDelay.find_element(By.XPATH, ".//span[@class='ng-star-inserted']").text

        except: # Train is running
          tripType = data.find_element(By.XPATH, ".//div[starts-with(@class, 'travel-time d-flex')]") # Search area
          try: # Found trip duration and service level (direct, 2 segments, etc)
            travelTime = tripType.find_element(By.XPATH, ".//span[@class='text-center']").text
            segmentType = tripType.find_element(By.XPATH, ".//span[starts-with(@class, 'segment-display text-center')]").text
          except:
            try: # Get trip duration and skip Covid info
              travelTime = tripType.text.split("\n")[1]
            except IndexError: # Couldn't find Covid info, duration must be at [0]
              travelTime = tripType.text.split("\n")[0]
            segmentType = "1"

          arrive = data.find_element(By.XPATH, ".//div[starts-with(@class, 'arrival-inner')]") # Search area
          arrivalTime = arrive.find_element(By.XPATH, ".//div[contains(@class, 'align-items-baseline')]").text.replace("\n", "")
          arrivalDate = None
          try: # Multi-day trip
            arrivalInfo = arrive.find_element(By.XPATH, ".//div[starts-with(@class, 'travel-next-day')]").text
            arrivalDate = arrivalInfo
            if arrivalInfo == '': arrivalDate = self.departDate # One day trip
          except NoSuchElementException: # One day trip
            arrivalDate = self.departDate
          
          if name == "Multiple Trains":
            segmentInfo = self.__checkTripDetails(arrive)
          else: segmentInfo = []

          # Trip details contains train amenities and station stops (in groups of ten)

          prices = data.find_element(By.XPATH, ".//div[starts-with(@class, 'search-results-leg-travel-service')]") # Search area
          coachPrice = self.__findPrice(prices, 'coach')
          businessPrice = self.__findPrice(prices, 'business')
          sleeperPrice = self.__findPrice(prices, 'sleeper')

          if not(self.__isSoldOut(coachPrice, businessPrice, sleeperPrice)):
            outputDict = {"Number":number, "Name":name, "Origin":self.origin, "Departure Time":departTime, "Departure Date":self.departDate, "Travel Time":travelTime, "Destination":self.destination, "Arrival Time":arrivalTime, "Arrival Date":arrivalDate, "Coach Price":coachPrice, "Business Price":businessPrice, "Sleeper Price":sleeperPrice, "Segment Type":segmentType, "Segment Info":segmentInfo}
            if USE_TRAIN_CLASSES:
              self.thisSearchResultsAsTrain.update({self.numberTrainsFound : (Train(outputDict))})
            else:
              self.thisSearchResultsAsDict[self.numberTrainsFound] = outputDict
            self.numberTrainsFound += 1
            self.__updateNumberTrainsLabel()

      except Exception as e:
        print(traceback.format_exc())
        print(e) #Reached end of list but there is a second page

  def __checkEveryPage(self, area, pages: int, isScrape: bool=True) -> None:
    """
    Checks every page of search results. If there is one, it does not loop.

    Parameters
    ----------
    area : WebElement
        Search area at the bottom of the page where the page links are located.
    pages : int
        Number of pages of results.
    isScrape: bool, Optional
        Whether to use the old webscraping method (True) or the new JSON method (False), by default False
    """
    
    def scrapingMethod():
      for page in range(1,pages+1): # Starts at 1 (page 1) and goes up to pages
        self.__updateStatusMessage(f"Searching - checking page {page}", 29./pages)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)") # Puts page links in view
        
        # Loads next page and waits until elements load
        area.find_element(By.XPATH, f".//*[text()='{page}']").click()
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, f".//a[text()='{page}']//ancestor::li[@class='pagination-page page-item active ng-star-inserted']")))
        time.sleep(1)
        
        searchResultsTable = self.driver.find_element(By.XPATH, "//div[contains(@class, 'trigger-searchList')]") # Search area
        trainList = searchResultsTable.find_elements(By.XPATH, ".//div[contains(@class, 'trigger-searchItems')]") # List of train results
        self.__findTrainInfo(trainList)
    
    if isScrape:
      scrapingMethod() # We don't need this.
    else:
      if self.__processTrainJson() != True:
        scrapingMethod()

  def __processTrainJson(self, file: dict=None) -> bool:
    """
    New method to get train search results from session storage JSON.

    Parameters
    ----------
    file : dict, optional
        For testing onlt, specify a results dictionary to use, by default None

    Returns
    -------
    bool
        True, if the data was able to be parsed.
    """
    
    try:
      if file == None:
        j = json.loads(self._getSessionStorage("searchresults", True))
      else:
        j = file
        self.__updateStatusMessage('Test', 22)

      _journeySolutionOption = j["journeySolutionOption"]
      _journeyLegs = _journeySolutionOption["journeyLegs"][0]
      _journeyLegOptionsMultiple = _journeyLegs["journeyLegOptions"] #All segments

      for index, opt in enumerate(_journeyLegOptionsMultiple):
        self.__updateStatusMessage(f"Processing results", 28./len(_journeyLegOptionsMultiple))
        try:
          if len(opt["reservableAccommodations"]) > 0: # Not sold out

            # Basic Data Gathering // Compare to __findTrainInfo()
            segmentType = len(opt["travelLegs"])
            if opt["isMultiSegment"] == True: #Multi-segment
              number = "N/A"
              name = "Multiple Trains"
              hasTrain = False
              hasBus = False
              for leg in opt["travelLegs"]:
                if leg["travelService"]["type"].upper() == "TRAIN":
                  hasTrain = True
                elif leg["travelService"]["type"].upper() == "BUS":
                  hasBus = True
              if hasTrain and hasBus: name = "Mixed Service"
              elif hasBus and not hasTrain: name = "Multiple Buses"
              
            elif opt["isMultiSegment"] == False: #Single segment
              number = opt["travelLegs"][0]["travelService"]["number"]
              name = opt["travelLegs"][0]["travelService"]["name"]
            
            origin = opt["origin"]["code"]
            destination = opt["destination"]["code"]

            departure = opt["origin"]["schedule"]["departureDateTime"]
            arrival = opt["destination"]["schedule"]["arrivalDateTime"]
            travelTime = opt["duration"]

            coachPrice = opt["coach"]["lowestPrice"]
            businessPrice = opt["business"]["lowestPrice"]
            sleeperPrice = opt["rooms"]["lowestPrice"]
            
            # Initial data update
            outputDict = {
              "Number":number,
              "Name":name,
              "Origin":origin,
              "Departure":departure,
              "Travel Time":travelTime,
              "Destination":destination,
              "Arrival":arrival,
              "Coach Price":coachPrice,
              "Business Price":businessPrice,
              "Sleeper Price":sleeperPrice,
              "Segments":segmentType,
              "Raw":opt
            }

            # Advanced Data Gathering
            try:
              extra = {}
              for index, seg in enumerate(opt["segments"]):
                _thisAmenities = []
                for amenity in seg["travelLeg"]["travelService"]["amenities"]:
                  _thisAmenities.append(amenity["name"])

                _thisNum = seg["travelLeg"]["travelService"]["number"]
                _thisName = seg["travelLeg"]["travelService"]["name"]
                _thisType = seg["travelLeg"]["travelService"]["type"]

                _thisDest = seg["travelLeg"]["destination"]["code"]
                _thisArrive = seg["travelLeg"]["destination"]["schedule"]["arrivalDateTime"]
                _thisOrigin = seg["travelLeg"]["origin"]["code"]
                _thisDepart = seg["travelLeg"]["origin"]["schedule"]["departureDateTime"]

                _thisDuration = seg["travelLeg"]["elapsedTime"].replace('P','').replace('T',' ').replace('H', 'H ')
                _thisSeatsAvailable = opt["seatCapacityInfo"]["seatCapacityTravelClasses"][index]["availableInventory"]

                extra[seg["travelLegIndex"]] = {
                  "Name": _thisName,
                  "Number":_thisNum,
                  "Type":_thisType,
                  "Origin":_thisOrigin,
                  "Destination":_thisDest,
                  "Departure":_thisDepart,
                  "Arrival":_thisArrive,
                  "Duration":_thisDuration,
                  "Available Seats":_thisSeatsAvailable,
                  "Amenities":_thisAmenities
                }
              
              citySegments = opt["citySegments"]

              outputDict.update({
                "City Segments":citySegments,
                "Segment Info":extra})

            except (KeyError, IndexError) as e:
              print(e)

            if USE_TRAIN_CLASSES:
              self.thisSearchResultsAsTrain.update({self.numberTrainsFound : (Train(outputDict))})
            else:
              self.thisSearchResultsAsDict[self.numberTrainsFound] = outputDict
            self.numberTrainsFound += 1
            self.__updateNumberTrainsLabel()
        except Exception as e:
          print(e)

    except (KeyError, TypeError) as e:
      print(e)
      return False
    if self.numberTrainsFound > 0: # Interim
      return True
    else: return False

  def __enterStationInfo(self, area) -> None:
    """
    Fills in origin and destination fields.

    Parameters
    ----------
    area : WebElement
        Area that contains input fields.
    """
    # Entering departure station info
    fromStationSearchArea = self.driver.find_element(By.XPATH, "//div[@class='from-station flex-grow-1']")
    fromStationSearchArea.find_element(By.XPATH, "//station-search[@amt-auto-test-id='fare-finder-from-station-field-page']").click()
    inputField1 = fromStationSearchArea.find_element(By.XPATH, "//input[@id='mat-input-0']")
    inputField1.clear()
    inputField1.send_keys(self.origin)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'From')]"))) # Station name autofilled
    time.sleep(randint(5,100)/100.)

    # Entering destination station info
    toStationSearchArea = self.driver.find_element(By.XPATH, "//div[@class='to-station flex-grow-1']")
    toStationSearchArea.find_element(By.XPATH, "//station-search[@amt-auto-test-id='fare-finder-to-station-field-page']").click()
    inputField2 = toStationSearchArea.find_element(By.XPATH, "//input[@id='mat-input-1']")
    inputField2.clear()
    inputField2.send_keys(self.destination)
    WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[contains(@aria-label,'To')]"))) # Station name autofilled
    time.sleep(randint(5,100)/100.)

  def __enterDepartDate(self, area) -> None:
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
    time.sleep(randint(5,100)/100.)

  def _getSessionStorage(self, key: str, beCareful: bool=False) -> dict:
    """
    Retrieves an item from session storage.

    Parameters
    ----------
    key : str
        Item to retrieve.
    beCareful : bool, optional
        If True, do NOT refresh the page to get the results, by default False

    Returns
    -------
    dict
        Session storage item.
    """
    time.sleep(1)
    _tc = self.driver.execute_script("return window.sessionStorage.getItem(arguments[0]);", key)
    if _tc == None and beCareful == False:
      self.driver.refresh()
      time.sleep(2)
      _tc = self.driver.execute_script("return window.sessionStorage.getItem(arguments[0]);", key)
    return _tc

  def oneWaySearch(self, isScrape: bool=False) -> dict:
    """
    Performs a search for Amtrak trains on a one-way journey.

    Parameters
    ----------
    isScrape : bool
        If True, use the old scraping method, otherwise use the JSON method.

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
      self.__updateStatusMessage("Searching - loading page", 1)
      if (self.driver.current_url != cfg.SEARCH_URL) or self.returnedError: # If not at the page or an error occurred last time, reload
        self.driver.get(cfg.SEARCH_URL)
      self.returnedError = False
      self.driver.execute_script("window.scrollTo(document.body.scrollHeight, 0)") # Reset after previous search

      # Make sure the page loads and the New Search button is available to us
      WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[starts-with(@class, 'am-btn btn--secondary')]")))

      try: # Clicking the new search button
        self.__updateStatusMessage("Searching - opening input fields", 4)
        newSearchButton = self.driver.find_element(By.XPATH, "//button[starts-with(@class, 'am-btn btn--secondary')]")
        newSearchButton.click()
        time.sleep(1)

        try: # Entering to/from stations
          self.__updateStatusMessage("Searching - entering stations", 2)
          searchArea = self.driver.find_element(By.XPATH, "//div[@id='refineSearch']")
          searchArea = searchArea.find_element(By.XPATH, "//div[starts-with(@class, 'row align-items-center')]")
          self.__enterStationInfo(searchArea)

          try: # Entering departure date
            self.__updateStatusMessage("Searching - entering travel dates", 1)
            self.__enterDepartDate(searchArea)

            # Wait until "Find Trains" button is enabled, then click it
            self.__updateStatusMessage("Searching - starting search", 2)
            WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//button[@aria-label='FIND TRAINS' and @aria-disabled='false']")))
            searchArea.find_element(By.XPATH, "//div[starts-with(@class, 'amtrak-ff-body')]").click() # Get calendar popup out of the way
            time.sleep(randint(5,100)/100.)
            searchArea.find_element(by=By.XPATH, value="//button[@aria-label='FIND TRAINS' and @aria-disabled='false']").click() # Click search button

            # Search has been completed, but there is no service
            try:
              self.__updateStatusMessage("Searching - starting search", 2)
              time.sleep(2)
              self.__updateStatusMessage("Searching - loading results", 3)
              potentialError = self.driver.find_element(By.XPATH, "//div[starts-with(@class, 'alert-yellow-text')]").text
              print(potentialError)
              self.returnedError = True
              self.__updateStatusMessage("Error")
              return potentialError

            # Search has been completed, but we didn't find any trains on that day
            except NoSuchElementException:
              try:
                potentialError = self.driver.find_element(By.XPATH, "//div[@amt-auto-test-id='am-dialog']")
                newDate = potentialError.find_element(By.XPATH, ".//div[starts-with(@class, 'pb-0 mb-5 ng-star-inserted')]").text
                newDateError = '\n'.join(newDate.split("\n")[0:2])
                print(newDateError)
                self.returnedError = True
                self.__updateStatusMessage("Error")
                return newDateError

              # Search has been completed, and we found a train(s)
              except NoSuchElementException:
                try:
                  self.__updateStatusMessage("Searching - parsing results page", 5)
                  WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'trigger-searchList')]")))
                  searchResultsTable = self.driver.find_element(By.XPATH, "//div[contains(@class, 'trigger-searchList')]") # Table of results
                  nextPage = searchResultsTable.find_element(By.XPATH, ".//ul[starts-with(@class, 'pagination paginator__pagination')]") # Page links area
                  numberSearchPages = int((len(nextPage.find_elements(By.XPATH, ".//*"))-4)/2) # Find out how many pages exist
                  self.__checkEveryPage(nextPage, numberSearchPages, isScrape)
                  self.__updateStatusMessage("Done", 50)
                  
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