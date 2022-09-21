import datetime
from copy import deepcopy

from tkinter import messagebox

from views.config import APP_NAME
from traintracks.train import RailPass, Train

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
  columns : dict
      Defines columns for treeview objects and the column picker.
  exportColumns : dict
      Defines columns for output spreadsheet.
  
  Methods
  -------
  setColumns(vals)
      Updates the "Selected" state of the `columns` object.
  getColumns
      Returns the columns.
  setExportColumns(vals)
      Updates the export columns, changing the date related columns.
  getDisplayColumns
      Creates elements for a treeview object.
  isSearchOkay
      Performs search validation.
  addSegment(t)
      Adds a Rail Pass segment.
  getPrettyDate
      Returns `departDate` as a pretty string.
  And plenty of other fun get/set methods...
  """
  def __init__(self) -> None:
    self.origin = None
    self.destination = None
    self.departDate = datetime.date.today()
    self.userSelections = RailPass()

    self.columns = {
      "Origin": {"Display Name": "Origin", "Header": "Origin", "Width": 55, "Selected": False},
      "Destination": {"Display Name": "Destination", "Header": "Destination", "Width": 55, "Selected": False},
      "Number": {"Display Name": "Train Number", "Header": "#", "Width": 30, "Selected": True},
      "Name": {"Display Name": "Train Name", "Header": "Train", "Width": 175, "Selected": True},
      "Departs": {"Display Name": "Departure Date/Time", "Header": "Departs", "Width": 150, "Selected": True},
      "Arrives": {"Display Name": "Arrival Date/Time", "Header": "Arrives", "Width": 150, "Selected": True},
      "Duration": {"Display Name": "Travel Time", "Header": "Duration", "Width": 65, "Selected": True},
      "Coach Price": {"Display Name": "Coach Price", "Header": "Coach ($)", "Width": 60, "Selected": False},
      "Business Price": {"Display Name": "Business Price", "Header": "Business ($)", "Width": 60, "Selected": False},
      "Sleeper Price": {"Display Name": "Sleeper Price", "Header": "Sleeper ($)", "Width": 60, "Selected": False},
      "Number of Segments": {"Display Name": "Number of Segments", "Header": "Segments", "Width": 65, "Selected": True}
    }
    self.exportColumns = deepcopy(self.columns)

  def setColumns(self, vals: dict) -> None:
    """
    Updates the dictionary of selected columns.

    Parameters
    ----------
    vals : dict
        Column : Selected format, all columns required.
    """
    for col in vals:
      self.columns[col]["Selected"] = vals[col]

  def getColumns(self) -> dict[dict]:
    """
    Gets the column settings, in the form {Train Column: {Display Name, Header, Width, Selected}}

    Returns
    -------
    dict
        Columns.
    """
    return self.columns
  
  def setExportColumns(self, vals: dict):
    """
    Updates the columns to be used when exporting a spreadsheet. Date columns are turned into datetime objects.

    Parameters
    ----------
    vals : dict
        True or False for "Selected."
    """
    for col in vals:
      self.exportColumns[col]["Selected"] = vals[col]
    replacements = [('Arrives', 'Arrival Datetime'), ('Departs', 'Departure Datetime')]
    for r in (replacements): # Replace with full dates and times, if selected in display cols
      try:
        thisColVal = self.exportColumns.pop(r[0])
        self.exportColumns[r[1]] = thisColVal
      except ValueError:
        pass

  def getDisplayColumns(self) -> list:
    """
    Creates elements for a treeview object.

    Returns
    -------
    list
        Train object columns, headers with width, and display names.
    """
    columns = list()
    headerCols = dict()
    dispCols = list()
    for col in self.columns:
      columns.append(col)
      headerCols[self.columns[col]["Header"]] = self.columns[col]["Width"]
      if self.columns[col]["Selected"] == True:
        dispCols.append(col) # Creates mapping so we can retrieve Train objects later
    return [columns, headerCols, dispCols]

  def isSearchOkay(self) -> bool:
    """
    Performs validations at search time for station selections and departure date.

    Returns
    -------
    bool
        Continue the search if True.
    """
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

  def __beforeSearch_isSameDateOkay(self, mostRecent: Train) -> bool:
    if mostRecent.arrival.date() == self.departDate:
      return messagebox.askyesno(title=APP_NAME, message=f"The selected departure date for this search is the same as the most recent segment's arrival date, scheduled at {mostRecent.arrival.strftime('%I:%M %p')}. Ensure that there is ample time for a transfer.\nContinue with the search?")
    elif mostRecent.arrival.date() > self.departDate:
      return messagebox.askyesno(title=APP_NAME, message=f"The selected departure date for this search is before the most recent segment's arrival date of {mostRecent.arrival.date().strftime('%A, %B %d, %Y')}.\nContinue with the search?")
    else:
      return True
  
  def __beforeSearch_isSameStationOkay(self, mostRecent: Train) -> bool:
    # Patchwork
    origin = self.origin[self.origin.find("(")+1:self.origin.find(")")]
    destination = self.destination[self.destination.find("(")+1:self.destination.find(")")]
    if (mostRecent.origin == origin) & (mostRecent.destination == destination):
      return messagebox.askyesno(title=APP_NAME, message="The selected origin and destination stations are the same as the previous segment's stations.\nContinue with the search?")
    elif mostRecent.origin == origin:
      return messagebox.askyesno(title=APP_NAME, message="The selected origin station is the same as the previous segment's origin.\nContinue with the search?")
    elif mostRecent.destination == destination:
      return messagebox.askyesno(title=APP_NAME, message="The selected destination station is the same as the previous segment's destination.\nContinue with the search?")
    else:
      return True

  def getPrettyDate(self) -> str:
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

  def getDate(self) -> datetime.date:
    """
    Returns the departure date.

    Returns
    -------
    datetime.date
        `departDate`
    """
    return self.departDate
  
  def getSearchDate(self) -> str:
    """
    Returns the search date as a string.

    Returns
    -------
    str
        `departDate` as mm/dd/yyyy.
    """
    return datetime.datetime.strftime(self.departDate, "%m/%d/%Y")
  
  def setDate(self, d: datetime.date) -> None:
    """
    Sets the departure date to d.

    Parameters
    ----------
    d : datetime.date
        New departure date.
    """
    self.departDate = d
  
  def incrementDate(self, i: int) -> None:
    """
    Increments the departure date by some number.

    Parameters
    ----------
    i : int
        Amount to increment. Can be negative.
    """
    _today = datetime.datetime.now()
    if i < 0:
      if self.departDate > _today.date():
        self.departDate += datetime.timedelta(days=i)
    elif i > 0:
      self.departDate += datetime.timedelta(days=i)

  def set(self, city: str, side: int) -> None:
    """
    Generalized set city method.

    Parameters
    ----------
    city : str
        City name in the form 'Name, State (Code)'.
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).
    """
    if side == 1:
      self.setOrigin(city)
    elif side == 2:
      self.setDestination(city)

  def setOrigin(self, o: str) -> None:
    """
    Sets the origin key.

    Parameters
    ----------
    o : str
        'Name, State (Code)'
    """
    self.origin = o
  def getOrigin(self) -> str:
    """
    Returns the origin key.

    Returns
    -------
    str
        'Name, State (Code)'
    """
    return self.origin
  
  def setDestination(self, d: str) -> None:
    """
    Sets the destination key.

    Parameters
    ----------
    d : str
        'Name, State (Code)'
    """
    self.destination = d
  def getDestination(self) -> str:
    """
    Returns the destination key.

    Returns
    -------
    str
        'Name, State (Code)'
    """
    return self.destination
  
  def addSegment(self, t: Train) -> None:
    """
    Adds a segment to the railpass.
    
    Parameters
    ----------
    t : Train
        The segment object.
    """
    self.userSelections.createSegment(t)