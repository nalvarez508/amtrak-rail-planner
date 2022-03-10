import tkinter as tk
from tkinter import ttk, font, messagebox
from tkcalendar import Calendar

import os
import random
import sys
import time
import traceback
from threading import Thread, Event, Lock

from HelperClasses import Train, RailPass, Driver, UserSelections, Stations
from DriverHelper import ImageSearch
from AmtrakSearcher import AmtrakSearch

APP_NAME = "Amtrak Rail Planner"
SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
IMAGE_DIMENSIONS = [245,183]
if os.name == 'nt':
  SYSTEM_FONT = "Segoe UI"
elif os.name == 'posix':
  SYSTEM_FONT = "TkDefaultFont"

class TitleArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    tk.Label(self, text=APP_NAME, font=(SYSTEM_FONT, 24, 'bold')).pack()
    tk.Label(self, text="Make the most of your Rail Pass!", font=(SYSTEM_FONT, 12, 'italic')).pack()#, font=(SYSTEM_FONT, 12, 'italic')).pack()

class ImageArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.imageCatcher = ImageSearch()
    #self.imageCatcher.loadImage(self.parent.us.getOrigin(), 1)
    #self.imageCatcher.loadImage(self.parent.us.getDestination(), 2)

    self.leftImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(1), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.leftImage.grid(row=0, column=0, padx=4, pady=16)
    #self.leftImage.bind("<Configure>", self.resizeImageCallback)

    self.rightImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(2), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.rightImage.grid(row=0, column=1, padx=4, pady=16)

    #self.leftInfo = tk.Label(self, text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")
    #self.leftInfo.grid(row=1, column=0)
    #self.rightInfo = tk.Label(self, text=f"{self.rightImage.winfo_width()}x{self.rightImage.winfo_height()}")
    #self.rightInfo.grid(row=1, column=2)
    #tk.Button(self, text="Update", command=self._test_widgetDims).grid(row=1, column=1)

  def _test_widgetDims(self):
    self.leftInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")
    self.rightInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")

  def updateImage(self, side):
    if side == 1:
      self.leftImage.configure(image=self.imageCatcher.getCityPhoto(side))
    elif side == 2:
      self.rightImage.configure(image=self.imageCatcher.getCityPhoto(side))

class StationsArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.stations = Stations()
    self.lengthOfList = len(self.stations.returnStationKeys())
    self.boxWidth = 30

    self.origin = self.createCombobox(1)
    self.origin.grid(row=0, column=0, padx=4)
    self.destination = self.createCombobox(2)
    self.destination.grid(row=0, column=2, padx=4)

    self.swapButton = ttk.Button(self, text="<- Swap ->", command=self.swapStations)
    self.swapButton.grid(row=0, column=1, padx=12)

    self.parent.doRefresh(self.stations.returnCityState(self.origin.get()), 1)
    #self.parent.doRefresh(self.stations.returnCityState(self.destination.get()), 2)
    #self.parent.startThread(self.parent.doRefresh, [self.stations.returnCityState(self.origin.get()), 1])
    self.parent.startThread(self.parent.doRefresh, [self.stations.returnCityState(self.destination.get()), 2])

  def swapStations(self):
    newOriginCity = self.destination.current()
    newDestinationCity = self.origin.current()
    self.origin.current(newOriginCity)
    self.destination.current(newDestinationCity)
    self.parent.imageArea.imageCatcher.doCitySwap()
    self.selectionChangedCallback(self.origin, 1, True)
    self.selectionChangedCallback(self.destination, 2, True)

  def ignoreHorizontalScroll(self, e=None, *args):
    pass

  def createCombobox(self, side):
    temp = ttk.Combobox(self, values=self.stations.returnStationKeys(), width=self.boxWidth, xscrollcommand=self.ignoreHorizontalScroll)
    temp.current(random.randint(0, self.lengthOfList-1))
    temp.bind("<<ComboboxSelected>>", lambda e, widget=temp, side=side, isSwap=False: self.selectionChangedCallback(widget, side, isSwap, e))
    temp.bind("<Shift-MouseWheel>", self.ignoreHorizontalScroll)
    self.parent.us.set(temp.get(), side)
    return temp

  def selectionChangedCallback(self, widget, side, isSwap=False, e=None):
    self.parent.us.set((widget.get()), side)
    lock = self.parent.imageDriverLock
    city = self.stations.returnCityState(widget.get())
    self.parent.startThread(self.parent.doRefresh, [city, side, isSwap, lock])

#class DateSelectionArea(tk.Frame):

class ResultsHeadingArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent

    self.titleToAndFrom = tk.StringVar(self)
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.boldItalic = font.Font(family=SYSTEM_FONT, size=14, weight=font.BOLD, slant=font.ITALIC)
    self.numberOfTrains = tk.StringVar(self, value="0 trains found")

    self.titleLabel = tk.Label(self, textvariable=self.titleToAndFrom, font=self.boldItalic, background=self.background)
    self.titleLabel.pack(pady=1)#grid(row=0, column=0, pady=4)
    self.numberLabel = tk.Label(self, textvariable=self.numberOfTrains, background=self.background)
    self.numberLabel.pack()#grid(row=1, column=0)

class TrainResultsArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.background = self.parent.resultsBackground
    self.config(background=self.background)

    self.inViewSegmentResults = dict()#self.parent.searcher._test_returnSearchData() # AmtrakSearch thisSearchResultsAsTrain

    self.columns = ["Number", "Name", "Departs", "Arrives", "Duration"]
    self.headerCols = {"#":30, "Train":175, "Departs":120, "Arrives":120, "Duration":65}
    #self.numberOfTrains = tk.StringVar(self, value="0 trains found") # Pass this in to searcher?
    self.results = ttk.Treeview(self, columns=self.columns, show='headings', cursor="hand1", selectmode='browse')
    self.makeHeadings()

    self.findTrainsBtn = ttk.Button(self, text="Find Trains", command=self.startSearch)
    self.findTrainsBtn.pack()
    self.results.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
  
  def getSelection(self):
    #self.results.selection()
    item = self.results.focus()
    if item != "":
      print(self.results.item(item, "text"))
      myTrain = (self.inViewSegmentResults[self.results.item(item, "text")])
      print(myTrain)
      #item['values']['train_item'].number #https://stackoverflow.com/questions/44123356/storing-class-instances-in-a-python-tkinter-treeview

  def _test_getColInfo(self):
    for col in self.columns:
      print(self.results.column(col))

  def clearTree(self):
    for item in self.results.get_children():
      self.results.delete(item)

  def makeHeadings(self):
    dispCols = list()
    for index, col in enumerate(self.headerCols):
      self.results.heading(self.columns[index], text=col, anchor='w')
      self.results.column(self.columns[index], minwidth=10, width=self.headerCols[col], stretch=True, anchor='w')
      dispCols.append(self.columns[index])
    self.results["displaycolumns"] = dispCols
    
  def startSearch(self):
    self.findTrainsBtn.config(state='disabled')
    self.parent.statusMessage.set("Searching")
    self.clearTree()
    self.parent.resultsHeadingArea.numberOfTrains.set("0 trains found")

    origin = self.parent.us.getOrigin()
    dest = self.parent.us.getDestination()
    date = "03/28/2022"

    self.parent.resultsHeadingArea.titleToAndFrom.set(f"{self.parent.stationsArea.stations.returnStationNameAndState(origin)} to {self.parent.stationsArea.stations.returnStationNameAndState(dest)}")
    self.update_idletasks()
    try:
      self.parent.searcher.preSearchSetup(self.parent.stationsArea.stations.getStationCode(origin), self.parent.stationsArea.stations.getStationCode(dest), date)
    
    #fakeResults = self.parent.searcher._test_returnSearchData()
    #time.sleep(1)
      self.parent.startThread(self.doSearchCall)
    except Exception as e:
      print(traceback.format_exc())
      print(e)
      tk.messagebox.showerror(APP_NAME, message="Unable to search right now. Try again in just a few seconds.")
      self.findTrainsBtn.config(state='normal')
      self.parent.statusMessage.set("Ready")
    # self.parent.update_idletasks()

  def doSearchCall(self):
    response = self.parent.searcher.oneWaySearch()
    if type(response) == dict:
      self.inViewSegmentResults = response
      self.populateTreeview(response)
    else:
      tk.messagebox.showerror(APP_NAME, message=response)
    self.findTrainsBtn.config(state='normal')
    self.parent.statusMessage.set("Ready")
    self.parent.update_idletasks()

  def populateTreeview(self, trains):
    for train in trains:
      num = train+1
      vals = trains[train].returnSelectedElements(self.columns)
      #vals.append(train)
      self.results.insert('', tk.END, text=train, values=vals)
      if num == 1:
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} train found")
      else:
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} trains found")
    self.findTrainsBtn.config(state='normal')
    self.parent.statusMessage.set("Ready")
    self.parent.update_idletasks()

class DevTools(tk.Toplevel):
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.title("Dev Tools")
    tk.Label(self, text="Development Tools", font=('', 16, font.NORMAL)).pack()
    tk.Button(self, text="Print Geometry", command=self.parent._test_getGeometry).pack()
    tk.Button(self, text="Print Column Info", command=self.parent.trainResultsArea._test_getColInfo).pack()
    tk.Button(self, text="Print Selection", command=self.parent.trainResultsArea.getSelection).pack()

class MainWindow(tk.Tk):
  def __init__(self):
    super().__init__()
    self.geometry("580x700")
    self.minsize(580,700)
    
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
    self.resultsHeadingArea = ResultsHeadingArea(self)
    self.trainResultsArea = TrainResultsArea(self)
    self.devTools = DevTools(self)

    self.titleArea.pack()
    self.imageArea.pack()
    self.stationsArea.pack(pady=16)
    self.resultsHeadingArea.pack(fill=tk.X)
    self.trainResultsArea.pack(fill=tk.BOTH, expand=True)

    tk.Label(self, textvariable=self.statusMessage, bd=1, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.BOTH)

    self.update()

  def _test_getGeometry(self):
    print(self.geometry(None))

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
    self.searcher = AmtrakSearch(self, Driver(SEARCH_URL).driver, status=self.statusMessage)

  def doRefresh(self, city, side, isSwap=False, lock=None):
    if isSwap == False:
      if city != self.imageArea.imageCatcher.getCityName(side):
        self.imageArea.imageCatcher.setCityPhoto(side, None)
        self.imageArea.updateImage(side)
        try:
          with lock:
            self.imageArea.imageCatcher.loadImage(city, side, IMAGE_DIMENSIONS)
        except AttributeError:
          self.imageArea.imageCatcher.loadImage(city, side, IMAGE_DIMENSIONS)
        self.imageArea.updateImage(side)
    elif isSwap == True:
      self.imageArea.updateImage(side)
    self.update_idletasks()

if __name__ == "__main__":
  app = MainWindow()
  app.wm_protocol("WM_DELETE_WINDOW", app.onClose)
  app.mainloop()
  #am = AmtrakSearch(None)
  #fakeresults = am._test_returnSearchData()
  #for train in fakeresults:
  #  vals = train.returnSelectedElements(["#", "Train", "Departs", "Arrives", "Duration"])