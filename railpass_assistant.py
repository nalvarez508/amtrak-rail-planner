import tkinter as tk
from tkinter import ttk

import sys
from threading import Thread, Event, Lock

from searcher.driver import Driver
from searcher.userselections import UserSelections
from searcher.amtrak_searcher import AmtrakSearch

from views import config as cfg
from views.titlearea import TitleArea
from views.imagearea import ImageArea
from views.stationsarea import StationsArea
from views.dateselectionarea import DateSelectionArea
from views.resultsheadingarea import ResultsHeadingArea
from views.trainresultsarea import TrainResultsArea
from views.menuoptions import MenuOptions
from views.devtools import DevTools

class MainWindow(tk.Tk):
  """
  A class to structure the window, holding other classes of elements.

  Parameters
  ----------
  tk : Tk
      Root object. Initialized in `__init__()`.
  
  Attributes
  ----------
  self : Tk
    Root/master object.
  us : UserSelections
  searcher : AmtrakSearch
  statusMessage : StringVar
      Holds message for status bar at the bottom of the window.
  imageDriverLock : threading.Lock
      Used to stop two requests from getting to the WebDriver at the same time.
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
  statusBar : tk.Label

  Methods
  -------
  startThread(function, args=None)
      Starts a thread to run the given function.
  onClose()
      Quits the application and closes the webdrivers.
  doRefresh(city, side, isSwap=False, lock=None)
      Refreshes the images in the window with new cities.
  """
  def __init__(self):
    super().__init__()
    self.geometry(cfg.GEOMETRY)
    self.minsize(width=cfg.MINSIZE[0], height=cfg.MINSIZE[1])
    self.config(background=cfg.BACKGROUND)
    self.title("Rail Pass Planner")
    self.iconbitmap("Amtrak_square.ico")
    self.us = UserSelections()
    self.searcher = None
    self.statusMessage = tk.StringVar(self, "Ready")
    self.startThread(self.__startup)
    self.imageDriverLock = Lock()
    self.resultsBackground = "gainsboro"

    self.titleArea = TitleArea(self)
    self.imageArea = ImageArea(self)
    self.stationsArea = StationsArea(self)
    self.dateSelectionArea = DateSelectionArea(self)
    self.__setBackground()
    self.resultsHeadingArea = ResultsHeadingArea(self)
    self.trainResultsArea = TrainResultsArea(self)
    self.devTools = DevTools(self)
    self.config(menu=MenuOptions(self))

    self.statusBar = tk.Label(self, textvariable=self.statusMessage, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    self.statusBar.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.statusBar.lift

    self.titleArea.pack()
    self.imageArea.pack()
    self.stationsArea.pack()
    self.dateSelectionArea.pack(pady=4)
    self.resultsHeadingArea.pack(fill=tk.X)
    self.trainResultsArea.pack(fill=tk.BOTH, expand=True)

    self.update()

  def __setBackground(self, f=None):
    """Sets the background to `cfg.BACKGROUND` for all non-results and non-ttk elements."""
    DONOTCHANGETHESE = [ttk.Button, ttk.Combobox, ttk.Treeview, ttk.Progressbar, ttk.Label, ttk.Frame, ttk.Scrollbar]
    if f == None:
      f = self
    if type(f) not in DONOTCHANGETHESE:
      f.config(background=cfg.BACKGROUND)
    for child in f.winfo_children():
      if child.winfo_children():
        self.__setBackground(child)
      else:
        try:
          #print(f"Before check: ///{f, child}///\n")
          if type(child) not in DONOTCHANGETHESE:
            #print(f"Child {child} made it through.\n\n")
            child.config(background=cfg.BACKGROUND)
        except tk.TclError as e:
          print(e)
          pass

  def __test_getGeometry(self):
    print(self.geometry(None))
  def __test_getBackground(self):
    s1 = ttk.Style()
    bg = s1.lookup("TButton", "background")
    print(bg)

  def startThread(self, function, args=None):
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

  def onClose(self):
    self.devTools.destroy()
    self.destroy()
    # Close webdrivers
    self.imageArea.imageCatcher.driver.close()
    self.searcher.driver.close()
    self.imageArea.imageCatcher.driver.quit()
    self.searcher.driver.quit()
    sys.exit()

  def __startup(self):
    self.searcher = AmtrakSearch(self, Driver(cfg.SEARCH_URL).driver, status=self.statusMessage)

  def doRefresh(self, city, side, isSwap=False, lock=None):
    """
    Refreshes the ImageArea labels with new cities.

    Parameters
    ----------
    city : str
        'City, State'
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).
    isSwap : bool, optional
        True if the images are only being swapped, by default False
    lock : threading.Lock, optional
        ImageCatcher lock so WebDriver does not get multiple requests at once, by default None
    
    Raises
    ------
    AttributeError
        Lock was not passed to function.
    """
    if isSwap == False:
      if city != self.imageArea.imageCatcher.getCityName(side): # Do not update anything if the same city is selected
        self.imageArea.imageCatcher.setCityPhoto(side, None) # Remove the photo to indicate something is happening
        self.imageArea.updateImage(side)
        try:
          with lock:
            self.imageArea.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS) # Find a new image
        except AttributeError:
          self.imageArea.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS)
        self.imageArea.updateImage(side)
    elif isSwap == True: # Do not call search functions
      self.imageArea.updateImage(side)
    self.update_idletasks()

if __name__ == "__main__":
  app = MainWindow()
  app.wm_protocol("WM_DELETE_WINDOW", app.onClose)
  app.lift()
  app.mainloop()
  #am = AmtrakSearch(None)
  #fakeresults = am._test_returnSearchData()
  #for train in fakeresults:
  #  vals = train.returnSelectedElements(["#", "Train", "Departs", "Arrives", "Duration"])