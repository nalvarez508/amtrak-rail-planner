import tkinter as tk
from tkinter import ttk, messagebox

from copy import deepcopy
from datetime import datetime
from math import trunc
import webbrowser

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
  resultsArea : tk.Frame
      Holds `results` and `tvScroll`.
  buttonsArea : tk.Frame
  trainMenu : tk.Menu
  isSegmentSaved : bool
  savedSegmentIndices : list
  inViewSegmentResults : dict
      Currently displayed results.
  columns : list
      Selected column names from `Train.organizationalUnit`.
  headerCols : dict
      Selected column display names and their widths. Corresponds to `columns`.
  dispCols : list
      Columns to be shown in the table.
  results : ttk.Treeview
  tvScroll : ttk.Scrollbar
      Controls `results` yview.
  tvScrollHoriz : ttk.Scrollbar
      Controls `results` xview.
  saveButton : ttk.Button
  findTrainsBtn : ttk.Button
  progressBar : ttk.Progressbar

  Methods
  -------
  toggleSaveButton(enabled=False)
      Enables/disables the Save Segment button.
  updateDisplayColumns
      Refreshes the table's display columns.
  getSelection
      Retrieves currently selected item.
  startSearch
      Prepares UI elements for a search and starts a searching thread.
  refreshHandler(response, saved)
      Loads the table with existing search results.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.resultsArea = tk.Frame(self)
    self.buttonsArea = tk.Frame(self, background=self.background)
    self.trainMenu = tk.Menu(self, tearoff=0)
    self.trainMenu.add_command(label="Save Segment", command=self.__saveSelection)
    self.trainMenu.add_command(label="Train Info", command=self.__openTrainLink)
    self.isSegmentSaved = False
    self.savedSegmentsIndices = list()
    self.inViewSegmentResults = dict()#self.parent.searcher._test_returnSearchData() # AmtrakSearch thisSearchResultsAsTrain

    self.columns = list()
    self.headerCols = dict()
    self.dispCols = list()
    self.__getDisplayColumns()
    #self.numberOfTrains = tk.StringVar(self, value="0 trains found") # Pass this in to searcher?
    self.results = ttk.Treeview(self.resultsArea, columns=self.columns, show='headings', cursor="hand2", selectmode='browse', height=12/cfg.WIDTH_DIV)
    self.__makeHeadings()
    self.tvScroll = ttk.Scrollbar(self.resultsArea, orient='vertical', command=self.results.yview)
    self.tvScrollHoriz = ttk.Scrollbar(self.resultsArea, orient='horizontal', command=self.results.xview)
    self.results.configure(yscrollcommand=self.tvScroll.set, xscrollcommand=self.tvScrollHoriz.set)
    self.results.bind("<Button-1>", lambda e: self.toggleSaveButton(True))
    self.results.bind("<Double-Button-1>", lambda e: self.__saveSelection)
    self.results.bind("<Return>", lambda e: self.__saveSelection)
    self.results.bind("<Button-3>", self.__trainContextMenu)

    self.saveButton = ttk.Button(self.buttonsArea, text="Save Segment", state='disabled', command=self.__saveSelection)
    self.saveButton.pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)
    self.findTrainsBtn = ttk.Button(self.buttonsArea, text="Find Trains", command=self.startSearch)
    self.findTrainsBtn.pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)
    ttk.Button(self.buttonsArea, text="View Itinerary", command=self.parent.openItinerary).pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)
    
    self.progressBar = ttk.Progressbar(self, orient='horizontal', length=200, maximum=100, mode='determinate')
    self.tvScrollHoriz.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.buttonsArea.pack(side=tk.TOP, padx=8, expand=False)
    self.resultsArea.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=8, pady=4, expand=True)

  def toggleSaveButton(self, enabled=False):
    """
    Enables or disables the "Save Segment" button.

    Parameters
    ----------
    enabled : bool, optional
        Whether or not to enable the button, by default False
    """
    if enabled: self.saveButton.config(state='normal')
    else: self.saveButton.config(state='disabled')

  def updateDisplayColumns(self):
    """
    Refreshes currently displayed columns in `results`.
    """
    self.__getDisplayColumns()
    self.results["displaycolumns"] = self.dispCols
    if self.inViewSegmentResults != {}:
      self.__clearTree()
      self.__populateTreeview(self.inViewSegmentResults)
    self.update_idletasks()

  def __getDisplayColumns(self):
    self.columns, self.headerCols, self.dispCols = self.parent.us.getDisplayColumns()

  def __trainContextMenu(self, event):
    iid = self.results.identify_row(event.y)
    if iid:
      self.results.selection_set(iid)
      try:
        self.trainMenu.tk_popup(event.x_root, event.y_root)
      finally:
        self.trainMenu.grab_release()
  
  def __openTrainLink(self):
    item = self.getSelection()
    trainName = item["Train"].name
    trainName.replace(' ', '-')
    if trainName != "NA":
      url = f"https://www.amtrak.com/{trainName}-train"
      webbrowser.open(url, new=1, autoraise=True)
    else:
      messagebox.showwarning(title=cfg.APP_NAME, message="Cannot view information about multiple segments.")

  def __saveSelection(self, *args):
    """Performs some validation for segments before saving them to the Rail Pass."""
    segment = self.getSelection()
    def doSave():
      self.parent.us.userSelections.createSegment(segment["Train"], self.parent.resultsHeadingArea.getSearchNum())
      self.isSegmentSaved = True
      self.savedSegmentsIndices.append(segment["Index"])
      self.parent.us.userSelections.updateSearch(self.parent.resultsHeadingArea.getSearchNum(), deepcopy(self.savedSegmentsIndices))
      try: self.parent.itineraryWindow.updateItinerary()
      except: pass
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
    """
    Gets the currently selected item from the results table.

    Returns
    -------
    dict
        Index (int): Train (Train)
    """
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
    self.isSegmentSaved = (True if (len(self.savedSegmentsIndices) > 0) else False)
    self.parent.update_idletasks()

  def __clearTree(self):
    """Wipes out all tree elements."""
    for item in self.results.get_children():
      self.results.delete(item)
    self.inViewSegmentResults.clear()
    self.savedSegmentsIndices.clear()

  def __makeHeadings(self):
    for index, col in enumerate(self.headerCols):
      self.results.heading(self.columns[index], text=col, anchor='w')
      self.results.column(self.columns[index], minwidth=10, width=self.headerCols[col], stretch=True, anchor='w')
    self.results["displaycolumns"] = self.dispCols

  def startSearch(self):
    """
    Prepares the application to search by changing states and updating variables.

    Extended Summary
    ----------------
    Checks if the search is OK with user, depending on station and date selections.
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
      origin = self.parent.us.getOrigin() # As-is: Combobox
      dest = self.parent.us.getDestination() # As-is: Combobox
      date = self.parent.us.getSearchDate() # As-is: Calendar area
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

    # DEVELOPMENT
    fileToUse = trunc(datetime.now().timestamp()) % 3
    with open(f"_retrieved/TestTrainSearch{fileToUse}.json", "r") as f:
      temp = json.loads(f.read())
      for num in temp:
        response[int(num)] = Train(temp[num])
    
    self.__searchHandler(response)

  def refreshHandler(self, response, saved):
    """
    Refreshes the table with existing results.

    Parameters
    ----------
    response : dict
        Prev. search Train objects with indexes.
    saved : list
        Prev. search saved segments indices for validation.
    """
    self.__clearTree()
    self.inViewSegmentResults = deepcopy(response)
    self.savedSegmentsIndices = deepcopy(saved)
    self.__populateTreeview(response)
    self.__resetWidgets()
    self.update()

  def __searchHandler(self, response):
    if type(response) == dict: # Trains returned
      self.inViewSegmentResults = deepcopy(response)
      self.parent.us.userSelections.addSearch(self.parent.us.getOrigin(), self.parent.us.getDestination(), self.parent.us.getDate(), response)
      self.__populateTreeview(response)
      self.parent.resultsHeadingArea.changeSearchView(-1)
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