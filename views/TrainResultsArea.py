import tkinter as tk
from tkinter import ttk

from . import config as cfg

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
    self.results = ttk.Treeview(self.resultsArea, columns=self.columns, show='headings', cursor="hand2", selectmode='browse', height=12/cfg.WIDTH_DIV)
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
      self.parent.startThread(self.doSearchCall)
    except Exception as e:
      print(e)
      tk.messagebox.showerror(cfg.APP_NAME, message="Unable to search right now. Try again in just a few seconds.")
      self.resetWidgets()

  def doSearchCall(self):
    response = self.parent.searcher.oneWaySearch()
    if type(response) == dict:
      self.inViewSegmentResults = response
      self.populateTreeview(response)
    elif response != None:
      tk.messagebox.showerror(cfg.APP_NAME, message=response)
    self.resetWidgets()

  def populateTreeview(self, trains):
    for train in trains:
      num = train+1
      vals = trains[train].returnSelectedElements(self.columns)
      self.results.insert('', tk.END, text=train, values=vals)
      if num == 1:
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} train found")
      else:
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} trains found")
    self.resetWidgets()