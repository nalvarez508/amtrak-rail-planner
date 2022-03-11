import datetime

class RailPass:
  def __init__(self):
    self.segments = dict()
    self.segmentResults = dict()
  
  def getSegmentResult(self, index):
    return self.segmentResults[index]

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

class Train:
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
    self.departure = self.convertToDatetime(self.departureDate, self.departureTime)
    self.travelTime = key["Travel Time"]
    self.arrivalTime = key["Arrival Time"]
    self.arrivalDate = key["Arrival Date"]
    self.arrival = self.convertToDatetime(self.arrivalDate, self.arrivalTime)
    self.prettyDeparture, self.prettyArrival = self.makePrettyDates()
    self.coachPrice = key["Coach Price"]
    self.businessPrice = key["Business Price"]
    self.sleeperPrice = key["Sleeper Price"]
    self.segmentType = key["Segment Type"]
    self.numberOfSegments = self.findSegments()

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
  
  def findSegments(self):
    try:
      val = int(self.segmentType.split()[0])
      return val
    except ValueError:
      return 1

  def makePrettyDate(self, dt, compare=False):
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
  
  def makePrettyDates(self):
    def doDayStringPrettification(dt, doDate=""):
      suffix = ""
      if doDate:
        if (dt.day <= 3) or (dt.day > 20):
          day = dt.day % 10
          if day == 1: suffix = "st"
          elif day == 2: suffix = "nd"
          elif day == 3: suffix = "rd"
          else: suffix = "th"
        else:
          suffix = "th"
        if dt.day < 10: doDate = f"%a. {dt.day}"
      return datetime.datetime.strftime(dt, f"{doDate}{suffix} %I:%M%p").strip()

    if self.departure.day == self.arrival.day:
      return [doDayStringPrettification(self.departure), doDayStringPrettification(self.arrival)]
    elif self.departure < self.arrival:
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