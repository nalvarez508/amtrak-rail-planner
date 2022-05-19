import tkinter as tk

import webbrowser
import json
from urllib.parse import quote
from copy import deepcopy
from time import sleep

from views.columnsettings import ColumnSettings
from . import config as cfg

class MenuOptions(tk.Menu):
  """
  A class to hold UI elements for the menu bar.

  Parameters
  ----------
  tk : Tk
      The parent frame.

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
    self.helpmenu.add_command(label="About", command=lambda: self.openBox(f"Amtrak Rail Pass Assistant\nv{cfg.APP_VERSION}"))
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
    self.filemenu.add_command(label="Import")
    self.filemenu.add_command(label="Export", command=self.__openItineraryWithExport)

    self.editmenu = tk.Menu(self, tearoff=0)
    self.editmenu.add_command(label="Display Columns", command=lambda: ColumnSettings(self.parent))

    self.viewmenu = tk.Menu(self, tearoff=0)
    self.viewmenu.add_command(label="Itinerary", command=lambda: self.parent.openItinerary())
    self.viewmenu.add_command(label="Current Journey", command=self.parent.openMap)
    self.viewmenu.add_command(label="Route Map", command=lambda: self.openLink("https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/Maps/Amtrak-System-Map-1018.pdf"))
    
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

  def __openItineraryWithExport(self):
    try:
      self.parent.itineraryWindow.doExport()
    except: # Itinerary window not open
      self.parent.openItinerary(True)

  def openLink(self, l):
    """
    Opens a link in the default web browser.

    Parameters
    ----------
    l : str
        Fully qualified URL.
    """
    webbrowser.open(l, new=1, autoraise=True)
  
  def openBox(self, m):
    """
    Displays an information messagebox.

    Parameters
    ----------
    m : str
        The message to display.
    """
    tk.messagebox.showinfo(cfg.APP_NAME, message=m)
  
  def _loadTimetables(self):
    # Get some data from session storage
    # For each of the datas, create a menu item
    traincodes = None
    while(traincodes == None):
      traincodes = json.loads(self.parent.searcher._getSessionStorage('traincodes'))
      sleep(0.1)

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
      
  def _createTimetableMenu(self):
    timetablesMenu = tk.Menu(self, tearoff=0)
    for train in self.timetableUrls:
      timetablesMenu.add_command(label=train, command=lambda url=self.timetableUrls[train]: self.openLink((url)))
    self.viewmenu.add_cascade(label="Timetables", menu=timetablesMenu)
    self.update()
    self.parent.update()