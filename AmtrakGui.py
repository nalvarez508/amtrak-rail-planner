import tkinter as tk
from tkinter import ttk

import sys
from threading import Thread, Event, Lock

from HelperClasses import Driver, UserSelections
from AmtrakSearcher import AmtrakSearch
from views import config as cfg
from views.TitleArea import TitleArea
from views.ImageArea import ImageArea
from views.StationsArea import StationsArea
from views.DateSelectionArea import DateSelectionArea
from views.ResultsHeadingArea import ResultsHeadingArea
from views.TrainResultsArea import TrainResultsArea
from views.MenuOptions import MenuOptions
from views.DevTools import DevTools

class MainWindow(tk.Tk):
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
    self.startThread(self.startup)
    self.imageDriverLock = Lock()
    self.resultsBackground = "gainsboro"

    self.titleArea = TitleArea(self)
    self.imageArea = ImageArea(self)
    self.stationsArea = StationsArea(self)
    self.dateSelectionArea = DateSelectionArea(self)
    self.setBackground()
    self.resultsHeadingArea = ResultsHeadingArea(self)
    self.trainResultsArea = TrainResultsArea(self)
    self.devTools = DevTools(self)
    self.config(menu=MenuOptions(self))

    self.titleArea.pack()
    self.imageArea.pack()
    self.stationsArea.pack()
    self.dateSelectionArea.pack(pady=4)
    self.resultsHeadingArea.pack(fill=tk.X)
    self.trainResultsArea.pack(fill=tk.BOTH, expand=True)

    self.statusBar = tk.Label(self, textvariable=self.statusMessage, bd=1, relief=tk.SUNKEN, anchor=tk.W)
    self.statusBar.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.statusBar.lift

    self.update()

  def setBackground(self, f=None):
    DONOTCHANGETHESE = [ttk.Button, ttk.Combobox, ttk.Treeview, ttk.Progressbar, ttk.Label, ttk.Frame, ttk.Scrollbar]
    if f == None:
      f = self
    if type(f) not in DONOTCHANGETHESE:
      f.config(background=cfg.BACKGROUND)
    for child in f.winfo_children():
      if child.winfo_children():
        self.setBackground(child)
      else:
        try:
          #print(f"Before check: ///{f, child}///\n")
          if type(child) not in DONOTCHANGETHESE:
            #print(f"Child {child} made it through.\n\n")
            child.config(background=cfg.BACKGROUND)
        except tk.TclError as e:
          print(e)
          pass

  def _test_getGeometry(self):
    print(self.geometry(None))
  def _test_getBackground(self):
    s1 = ttk.Style()
    bg = s1.lookup("TButton", "background")
    print(bg)

  def startThread(self, function, args=None):
    if args:
      Thread(target=function, args=args).start()
    else:
      Thread(target=function).start()

  def onClose(self):
    self.devTools.destroy()
    self.destroy()
    self.imageArea.imageCatcher.driver.close()
    self.searcher.driver.close()
    self.imageArea.imageCatcher.driver.quit()
    self.searcher.driver.quit()
    sys.exit()

  def startup(self):
    self.searcher = AmtrakSearch(self, Driver(cfg.SEARCH_URL).driver, status=self.statusMessage)

  def doRefresh(self, city, side, isSwap=False, lock=None):
    if isSwap == False:
      if city != self.imageArea.imageCatcher.getCityName(side):
        self.imageArea.imageCatcher.setCityPhoto(side, None)
        self.imageArea.updateImage(side)
        try:
          with lock:
            self.imageArea.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS)
        except AttributeError:
          self.imageArea.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS)
        self.imageArea.updateImage(side)
    elif isSwap == True:
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