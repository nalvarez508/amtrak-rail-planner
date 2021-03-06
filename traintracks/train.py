import datetime
from copy import deepcopy

class RailPass:
  """
  A class to hold each user-selected segment of their journey.

  Attributes
  ----------
  numSegments : int
      Number of currently saved segments, starting at 1, inclusive.
  numSearches : int
      Number of searches performed.
  segments : dict
      Holds an ordered dictionary of {Segment Number : Train object}.
  segmentResults : dict
      Holds mapping from segment number to `allResults` index.
  allResults : dict
      Stores every search performed.
  
  Methods
  -------
  updateSearch(num, saved)
      Updates `allResults` key with any new saved segments.
  addSearch(origin, destination, date, s)
      Adds a new search to `allResults`
  getSearch(num)
      Returns a the *n*-th search.
  getSegmentSearchNum(segment)
      Returns search results index in `allResults` for a given segment.
  getSegments
      Returns all saved segments.
  createCsv(path, cols)
      Creates a dictionary of `segments` and writes to a file.
  createSegment(segment, searchNum):
      Creates a Rail Pass segment.
  deleteSegment(segment)
      Deletes the specified segment and updates the ordering.
  swapSegment(segment, direction)
      Moves a segment "up" or "down" in the ordering.
  getMostRecentSegment
      Returns the most recent segment.
  """
  def __init__(self):
    self.numSegments = 1
    self.numSearches = 0
    self.segments = dict()
    self.segmentResults = dict()
    self.allResults = dict()
  
  def updateSearch(self, num, saved):
    """
    Updates a `allResults` key dict with any new saved segments.

    Parameters
    ----------
    num : int
        Search number.
    saved : list
        List of indices in the results with saved segments.
    """
    if saved == []: self.allResults[num]["Has Segment Saved"] = False
    else: self.allResults[num]["Has Segment Saved"] = True
    self.allResults[num]["Saved Index"] = saved

  def addSearch(self, origin, destination, date, s):
    """
    Adds search results to `allResults`.

    Parameters
    ----------
    origin : str
        'Name, State (Code)'
    destination : str
        'Name, State (Code)'
    date : datetime.date
        Departure date.
    s : dict
        Search results.
    """
    self.numSearches += 1
    self.allResults[self.numSearches] = {"Origin": origin, "Destination": destination, "Date": date, "Has Segment Saved": False, "Results": s, "Saved Index": []}
  
  def getSearch(self, num):
    """
    Gets a dictionary at search number.

    Parameters
    ----------
    num : int
        Search number.

    Returns
    -------
    dict
        Dictionary including "Results" key.
    """
    return self.allResults[num]
  def getSegmentSearchNum(self, segment):
    """
    Returns a search number for the given segment.

    Parameters
    ----------
    segment : int
        The segment number.

    Returns
    -------
    int
        Search number.
    """
    return self.segmentResults[segment]

  def getSegments(self):
    """
    Returns all saved segments.

    Returns
    -------
    dict
        Full of Trains!
    """
    return self.segments

  def createCsv(self, path, cols):
    """
    Writes data to a CSV file.

    Parameters
    ----------
    path : os.path
        Path to save the file at, including file name.
    cols : dict
        Columns as returned by `UserSelections.getExportColumns()`

    Returns
    -------
    bool
        Success of failure of writing the file.
    """
    output = str()
    headerRow = "Leg,"
    hasWrittenHeaders = False
    try:
      for segment in (self.segments): # For every train
        thisTrain = self.segments[segment].organizationalUnit # Get its dictionary
        output += str(str(segment) + ',')

        for col in cols: # For every attribute
          if cols[col]["Selected"] == True: # Check if it is selected
            if not hasWrittenHeaders: headerRow += str(str(cols[col]["Header"]) + ',') # Add it to header row
            item = thisTrain[col]
            if type(item) == datetime.datetime:
              item = self.segments[segment]._makePrettyDates(obj=item, forcePretty=True)
            output += str(str(item).replace(',', ';') + ',') # Add train attribute

        hasWrittenHeaders = True
        output += '\n'

      try:
        headerRow += '\n'
        with open(path, 'w') as f:
          f.write(headerRow+output)
        return True
      except Exception as e:
        print(e)
        return False
    except Exception as e:
      print(e)
      return False

  def createSegment(self, segment, searchNum):
    """
    Creates a saved Rail Pass segment.

    Parameters
    ----------
    segment : Train
    searchNum : int
        Current search number.
    """
    self.segments[self.numSegments] = segment
    self.allResults[self.numSearches]["Has Segment Saved"] = True
    self.segmentResults[self.numSegments] = searchNum
    self.numSegments += segment.numberOfSegments
  
  def __adjust(self, segment):
    """Finds segments around (left or right) a given segment number."""
    keys = list(self.segments.keys())
    removing = keys.index(segment)
    _curr = self.segments[segment].numberOfSegments
    try: _prev = self.segments[keys[removing-1]].numberOfSegments
    except (IndexError, ValueError, KeyError): _prev=0
    try: _next = self.segments[keys[removing+1]].numberOfSegments
    except (IndexError, ValueError, KeyError): _next=0
    return [_prev, _curr, _next]

  def deleteSegment(self, segment):
    """
    Deletes a segment from `segments` and reorders the dictionary.

    Parameters
    ----------
    segment : int
        Segment number.

    Returns
    -------
    int
        Search number that was affected, for reloading the treeview.
    """
    doBreak = False
    affectedSearch = -1
    for search in self.allResults: # Get indexes
      if self.allResults[search]["Has Segment Saved"] == True:
        for train in self.allResults[search]["Results"]:
          if self.allResults[search]["Results"][train] == self.segments[segment]:
            try:
              self.allResults[search]["Saved Index"].remove(train)
              self.allResults[search]["Has Segment Saved"] == True
              affectedSearch = search
              # This will not update the treeview until the search is reloaded
              # ie left then right in search results
              doBreak = True
              break
            except ValueError:
              pass
        if doBreak: break

    cutBy = self.segments[segment].numberOfSegments

    self.segmentResults.pop(segment)
    self.segments.pop(segment)

    for num in (list(self.segments)):
      if num > segment:
        self.segments[num-cutBy] = self.segments.pop(num)
  
    for index in list(self.segmentResults):
      if index > segment:
        self.segmentResults[index-cutBy] = self.segmentResults.pop(index)
    self.numSegments -= cutBy
    return affectedSearch

  def swapSegment(self, segment, direction):
    """
    Moves a segment "up" or "down" in the itinerary.

    Parameters
    ----------
    segment : int
        Segment number.
    direction : str
        'up' or 'down'
    """
    def moveDown(container):
      theUserSegment = container.pop(segment)
      theSegmentGettingBumped = container.pop(segment+_curr)
      container[segment] = theSegmentGettingBumped
      container[segment+_next] = theUserSegment
    
    def moveUp(container):
      theUserSegment = container.pop(segment)
      theSegmentGettingBumped = container.pop(segment-_prev)
      container[segment-_prev] = theUserSegment
      container[segment-_prev+_curr] = theSegmentGettingBumped

    _prev,_curr,_next = self.__adjust(segment)

    if direction == 'down': #Affect itself and after
      moveDown(self.segments)
      moveDown(self.segmentResults)

    elif direction == 'up': #Affect itself and before
      moveUp(self.segments)
      moveUp(self.segmentResults)

    self.segments = {key: value for key, value in sorted(self.segments.items())}
    self.segmentResults = {key: value for key, value in sorted(self.segmentResults.items())}

  def getMostRecentSegment(self):
    """
    Returns the most recent segment object.

    Returns
    -------
    Train
        The most recent saved segment as a Train object.
    """
    if len(self.segments.keys()) > 1: #Compare length dict keys
      num = list(self.segments.keys())[-1]
      return self.segments[num]
    else:
      return None

  def _printRailPass(self):
    for item in self.segments:
      print(item)
      print(self.segments[item])

