import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import Calendar
from easygui import fileopenbox, filesavebox

import sys
from threading import Thread
import os
import pickle
from copy import deepcopy

from traintracks.maputils import _loadAllRoutes

from searcher.driver import Driver
from searcher.userselections import UserSelections
from searcher.amtrak_searcher import AmtrakSearch

from views import config as cfg
from views.itinerary import Itinerary
from views.titlearea import TitleArea
from views.imagearea import ImageArea
from views.stationsarea import StationsArea
from views.dateselectionarea import DateSelectionArea
from views.resultsheadingarea import ResultsHeadingArea
from views.trainresultsarea import TrainResultsArea
from views.menuoptions import MenuOptions
from views.devtools import DevTools
from views.map import Map

class MainWindow(tk.Tk):
  """
  A class to structure the window, holding other classes of elements.

  Parameters
  ----------
  tk : Tk
  
  Attributes
  ----------
  self : Tk
    Root/master object.
  us : UserSelections
  searcher : AmtrakSearch
  statusMessage : StringVar
      Holds message for status bar at the bottom of the window.
  resultsBackground : str
      Background color for train search results area.
  titleArea : TitleArea
  imageArea : ImageArea
  stationsArea : StationsArea
  dateSelectionArea : DateSelectionArea
  resultsHeadingArea : ResultsHeadingArea
  trainResultsArea : TrainResultsArea
  devTools : DevTools
      Not used in production, only for testing.
  itineraryWindow : Itinerary
      `None` if window is not open.
  statusBar : tk.Label

  Methods
  -------
  openItinerary
      If not already open, spawns an Itinerary object.
  closeItinerary
      Sets `itineraryWindow` to None.
  startThread(function, args=None)
      Starts a thread to run the given function.
  onClose
      Quits the application and closes the webdrivers.
  """
  def __init__(self) -> None:
    super().__init__()
    self.geometry(cfg.GEOMETRY)
    self.minsize(width=cfg.MINSIZE[0], height=cfg.MINSIZE[1])
    self.config(background=cfg.BACKGROUND)
    self.title(cfg.APP_NAME)
    if os.name == 'nt': self.iconbitmap(cfg.ICON)
    self.isSaved = True

    self.us = UserSelections()
    self.searcher = None
    self.statusMessage = tk.StringVar(self, "Ready")
    self.resultsBackground = "gainsboro"

    self.titleArea = TitleArea(self)
    self.imageArea = ImageArea(self)
    self.stationsArea = StationsArea(self)
    self.dateSelectionArea = DateSelectionArea(self)
    self.__setBackground()
    self.resultsHeadingArea = ResultsHeadingArea(self)
    self.trainResultsArea = TrainResultsArea(self)
    #self.devTools = DevTools(self)
    self.itineraryWindow = None
    self.mapWindow = Map(self)
    self.menuOptions = MenuOptions(self)
    self.startThread(self.__startup)
    self.config(menu=self.menuOptions)

    self.statusBar = tk.Label(self, textvariable=self.statusMessage, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    self.statusBar.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.statusBar.lift

    #self.titleArea.pack()
    self.imageArea.pack()
    self.stationsArea.pack()
    self.dateSelectionArea.pack(pady=4)
    self.resultsHeadingArea.pack(fill=tk.X)
    self.trainResultsArea.pack(fill=tk.BOTH, expand=True)

    self.update()

  def newRailFile(self) -> None:
    """
    Wipes out current rail plan, prompting the user to save if necessary.
    """
    def updateElements():
      """Resets widgets and data."""
      self.us.reset()
      self.resultsHeadingArea.changeSearchView(self.us.userSelections.numSearches)
      self.resultsHeadingArea.titleToAndFrom.set("Click \"Find Trains\" to start a search!")
      self.itineraryWindow.updateItinerary()
      self.isSaved = True
      self.title(cfg.APP_NAME)

    if self.isSaved:
      updateElements()
    else:
      ans = messagebox.askyesnocancel(cfg.APP_NAME, "There are unsaved changes. Do you want to save them before starting a new plan?")
      if ans == True:
        if self.saveRailFile():
          updateElements()
      elif ans == False:
        updateElements()
      else: pass

  def openRailFile(self) -> None:
    """
    Opens a railplan file and populates widget info.
    """
    _inpath = fileopenbox(title="Open Rail Planner File", default=os.path.expanduser('~/'), filetypes=['*.railplan', 'Rail Planner Files'])
    if _inpath != None:
      if _inpath.endswith('.railplan'):
        try:
          with open(_inpath, 'rb') as infile:
            _data = pickle.load(infile)
            self.us.userSelections = deepcopy(_data)
            self.resultsHeadingArea.changeSearchView(self.us.userSelections.numSearches)
            self.itineraryWindow.updateItinerary()
            self.isSaved = True
            self.title(cfg.APP_NAME)
        except (FileNotFoundError, OSError):
          messagebox.showerror("Import Rail Plan", "There was an issue reading the file.")
      else:
        messagebox.showerror("Import Rail Plan", "Unsupported file type.")
  
  def saveRailFile(self) -> bool:
    """
    Saves the current rail plan.

    Returns
    -------
    bool
        Sucess in file saving.
    """
    defaultPath = os.path.join(os.path.expanduser('~/'), 'My Plan.railplan')
    _outpath = filesavebox(title="Save Rail Planner File", default=defaultPath, filetypes=['*.railplan', 'Rail Planner Files'])
    if _outpath != None:
      if not _outpath.endswith('.railplan'):
        _outpath += ".railplan"
      try:
        with open(_outpath, 'wb') as outfile:
          pickle.dump(self.us.userSelections, outfile, protocol=pickle.HIGHEST_PROTOCOL)
          self.isSaved = True
          self.title(cfg.APP_NAME)
          return True
      except (FileNotFoundError, OSError):
        messagebox.showerror("Import Rail Plan", "There was an issue writing the file.")
        return False
    else: return False

  def openItinerary(self, spawnExport: bool=False) -> None:
    """
    Opens the itinerary window. If it is already open, bring it to the front.

    Parameters
    ----------
    spawnExport : bool, optional
        If True, open the window and start the export process, by default False
    """
    if self.itineraryWindow == None:
      self.itineraryWindow = Itinerary(self, spawnExport)
    else:
      self.itineraryWindow.lift()
  
  def closeItinerary(self) -> None:
    self.itineraryWindow = None
  
  def openMap(self) -> None:
    """Opens the map. If already open, bring it to the front."""
    if self.mapWindow == None:
      self.mapWindow = Map(self)
    else:
      self.mapWindow.lift()
  
  def closeMap(self) -> None:
    self.mapWindow = None

  def __setBackground(self, f=None) -> None:
    """Sets the background to `cfg.BACKGROUND` for all non-results and non-ttk elements."""
    DONOTCHANGETHESE = [ttk.Button, ttk.Combobox, ttk.Treeview, ttk.Progressbar, ttk.Label, ttk.Frame, ttk.Scrollbar, Calendar]
    if f == None:
      f = self
    if type(f) not in DONOTCHANGETHESE:
      f.config(background=cfg.BACKGROUND)
    for child in f.winfo_children():
      if child.winfo_children():
        self.__setBackground(child)
      else:
        try:
          if type(child) not in DONOTCHANGETHESE:
            child.config(background=cfg.BACKGROUND)
        except tk.TclError as e:
          print(e)
          pass

  def _test_getGeometry(self):
    print("Main Window:", self.geometry(None))
    if self.itineraryWindow != None:
      self.itineraryWindow._test_getGeometry()
  def _test_getBackground(self):
    s1 = ttk.Style()
    bg = s1.lookup("TButton", "background")
    print(bg)

  def startThread(self, function, args: list=None) -> None:
    """
    Starts a thread to run the given function.

    Parameters
    ----------
    function : function
        Input function.
    args : list, optional
        A list of arguments to pass to `function`, by default None
    """
    if args:
      Thread(target=function, args=args).start()
    else:
      Thread(target=function).start()

  def onClose(self) -> None:
    """Closes webdrivers and any windows, if the user has no unsaved changes."""

    def cleanup():
      """Closes application."""
      try: self.devTools.destroy()
      except: pass
      self.destroy()
      # Close webdrivers
      self.imageArea.imageCatcher.driver.close()
      self.imageArea.imageCatcher.driver.quit()
      self.searcher.driver.close()
      self.searcher.driver.quit()
      sys.exit()

    if not self.isSaved:
      ans = messagebox.askyesnocancel(cfg.APP_NAME, message="There are unsaved changes. Do you want to save them before exiting?")
      if ans == True:
        if self.saveRailFile():
          cleanup()
      elif ans == False:
        cleanup()
      else: pass
    else: cleanup()

  def __startup(self) -> None:
    """Launches startup tasks: creating Amtrak searcher, loading routes, loading timetables."""
    _dev = cfg.DEV_MODE
    if not _dev: self.searcher = AmtrakSearch(self, Driver(cfg.SEARCH_URL, undetected=True).driver, status=self.statusMessage)
    else: self.searcher = AmtrakSearch(self, None, status=self.statusMessage)
    self.routes = _loadAllRoutes()
    self.menuOptions._loadTimetables()

if __name__ == "__main__":
  app = MainWindow()
  app.wm_protocol("WM_DELETE_WINDOW", app.onClose)
  app.lift()
  app.mainloop()