import tkinter as tk
from tkinter import StringVar, ttk, font, messagebox
from tkcalendar import Calendar as Cal

import os
import random
import sys
import time
import traceback
from threading import Thread, Event, Lock
import datetime
import webbrowser

from HelperClasses import Train, RailPass, Driver, UserSelections, Stations
from DriverHelper import ImageSearch
from AmtrakSearcher import AmtrakSearch

APP_NAME = "Amtrak Rail Planner"
SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
IMAGE_DIMENSIONS = [300,225]
if os.name == 'nt':
  SYSTEM_FONT = "Segoe UI"
  GEOMETRY = "650x870+50+50"
  MINSIZE = [635, 730]
  BACKGROUND = "SystemButtonFace"
  WIDTH_DIV = 1
elif os.name == 'posix':
  SYSTEM_FONT = "TkDefaultFont"
  GEOMETRY = "700x680+0+0"
  MINSIZE = [700, 680]
  BACKGROUND = "gray93"
  WIDTH_DIV = 1.5

class TitleArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    tk.Label(self, text=APP_NAME, font=(SYSTEM_FONT, 24, 'bold'), background=BACKGROUND).pack()
    tk.Label(self, text="Make the most of your Rail Pass!", font=(SYSTEM_FONT, 12, 'italic'), background=BACKGROUND).pack()#, font=(SYSTEM_FONT, 12, 'italic')).pack()

class ImageArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.imageCatcher = ImageSearch()

    self.leftImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(1), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.leftImage.grid(row=0, column=0, padx=4, pady=4)
    #self.leftImage.bind("<Configure>", self.resizeImageCallback)

    self.rightImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(2), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.rightImage.grid(row=0, column=1, padx=4, pady=4)

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
    self.boxWidth = int(30/WIDTH_DIV)
    #self.config(background=BACKGROUND)

    #self.originVar = tk.StringVar(self)
    #self.destinationVar = tk.StringVar(self)
    #self.labelFrame = tk.Frame(self)
    #self.listboxFrame = tk.Frame(self)
    
    tk.Label(self, text="Origin").grid(row=0, column=0, pady=1)
    tk.Label(self, text="Destination").grid(row=0, column=2, pady=1)

    self.origin = self.createCombobox(1)
    self.origin.grid(row=1, column=0, padx=4)
    self.destination = self.createCombobox(2)
    self.destination.grid(row=1, column=2, padx=4)

    self.swapButton = ttk.Button(self, text="<- Swap ->", command=self.swapStations)
    self.swapButton.grid(row=1, column=1, padx=12)

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

  def ignoreHorizontalScroll(self, event=None, *args):
    pass
    #self.origin.xview_scroll(0*(event.delta/120), "units")
    #self.destination.xview_scroll(0*(event.delta/120), "units")

  def createCombobox(self, side):
    temp = ttk.Combobox(self, values=self.stations.returnStationKeys(), width=self.boxWidth, height=16, xscrollcommand=self.ignoreHorizontalScroll)
    temp.current(random.randint(0, self.lengthOfList-1))
    temp.bind("<<ComboboxSelected>>", lambda e, widget=temp, side=side, isSwap=False: self.selectionChangedCallback(widget, side, isSwap, e))
    temp.bind("<Shift-MouseWheel>", self.ignoreHorizontalScroll)
    #temp.configure(xscrollcommand=self.ignoreHorizontalScroll)
    self.parent.us.set(temp.get(), side)
    return temp

  def selectionChangedCallback(self, widget, side, isSwap=False, e=None):
    self.parent.us.set((widget.get()), side)
    lock = self.parent.imageDriverLock
    city = self.stations.returnCityState(widget.get())
    self.parent.startThread(self.parent.doRefresh, [city, side, isSwap, lock])

class DateSelectionArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.isCalendarShown = False
    self.incrementWidth = int(3/WIDTH_DIV)
    self.dateDisplay = tk.StringVar(self, self.parent.us.getPrettyDate())
    self.incrementButton = ttk.Style()
    self.incrementButton.configure('inc.TButton', font=(SYSTEM_FONT, 10))
    self.incrementArea = tk.Frame(self)
    ttk.Button(self, text="Select Departure Date", command=self.showCalendar).grid(row=0, column=0)
    self.currentDate = tk.Label(self, textvariable=self.dateDisplay, width=25, relief=tk.SUNKEN, cursor="hand2")
    self.currentDate.grid(row=0, column=1, padx=8)
    ttk.Button(self.incrementArea, text="-", command=lambda d=-1:self.changeDate(d), width=self.incrementWidth, style="inc.TButton").grid(row=0, column=0)
    ttk.Button(self.incrementArea, text="+", command=lambda d=1:self.changeDate(d), width=self.incrementWidth, style="inc.TButton").grid(row=0, column=1)
    self.incrementArea.grid(row=0, column=2)
    self.calendar = self.createCalendarArea()

    self.currentDate.bind("<Button-1>", lambda e: self.showCalendar())

  def changeDate(self, d):
    if type(d) == int:
      self.parent.us.incrementDate(d)
    elif type(d) == datetime.date:
      self.parent.us.setDate(d)
    self.dateDisplay.set(self.parent.us.getPrettyDate())
    self.update_idletasks()
  
  def callbackCalendar(self, e=None):
    self.changeDate(self.calendar.selection_get())
    self.removeCal()
  
  def removeCal(self):
    time.sleep(0.15)
    self.calendar.grid_remove()
    self.isCalendarShown = False
    self.update_idletasks()

  def showCalendar(self):
    if self.isCalendarShown == False:
      self.calendar.grid(row=1, column=0, columnspan=4, pady=8)
      self.isCalendarShown = True
    else:
      self.removeCal()
    self.update_idletasks()

  def createCalendarArea(self):
    rightNow = self.parent.us.getDate()
    cal = Cal(self, selectmode='day', year=rightNow.year, month=rightNow.month, day=rightNow.day, firstweekday="sunday", mindate=rightNow, date_pattern="m/d/y")
    cal.bind("<<CalendarSelected>>", self.callbackCalendar)
    return cal

  def createCalendarPopupWindow(self):
    def getCalDate():
      date = cal.selection_get()
      #date = datetime.datetime.strptime(date, "%m/%d/%Y")
      #date = datetime.date(year=date.year, month=date.month, day=date.day)
      self.changeDate(cal.selection_get())
    calWindow = tk.Toplevel(self.parent)
    rightNow = self.parent.us.getDate()
    cal = Cal(calWindow, selectmode='day', year=rightNow.year, month=rightNow.month, day=rightNow.day)
    cal.pack()
    tk.Button(cal, text="Select", command=getCalDate).pack()
    calWindow.wm_protocol("WM_DELETE_WINDOW", calWindow.destroy)
    calWindow.mainloop()


class ResultsHeadingArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent

    self.titleToAndFrom = tk.StringVar(self)
    self.searchDate = tk.StringVar(self)
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.boldItalic = font.Font(family=SYSTEM_FONT, size=14, weight=font.BOLD, slant=font.ITALIC)
    self.numberOfTrains = tk.StringVar(self)

    self.titleLabel = tk.Label(self, textvariable=self.titleToAndFrom, font=self.boldItalic, background=self.background)
    self.titleLabel.pack()#grid(row=0, column=0, pady=4)
    self.dateLabel = tk.Label(self, textvariable=self.searchDate, font=(SYSTEM_FONT, 11, font.NORMAL), background=self.background)
    self.dateLabel.pack()
    self.numberLabel = tk.Label(self, textvariable=self.numberOfTrains, background=self.background)
    self.numberLabel.pack()#grid(row=1, column=0)

class TrainResultsArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.resultsArea = tk.Frame(self)

    self.inViewSegmentResults = dict()#self.parent.searcher._test_returnSearchData() # AmtrakSearch thisSearchResultsAsTrain

    self.columns = ["Number", "Name", "Departs", "Arrives", "Duration", "Number of Segments"]
    self.headerCols = {"#":30, "Train":175, "Departs":130, "Arrives":130, "Duration":65, "Segments":65}
    #self.numberOfTrains = tk.StringVar(self, value="0 trains found") # Pass this in to searcher?
    self.results = ttk.Treeview(self.resultsArea, columns=self.columns, show='headings', cursor="hand2", selectmode='browse', height=12/WIDTH_DIV)
    self.makeHeadings()
    self.tvScroll = ttk.Scrollbar(self.resultsArea, orient='vertical', command=self.results.yview)
    self.results.configure(yscrollcommand=self.tvScroll.set)

    self.findTrainsBtn = ttk.Button(self, text="Find Trains", command=self.startSearch)
    self.findTrainsBtn.pack()
    self.progressBar = ttk.Progressbar(self, orient='horizontal', length=200, maximum=100, mode='determinate')
    self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.resultsArea.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)


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

  def resetWidgets(self):
    self.progressBar.pack_forget()
    self.findTrainsBtn.config(state='normal')
    self.parent.statusMessage.set("Ready")
    self.parent.update_idletasks()

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
    self.resultsArea.pack_forget()
    self.progressBar.pack()
    self.progressBar['value'] = 0
    self.resultsArea.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
    self.clearTree()
    self.parent.resultsHeadingArea.numberOfTrains.set("0 trains found")

    origin = self.parent.us.getOrigin()
    dest = self.parent.us.getDestination()
    date = self.parent.us.getSearchDate()
    prettyDate = self.parent.us.getPrettyDate()

    self.parent.resultsHeadingArea.titleToAndFrom.set(f"{self.parent.stationsArea.stations.returnStationNameAndState(origin)} to {self.parent.stationsArea.stations.returnStationNameAndState(dest)}")
    self.parent.resultsHeadingArea.searchDate.set(prettyDate)
    self.update_idletasks()
    try:
      self.parent.searcher.preSearchSetup(self.parent.stationsArea.stations.getStationCode(origin), self.parent.stationsArea.stations.getStationCode(dest), date, self.progressBar)
    
    #fakeResults = self.parent.searcher._test_returnSearchData()
    #time.sleep(1)
      self.parent.startThread(self.doSearchCall)
    except Exception as e:
      print(traceback.format_exc())
      print(e)
      tk.messagebox.showerror(APP_NAME, message="Unable to search right now. Try again in just a few seconds.")
      self.resetWidgets()

  def doSearchCall(self):
    response = self.parent.searcher.oneWaySearch()
    if type(response) == dict:
      self.inViewSegmentResults = response
      self.populateTreeview(response)
    elif response != None:
      tk.messagebox.showerror(APP_NAME, message=response)
    self.resetWidgets()

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
    self.resetWidgets()

class MenuOptions(tk.Menu):
  def __init__(self, parent, *args, **kwargs):
    tk.Menu.__init__(self, parent)
    self.parent = parent
    self.helpmenu = tk.Menu(self, tearoff=0)
    self.helpmenu.add_command(label="Open Route Map", command=lambda: self.openLink("https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/Maps/Amtrak-System-Map-1018.pdf"))
    self.helpmenu.add_command(label="About", command=lambda: self.openBox("Amtrak Rail Pass Assistant\nv0.1.0"))
    self.add_cascade(label="Help", menu=self.helpmenu)

  def openLink(self, l):
    webbrowser.open(l, new=1, autoraise=True)
  
  def openBox(self, m):
    tk.messagebox.showinfo(APP_NAME, message=m)

class DevTools(tk.Toplevel):
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.title("Dev Tools")
    tk.Label(self, text="Development Tools", font=('', 16, font.NORMAL)).pack()
    tk.Button(self, text="Print Geometry", command=self.parent._test_getGeometry).pack()
    tk.Button(self, text="Print Column Info", command=self.parent.trainResultsArea._test_getColInfo).pack()
    tk.Button(self, text="Print Selection", command=self.parent.trainResultsArea.getSelection).pack()
    tk.Button(self, text="Print Widget Background", command=self.parent._test_getBackground).pack()

class MainWindow(tk.Tk):
  def __init__(self):
    super().__init__()
    self.geometry(GEOMETRY)
    self.minsize(width=MINSIZE[0], height=MINSIZE[1])
    self.config(background=BACKGROUND)
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
      f.config(background=BACKGROUND)
    for child in f.winfo_children():
      if child.winfo_children():
        self.setBackground(child)
      else:
        try:
          #print(f"Before check: ///{f, child}///\n")
          if type(child) not in DONOTCHANGETHESE:
            #print(f"Child {child} made it through.\n\n")
            child.config(background=BACKGROUND)
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
  app.lift()
  app.mainloop()
  #am = AmtrakSearch(None)
  #fakeresults = am._test_returnSearchData()
  #for train in fakeresults:
  #  vals = train.returnSelectedElements(["#", "Train", "Departs", "Arrives", "Duration"])