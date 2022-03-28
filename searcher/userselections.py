import datetime

from tkinter import messagebox

from views.config import APP_NAME
from traintracks.train import RailPass

class UserSelections:
  """
  A class to hold user selections from the UI.

  Attributes
  ----------
  origin : str
      Key from Stations of the form 'Code | Name, State'
  destination : str
      Key from Stations of the form 'Code | Name, State'
  departDate : datetime.date
  userSelections : RailPass
      Holds selected trip segments.
  
  getPrettyDate()
      Returns `departDate` as a pretty string.
  """
  def __init__(self):
    self.origin = None
    self.destination = None
    self.departDate = datetime.date.today()

    self.userSelections = RailPass()
  
  def isSearchOkay(self):
    mostRecent = self.userSelections.getMostRecentSegment()
    if mostRecent != None:
      if self.__beforeSearch_isSameStationOkay(mostRecent):
        if self.__beforeSearch_isSameDateOkay(mostRecent):
          return True
        else:
          return False
      else:
        return False
    else:
      return True

  def __beforeSearch_isSameDateOkay(self, mostRecent):
    if mostRecent.arrival.date() == self.departDate:
      return messagebox.askyesno(title=APP_NAME, message=f"The selected departure date for this search is the same as the most recent segment's arrival date, scheduled at {mostRecent.arrival.strftime('%I:%M %p')}. Ensure that there is ample time for a transfer.\nContinue with the search?")
    elif mostRecent.arrival.date() > self.departDate:
      return messagebox.askyesno(title=APP_NAME, message=f"The selected departure date for this search is before the most recent segment's arrival date of {mostRecent.arrival.date().strftime('%A, %B %d, %Y')}.\nContinue with the search?")
    else:
      return True
  
  def __beforeSearch_isSameStationOkay(self, mostRecent):
    origin = self.origin.split()[0]
    destination = self.destination.split()[0]
    if (mostRecent.origin == origin) & (mostRecent.destination == destination):
      return messagebox.askyesno(title=APP_NAME, message="The selected origin and destination stations are the same as the previous segment's stations.\nContinue with the search?")
    elif mostRecent.origin == origin:
      return messagebox.askyesno(title=APP_NAME, message="The selected origin station is the same as the previous segment's origin.\nContinue with the search?")
    elif mostRecent.destination == destination:
      return messagebox.askyesno(title=APP_NAME, message="The selected destination station is the same as the previous segment's destination.\nContinue with the search?")
    else:
      return True

  def getPrettyDate(self):
    """
    Formats `departDate` for display in the date selection area.

    Returns
    -------
    str
        String of the form 'Weekday, Mnth. Day, Long Year'.
    """
    def getSuffix():
      if (self.departDate.day <= 3) or (self.departDate.day > 20):
        day = self.departDate.day % 10
        if day == 1: suffix = "st"
        elif day == 2: suffix = "nd"
        elif day == 3: suffix = "rd"
        else: suffix = "th"
      else:
        suffix = "th"
      return suffix
    def dayCheck(): # Removes leading zero
      if self.departDate.day < 10: return self.departDate.day
      else: return "%d"
    return datetime.datetime.strftime(self.departDate, f"%A, %b. {dayCheck()}{getSuffix()}, %Y")

  def getDate(self):
    """
    Returns the departure date.

    Returns
    -------
    datetime.date
        `departDate`
    """
    return self.departDate
  
  def getSearchDate(self):
    """
    Returns the search date as a string.

    Returns
    -------
    str
        `departDate` as mm/dd/yyyy.
    """
    return datetime.datetime.strftime(self.departDate, "%m/%d/%Y")
  
  def setDate(self, d):
    """
    Sets the departure date to d.

    Parameters
    ----------
    d : datetime.date
        New departure date.
    """
    self.departDate = d
  
  def incrementDate(self, i):
    """
    Increments the departure date by some number.

    Parameters
    ----------
    i : int
        Amount to increment. Can be negative.
    """
    self.departDate += datetime.timedelta(days=i)

  def set(self, city, side):
    """
    Generalized set city method.

    Parameters
    ----------
    city : str
        City name in the form 'Code | Name, State'.
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).
    """
    if side == 1:
      self.setOrigin(city)
    elif side == 2:
      self.setDestination(city)

  def setOrigin(self, o):
    """
    Sets the origin key.

    Parameters
    ----------
    o : str
        'Code | Name, State'
    """
    self.origin = o
  def getOrigin(self):
    """
    Returns the origin key.

    Returns
    -------
    str
        'Code | Name, State'
    """
    return self.origin
  
  def setDestination(self, d):
    """
    Sets the destination key.

    Parameters
    ----------
    d : str
        'Code | Name, State'
    """
    self.destination = d
  def getDestination(self):
    """
    Returns the destination key.

    Returns
    -------
    str
        'Code | Name State'
    """
    return self.destination
  
  def addSegment(self, t):
    self.userSelections.createSegment(t)