class Train:
  """
  A class to store a single train journey's information.

  Attributes
  ----------
  origin : str
  destination : str
  number : int or str
      Train number or N/A if mixed service/multiple/unobtainable.
  name : str
  departureTime : str
  departureDate : str
  departure : datetime.datetime
      Combines departure date and time.
  travelTime : str
  arrivalTime : str
  arrivalDate : str
  arrival : datetime.datetime
      Combines arrival date and time.
  prettyDeparture : str
      Display string of `departure`.
  prettyArrival : str
      Display string of `arrival`.
  coachPrice : str
  businessPrice : str
  sleeperPrice : str
  segmentType : str
      Information about segment (direct, multiple)
  numberOfSegments : int
      Total trip segments, defaults to 1 unless other info is available.
  organizationalUnit : dict
      Structured representation of the Train object for use in a Treeview object.

  Methods
  -------
  returnSelectedElements(cols)
      Gets a list of elements that match certain attributes in the `organizationalUnit`.
  """
  def __init__(self, key):
    """
    Initializes the Train object,

    Parameters
    ----------
    key : dict
        Train information.
    """
    self.origin = key["Origin"]
    self.destination = key["Destination"]
    try:
      self.number = int(key["Number"])
    except ValueError:
      self.number = key["Number"]
    self.name = key["Name"]
    self.departureTime = key["Departure Time"]
    self.departureDate = key["Departure Date"]
    self.departure = self.__convertToDatetime(self.departureDate, self.departureTime)
    self.travelTime = key["Travel Time"]
    self.arrivalTime = key["Arrival Time"]
    self.arrivalDate = key["Arrival Date"]
    self.arrival = self.__convertToDatetime(self.arrivalDate, self.arrivalTime)
    self.prettyDeparture, self.prettyArrival = self._makePrettyDates()
    self.coachPrice = key["Coach Price"]
    self.businessPrice = key["Business Price"]
    self.sleeperPrice = key["Sleeper Price"]
    self.segmentType = key["Segment Type"]
    self.numberOfSegments = self.__findSegments()

    self.organizationalUnit = {
      "Origin":self.origin,
      "Destination":self.destination,
      "Number":self.number,
      "Name":self.name,
      "Arrival Time":self.arrivalTime,
      "Arrival Date":self.arrivalDate,
      "Arrival Datetime":self.arrival,
      "Arrives":self.prettyArrival,
      "Duration":self.travelTime,
      "Departure Time":self.departureTime,
      "Departure Date":self.departureDate,
      "Departure Datetime":self.departure,
      "Departs":self.prettyDeparture,
      "Coach Price":self.coachPrice,
      "Business Price":self.businessPrice,
      "Sleeper Price":self.sleeperPrice,
      "Segment Type":self.segmentType,
      "Number of Segments":self.numberOfSegments
    }

  def __str__(self):
    return f"{self.organizationalUnit}"
  
  def __eq__(self, other):
    if other != None:
      if self.number == other.number:
        if self.departure == other.departure:
          return True
        else: return False
      else: return False
    else: return False

  def __findSegments(self):
    """
    Tries to find out how many segments this journey has.

    Returns
    -------
    int
        Number of segments.
    """
    try:
      val = int(self.segmentType.split()[0])
      return val
    except ValueError:
      return 1

  def __makePrettyDate(self, dt, compare=False):
    def doDayStringPrettification(doDate=""):
      suffix = ""
      if doDate:
        day = dt.day % 10
        if day == 1: suffix = "st"
        elif day == 2: suffix = "nd"
        elif day == 3: suffix = "rd"
        else: suffix = "th"
        if dt.day < 10: doDate = f"%a. {dt.day}"
      return datetime.datetime.strftime(dt, f"{doDate}{suffix} %I:%M%p").strip()
    
    if compare == True:
      if self.departure.day == self.arrival.day:
        return doDayStringPrettification()
      elif self.departure.day < self.arrival.day:
        return doDayStringPrettification("%a. %-d")
    elif compare == False:
      return doDayStringPrettification()
  
  def _makePrettyDates(self, obj=None, forcePretty=False):
    """
    Removes leading zeroes, potentially fixes the year, and adds a suffix to the date display string.

    Parameters
    ----------
    obj : Train datetime.datetime attribute, optional
        Object to modify, by default None
    forcePretty : bool, optional
        Forces to return a string with full date, by default False
    """
    def doDayStringPrettification(dt, doDate=""): # doDate is the strftime format for weekday and day#
      suffix = ""
      if doDate:
        if (dt.day <= 3) or (dt.day > 20): # Add 'th' to any dates 4th-20th
          day = dt.day % 10
          if day == 1: suffix = "st"
          elif day == 2: suffix = "nd"
          elif day == 3: suffix = "rd"
          else: suffix = "th"
        else:
          suffix = "th"
        if dt.day < 10: doDate = f"%a. {dt.day}"
      return datetime.datetime.strftime(dt, f"{doDate}{suffix} %I:%M%p").strip()

    if forcePretty:
      return doDayStringPrettification(obj, "%a. %d")
    elif self.departure.day == self.arrival.day: # Only return the times
      return [doDayStringPrettification(self.departure), doDayStringPrettification(self.arrival)]
    elif self.departure < self.arrival: # Return day of week, date, time
      return [doDayStringPrettification(self.departure, "%a. %d"), doDayStringPrettification(self.arrival, "%a. %d")]

  def returnSelectedElements(self, cols):
    """
    Given a list of attributes, return the corresponding values from `organizationalUnit`.

    Parameters
    ----------
    cols : list
        Attributes to find from `organizationalUnit`.

    Returns
    -------
    list
        Values from corresponding attributes.
    """
    temp = list()
    for col in cols:
      try:
        currentValue = self.organizationalUnit[col]
        if type(currentValue) == datetime.datetime:
          currentValue = self._makePrettyDates(currentValue, forcePretty=True)
        temp.append(currentValue)

      except KeyError:
      # Passed in an incorrect attribute name
        temp.append('')
        print(f"Attribute {col} is not recognized.")
    return temp

  def __convertToDatetime(self, d, t):
    """
    Takes in strings of date and time and creates an object.

    Parameters
    ----------
    d : str
        Date in the form mm/dd/yyyy or Weekday, Mnth. Day
    t : str
        Time in the form HH:MMp

    Returns
    -------
    datetime.datetime
        Converted object.
    
    Notes
    -----
    Often the arrival date, if it isn't the same day as the departure date, is not a very friendly format to work with. Creating a datetime object does not input the year and defaults to 1900. We first try to replace this with the departure year and if that fails, the current year.
    """
    t = t.replace("p", "PM")
    t = t.replace("a", "AM")
    try:
      return datetime.datetime.strptime(f"{d} {t}", "%m/%d/%Y %I:%M%p")
    except:
      newObject = datetime.datetime.strptime(f"{d} {t}", "%a, %b %d %I:%M%p")
      if newObject.year == 1900:
        try:
          newObject = newObject.replace(year=self.departure.year)
        except:
          newObject = newObject.replace(year=datetime.datetime.now().year)
      return newObject