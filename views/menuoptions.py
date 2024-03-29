import tkinter as tk
from tkinter import messagebox, ttk

import webbrowser
import json
from urllib.parse import quote
from copy import deepcopy
from time import sleep

from views.columnsettings import ColumnSettings
from views.details import DetailWindow
from . import config as cfg

class MenuOptions(tk.Menu):
  """
  A class to hold UI elements for the menu bar.

  Parameters
  ----------
  tk : Menu

  Attributes
  ----------
  helpmenu : Menu
  statusmenu : Menu
  filemenu : Menu
  editmenu : Menu
  viewmenu : Menu
  otpmenu : Menu
      On-time performance, within View menu.

  Methods
  -------
  openLink(l)
      Opens a link in the default web browser.
  openBox(m)
      Displays an info box with a message.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Menu.__init__(self, parent)
    self.parent = parent
    self.timetableUrls = {}

    self.helpmenu = tk.Menu(self, tearoff=0)
    self.helpmenu.add_command(label="About", command=lambda: self.openBox(f"Amtrak Rail Pass Assistant\nv{cfg.APP_VERSION}\nCopyright 2022 Nick Alvarez\n\nRoute map data provided by Transitland."))
    self.helpmenu.add_command(label="Github", command=lambda: self.openLink("https://github.com/nalvarez508/amtrak-rail-planner"))

    self.statusmenu = tk.Menu(self, tearoff=0)
    self.statusmenu.add_command(label="Nationwide", command=lambda: self.openLink("https://asm.transitdocs.com/map"))
    self.statusmenu.add_separator()
    self.statusmenu.add_command(label="Northeast", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=Northeast"))
    self.statusmenu.add_command(label="Northeast Corridor", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=NEC"))
    self.statusmenu.add_command(label="East", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=East"))
    self.statusmenu.add_command(label="Midwest", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=Midwest"))
    self.statusmenu.add_command(label="West", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=West"))
    self.statusmenu.add_command(label="Northwest", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=Northwest"))
    self.statusmenu.add_command(label="California", command=lambda: self.openLink("http://dixielandsoftware.net/cgi-bin/getmap.pl?mapname=Cal"))

    self.filemenu = tk.Menu(self, tearoff=0)
    self.filemenu.add_command(label="New", command=self.parent.newRailFile)
    self.filemenu.add_command(label="Open", command=self.parent.openRailFile)
    self.filemenu.add_command(label="Save", command=self.parent.saveRailFile)
    self.filemenu.add_separator()
    self.filemenu.add_command(label="Export Itinerary", command=self.__openItineraryWithExport)

    self.editmenu = tk.Menu(self, tearoff=0)
    self.editmenu.add_command(label="Display Columns", command=lambda: ColumnSettings(self.parent))

    self.viewmenu = tk.Menu(self, tearoff=0)
    self.viewmenu.add_command(label="Itinerary", command=lambda: self.parent.openItinerary())
    self.viewmenu.add_command(label="Map Window", command=self.parent.openMap)
    self.viewmenu.add_command(label="Amtrak System Map", command=lambda: self.openLink("https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/Maps/Amtrak-System-Map-1018.pdf"))
    
    self.otpmenu = tk.Menu(self, tearoff=0)
    self.otpmenu.add_command(label="via Amtrak", command=lambda: self.openLink("https://www.amtrak.com/on-time-performance"))
    self.otpmenu.add_command(label="via Bureau of Transportation Statistics", command=lambda: self.openLink("https://www.bts.gov/content/amtrak-time-performance-trends-and-hours-delay-cause"))
    self.viewmenu.add_cascade(label="On-Time Performance", menu=self.otpmenu)

    self.add_cascade(label="File", menu=self.filemenu)
    self.add_cascade(label="Edit", menu=self.editmenu)
    self.add_cascade(label="View", menu=self.viewmenu)
    self.add_cascade(label="Status", menu=self.statusmenu)
    self.add_cascade(label="Help", menu=self.helpmenu)

    # Restart both drivers
    # Open station list
    # Column selection for treeview

  def __openItineraryWithExport(self) -> None:
    try:
      self.parent.itineraryWindow.doExport()
    except: # Itinerary window not open
      self.parent.openItinerary(True)

  def openLink(self, l: str) -> None:
    """
    Opens a link in the default web browser.

    Parameters
    ----------
    l : str
        Fully qualified URL.
    """
    webbrowser.open(l, new=1, autoraise=True)
  
  def openBox(self, m: str) -> None:
    """
    Displays an information messagebox.

    Parameters
    ----------
    m : str
        The message to display.
    """
    messagebox.showinfo(cfg.APP_NAME, message=m)
  
  def _loadTimetables(self) -> None:
    # Get some data from session storage
    # For each of the datas, create a menu item
    traincodes = None
    while(traincodes == None):
      try:
        traincodes = json.loads(self.parent.searcher._getSessionStorage('traincodes', True))
      except TypeError as e:
        print("Tried to load train codes", e)
        sleep(5)

    trainnames = list(traincodes.values())
    trainnames_unique = []
    [trainnames_unique.append(x) for x in trainnames if x not in trainnames_unique]

    trainnames_unique_excludes = []
    excludes = ['Connecting Bus', 'Acela Nonstop', 'Self Transfer', 'Coast Starlight Bus', 'ACE Commuter Train', 'Winter Park Express Shuttle', 'Connecting Van', 'Seastreak Ferry', 'Victoria Clipper Ferry', 'Connecting Taxi', 'NJ Transit Train', 'Grand Canyon Railway', 'Lincoln Service Missouri River Runner']
    [trainnames_unique_excludes.append(y) for y in trainnames_unique if y not in excludes]

    for train in sorted(trainnames_unique_excludes):
      baseUrl = "https://duckduckgo.com/?q=!ducky+"
      trainSuffix = quote((train + " train timetable schedule Amtrak filetype:pdf"))
      thisUrl = baseUrl + trainSuffix
      self.timetableUrls[train] = deepcopy(thisUrl)
    
    self._createTimetableMenu()
      
  def _createTimetableMenu(self) -> None:
    timetablesMenu = tk.Menu(self, tearoff=0)
    for train in self.timetableUrls:
      timetablesMenu.add_command(label=train, command=lambda url=self.timetableUrls[train]: self.openLink((url)))
    self.viewmenu.add_cascade(label="Timetables", menu=timetablesMenu)
    self.update()
    self.parent.update()

class TrainMenu(tk.Menu):
  """
  A class for right-click context menu in train results or itinerary.

  Parameters
  ----------
  tk : Menu
  
  Attributes
  ----------
  selectedIID : str
  tree : ttk.Treeview
  inview : list
  
  Methods
  -------
  openTimetable
  openTrainLink
  openDetailView
  openResults
  singleRouteUpdate
      Map update for non-journey (all) routes.
  """
  def __init__(self, parent, tree: ttk.Treeview, inview: dict, save=None, *args, **kwargs) -> None:
    """
    Initializes the right-click context menu.

    Parameters
    ----------
    parent : tk.Tk, tk.Frame, tk.Toplevel
        Parent window.
    tree : ttk.Treeview
        Tree object from the parent.
    inview : dict
        Visible results dictionary from the parent.
    save : function, optional
        Function to save results, by default None
    """
    tk.Menu.__init__(self, parent, tearoff=0)
    self.parent = parent
    self.selectedIID = ''
    self.tree = tree
    self.inview = inview

    if save != None:
      self.add_command(label="Save Segment", command=save)
      self.add_separator()
    self.add_command(label="Route Map", command=self.singleRouteUpdate)
    self.add_command(label="Train Details", command=self.openDetailView)
    self.add_separator()
    if save == None: self.add_command(label="Search Results", command=self.openResults)
    self.add_command(label="Online Info", command=self.openTrainLink)
    self.add_command(label="Timetable", command=self.openTimetable)
  
  def openTimetable(self) -> None:
    """Opens a timetable(s) for the selected result."""
    item = self.tree.item(self.selectedIID)
    trainName = self.inview[item['text']].name.lower()

    segmentInfo = self.inview[item['text']].segmentInfo
    for segment in segmentInfo:
      if segmentInfo[segment]["Type"].upper() == "TRAIN":
        baseUrl = "https://duckduckgo.com/?q=!ducky+"
        trainSuffix = quote((segmentInfo[segment]["Name"] + " train timetable schedule Amtrak filetype:pdf"))
        webbrowser.open((baseUrl + trainSuffix), new=1, autoraise=True)
      elif trainName == 'NA':
        messagebox.showwarning(title=cfg.APP_NAME, message="Cannot view information about multiple segments.")
  
  def openTrainLink(self) -> None:
    """Opens Amtrak train site(s) for the selected result."""
    item = self.tree.item(self.selectedIID)
    segmentInfo = self.inview[item['text']].segmentInfo
    for segment in segmentInfo:
      if segmentInfo[segment]["Type"].upper() == "TRAIN":
        trainName = segmentInfo[segment]["Name"].lower()
        trainName = trainName.replace(' ', '-')
        if ' ' not in trainName:
          if trainName != "NA":
            url = f"https://www.amtrak.com/{trainName}-train"
            webbrowser.open(url, new=1, autoraise=True)
  
  def openDetailView(self) -> None:
    """Spawns a DetailWindow with the item's info."""
    item = self.tree.item(self.selectedIID)
    _train = self.inview[item['text']]

    self.parent.parent.startThread(DetailWindow, [self.parent.parent, _train.organizationalUnit])
  
  def openResults(self) -> None:
    """Pulls up search results in the main window from this item's original search."""
    item = self.parent.getSelection()
    num = self.parent.parent.us.userSelections.getSegmentSearchNum(item["Index"])
    self.parent.parent.resultsHeadingArea.changeSearchView(num)
  
  def singleRouteUpdate(self) -> None:
    """Draws a train route on the map with intermediate stops shown."""
    _thisSelect = self.parent.getSelection(self.selectedIID)
    _name = _thisSelect["Train"].name
    self.parent.parent.openMap()
    if _thisSelect["Train"].numberOfSegments > 1:
      if _thisSelect["Train"].segmentInfo != {}:
        self.parent.parent.mapWindow.drawTrainRoute(_thisSelect["Train"].segmentInfo, _thisSelect["Train"].citySegments)
      else:
        self.parent.parent.mapWindow.drawTrainRoute(_name, [_thisSelect["Train"].origin, _thisSelect["Train"].destination])
    else:
      self.parent.parent.mapWindow.drawTrainRoute(_name, [_thisSelect["Train"].origin, _thisSelect["Train"].destination])