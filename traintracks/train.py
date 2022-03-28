import datetime

class RailPass:
  """
  A class to hold each user-selected segment of their journey.

  Attributes
  ----------
  segments : dict
      Holds an ordered dictionary of {Segment Number : Train object}.
  segmentResults : dict
      Holds dictionaries of selected segments' search results.
  
  Methods
  -------
  getSegmentResult(index)
      Returns search results for a given segment.
  createCsv()
      Creates a dictionary of `segments` for later writing to a file.
  createSegment():
      Undefined.
  """
  def __init__(self):
    self.numSegments = 1
    self.numRecentSegment = 1
    self.segments = dict()
    self.segmentResults = dict()
  
  def getSegmentResult(self, index):
    """
    Returns the search results of a given segment.

    Parameters
    ----------
    index : int
        The segment number.

    Returns
    -------
    dict
        A dictionary of Train objects.
    """
    return self.segmentResults[index]

  def createCsv(self):
    """
    Loads data into a dictionary for writing to a CSV file.

    Returns
    -------
    dict
        Dictionary with defined columns ready for writing to file.
    """
    output = dict()
    for segment, train in enumerate(self.segments):
      output.update({segment:train.convertToCsvRow()})
    return output
  
  def createSegment(self, segment, searchResults):
    self.numRecentSegment = self.numSegments
    self.segments[self.numSegments] = segment
    self.segmentResults[self.numSegments] = searchResults
    self.numSegments += segment.numberOfSegments
  
  def getMostRecentSegment(self):
    if self.numSegments > 1:
      return self.segments[self.numRecentSegment]
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
    self.prettyDeparture, self.prettyArrival = self.__makePrettyDates()
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
      "Departure Time":self.departureTime,
      "Departure Date":self.departureDate,
      "Departs":self.prettyDeparture,
      "Duration":self.travelTime,
      "Arrival Time":self.arrivalTime,
      "Arrival Date":self.arrivalDate,
      "Arrives":self.prettyArrival,
      "Coach Price":self.coachPrice,
      "Business Price":self.businessPrice,
      "Sleeper Price":self.sleeperPrice,
      "Segment Type":self.segmentType,
      "Number of Segments":self.numberOfSegments
    }

  def __str__(self):
    return f"{self.organizationalUnit}"
  
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
  
  def __makePrettyDates(self):
    """
    Removes leading zeroes, potentially fixes the year, and adds a suffix to the date display string.

    Parameters
    ----------
    dt : datetime.datetime
        Object to turn into string.
    compare : bool, optional
        Compares `departure` to `arrival` to fix the year, by default False
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

    if self.departure.day == self.arrival.day: # Only return the times
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
        temp.append(self.organizationalUnit[col])
      except KeyError:
      # Passed in an incorrect attribute name
        temp.append('')
        print(f"Attribute {col} is not recognized.")
    return temp

  def convertToCsvRow(self):
    """Returns a dictionary of items ready to be written to a spreadsheet."""
    tempDict = dict()
    tempDict["Origin"] = self.origin
    tempDict["Destination"] = self.destination
    tempDict["Train"] = f"{self.name} {self.number}"
    tempDict["Departs"] = datetime.datetime.strftime(self.departure, "%a %d %I:%M%p")
    tempDict["Arrives"] = datetime.datetime.strftime(self.arrival, "%a %d %I:%M%p")
    tempDict["Duration"] = self.travelTime
    return tempDict

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