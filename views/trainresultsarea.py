import tkinter as tk
from tkinter import ttk, messagebox

from . import config as cfg

class TrainResultsArea(tk.Frame):
  """
  A class to hold UI elements related to the search results.

  Parameters
  ----------
  tk : Tk
      The parent frame.

  Attributes
  ----------
  background : str
  resultsArea : tk.Frame
      Holds `results` and `tvScroll`.
  inViewSegmentResults : dict
      Currently displayed results.
  columns = list
      Selected column names from `Train.organizationalUnit`.
  headerCols = dict
      Selected column display names and their widths. Corresponds to `columns`.
  results : ttk.Treeview
  tvScroll : ttk.Scrollbar
      Controls `results` yview.
  findTrainsBtn : ttk.Button
  progressBar : ttk.Progressbar

  Methods
  -------
  startSearch
      Prepares UI elements for a search and starts a searching thread.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.resultsArea = tk.Frame(self)
    self.isSegmentSaved = False
    self.savedSegmentsIndices = list()

    self.inViewSegmentResults = dict()#self.parent.searcher._test_returnSearchData() # AmtrakSearch thisSearchResultsAsTrain

    self.columns = ["Number", "Name", "Departs", "Arrives", "Duration", "Number of Segments"]
    self.headerCols = {"#":30, "Train":175, "Departs":130, "Arrives":130, "Duration":65, "Segments":65}
    #self.numberOfTrains = tk.StringVar(self, value="0 trains found") # Pass this in to searcher?
    self.results = ttk.Treeview(self.resultsArea, columns=self.columns, show='headings', cursor="hand2", selectmode='browse', height=12/cfg.WIDTH_DIV)
    self.__makeHeadings()
    self.tvScroll = ttk.Scrollbar(self.resultsArea, orient='vertical', command=self.results.yview)
    self.results.configure(yscrollcommand=self.tvScroll.set)
    self.results.bind("<Button-1>", lambda e: self.toggleSaveButton(True))
    self.results.bind("<Double-Button-1>", lambda e: self.__saveSelection)

    self.saveButton = ttk.Button(self, text="Save Segment", state='disabled', command=self.__saveSelection)

    self.findTrainsBtn = ttk.Button(self, text="Find Trains", command=self.startSearch)
    self.findTrainsBtn.pack()
    self.progressBar = ttk.Progressbar(self, orient='horizontal', length=200, maximum=100, mode='determinate')
    self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.resultsArea.pack(fill=tk.BOTH, padx=8, pady=4, expand=True)
    self.saveButton.pack()

  def toggleSaveButton(self, enabled=False):
    if enabled: self.saveButton.config(state='normal')
    else: self.saveButton.config(state='disabled')

  def __saveSelection(self, *args):
    segment = self.getSelection()
    def doSave():
      self.parent.us.userSelections.createSegment(segment["Train"], self.inViewSegmentResults)
      self.isSegmentSaved = True
      self.savedSegmentsIndices.append(segment["Index"])
    if self.isSegmentSaved == False:
      doSave()
    else:
      if segment["Index"] in self.savedSegmentsIndices:
        messagebox.showerror(title=cfg.APP_NAME, message="This segment has already been saved.")
      else:
        doOverwrite = messagebox.askyesno(title=cfg.APP_NAME, message="A segment for this search has already been saved. Do you still want to save your selected segment?")
        if doOverwrite == True:
          doSave()
        else:
          pass

  def getSelection(self, *args):
    item = self.results.focus()
    if item != "":
      myTrain = (self.inViewSegmentResults[self.results.item(item, "text")]) # Train object
      return {"Index": self.results.item(item, "text"), "Train": myTrain}

  def _test_getColInfo(self):
    for col in self.columns:
      print(self.results.column(col))

  def __resetWidgets(self):
    """Removes progress bar, updates status, and enables search button."""
    self.progressBar.pack_forget()
    self.findTrainsBtn.config(state='normal')
    self.parent.statusMessage.set("Ready")
    self.isSegmentSaved = False
    self.parent.update_idletasks()

  def __clearTree(self):
    for item in self.results.get_children():
      self.results.delete(item)

  def __makeHeadings(self):
    dispCols = list()
    for index, col in enumerate(self.headerCols):
      self.results.heading(self.columns[index], text=col, anchor='w')
      self.results.column(self.columns[index], minwidth=10, width=self.headerCols[col], stretch=True, anchor='w')
      dispCols.append(self.columns[index])
    self.results["displaycolumns"] = dispCols # Creates mapping so we can retrieve Train objects later

  def startSearch(self):
    """
    Prepares the application to search by changing states and updating variables.

    Extended Summary
    ----------------
    Disables search button, sets status, and enables/resets progress bar.
    Clears the current search results and shows that 0 trains have been found.
    Updates UserSelection variables.
    Changes search information labels.
    Begins presearch setup by passing in required variables to AmtrakSearch.
    Starts a thread to begin the search.

    Raises
    -----
    Exception
        The user is starting a search before the Driver object (from `parent.searcher`) has finished being initialized. Probably okay to use again in a few seconds, once it finishes. Forcefully resetting the driver may be a good option to include in a help menu.
    """
    if self.parent.us.isSearchOkay():
      # Resetting search elements
      self.findTrainsBtn.config(state='disabled')
      self.toggleSaveButton()
      self.parent.statusMessage.set("Searching")
      self.resultsArea.pack_forget()
      self.progressBar.pack()
      self.progressBar['value'] = 0
      self.resultsArea.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
      self.__clearTree()
      self.parent.resultsHeadingArea.numberOfTrains.set("0 trains found")

      # Updating UserSelection values
      origin = self.parent.us.getOrigin()
      dest = self.parent.us.getDestination()
      date = self.parent.us.getSearchDate()
      prettyDate = self.parent.us.getPrettyDate()

      # Updating search labels
      self.parent.resultsHeadingArea.titleToAndFrom.set(f"{self.parent.stationsArea.stations.returnStationNameAndState(origin)} to {self.parent.stationsArea.stations.returnStationNameAndState(dest)}")
      self.parent.resultsHeadingArea.searchDate.set(prettyDate)
      self.update_idletasks()
      try:
        # Starting search thread
        #self.parent.searcher.preSearchSetup(self.parent.stationsArea.stations.getStationCode(origin), self.parent.stationsArea.stations.getStationCode(dest), date, self.progressBar, self.parent.resultsHeadingArea.numberOfTrains)
        self.parent.startThread(self.__doSearchCall)
      except Exception as e:
        print(e)
        messagebox.showerror(cfg.APP_NAME, message="Unable to search right now. Try again in just a few seconds.")
        self.__resetWidgets()

  def __doSearchCall(self):
    #response = self.parent.searcher.oneWaySearch()
    response = dict()
    import json
    from traintracks.train import Train

    with open("TestTrainSearch.json", "r") as f:
      temp = json.loads(f.read())
      for num in temp:
        response[int(num)] = Train(temp[num])
    if type(response) == dict: # Trains returned
      self.inViewSegmentResults = response
      self.__populateTreeview(response)
    elif response != None: # Error returned
      messagebox.showerror(cfg.APP_NAME, message=response)
    self.__resetWidgets()

  def __populateTreeview(self, trains):
    """
    Populates the Treeview object with a list of trains.

    Parameters
    ----------
    trains : dict
        A dict containing search element (key) and Train object.
    """
    for train in trains: # Every element of returned train dict
      num = train+1 # Dict starts at zero
      vals = trains[train].returnSelectedElements(self.columns)
      self.results.insert('', tk.END, text=train, values=vals)
      if num == 1: # Display of s for plural elements
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} train found")
      else:
        self.parent.resultsHeadingArea.numberOfTrains.set(f"{num} trains found")
    self.__resetWidgets()