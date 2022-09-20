import tkinter as tk
from tkinter import ttk, messagebox
import easygui

import os
from copy import deepcopy
from time import sleep
import webbrowser

from views.columnsettings import ColumnSettings
from views.config import ICON, WIDTH_DIV, BACKGROUND

class Itinerary(tk.Toplevel):
  """
  A class to create the Itinerary window, used to display saved segments.

  Parameters
  ----------
  tk : Toplevel
  
  Attributes
  ----------
  inViewSavedSegments : dict
  segmentsArea : tk.Frame
      Holds Treeview and scrollbars.
  buttonsArea : tk.Frame
  columns = list
      Selected column names from `Train.organizationalUnit`.
  headerCols = dict
      Selected column display names and their widths. Corresponds to `columns`.
  dispCols : list
      Currently displayed columns by name.
  userSegments : ttk.Treeview
  tvScroll : ttk.Scrollbar
      Y-axis.
  tvScrollHoriz : ttk.Scrollbar
      X-axis.
  trainInfoButton : ttk.Button
  deleteButton : ttk.Button
  moveUpButton : ttk.Button
  moveDownButton : ttk.Button
  exportButton : ttk.Button
  openResultsButton : ttk.Button
      Loads this segment's search results into the train results area.
  
  Methods
  -------
  getSelection
      Returns the current user selection (highlighted).
  doExport
      Asks for a file location and saves the itinerary.
  updateItinerary
      Refreshes the treeview object with new information.
  updateDisplayColumns
      Changes which columns are shown in the table.
  """
  def __init__(self, parent, spawnExport=False, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.geometry('800x330')
    self.title("Itinerary")
    if os.name == 'nt': self.iconbitmap(ICON)
    self.config(background=BACKGROUND)
    self.inViewSavedSegments = dict()
    self.segmentsArea = tk.Frame(self, background=BACKGROUND)
    self.buttonsArea = tk.Frame(self, background=BACKGROUND)

    self.columns = list()
    self.headerCols = dict()
    self.dispCols = list()
    self.__getDisplayColumns()
    self.userSegments = ttk.Treeview(self.segmentsArea, columns=self.columns, show='headings', cursor='hand2', selectmode='browse', height=int(12/WIDTH_DIV))
    self.__makeHeadings()
    self.tvScroll = ttk.Scrollbar(self.segmentsArea, orient='vertical', command=self.userSegments.yview)
    self.tvScrollHoriz = ttk.Scrollbar(self.segmentsArea, orient='horizontal', command=self.userSegments.xview)
    self.userSegments.configure(yscrollcommand=self.tvScroll.set, xscrollcommand=self.tvScrollHoriz.set)
    #self.__populateTreeview(self.parent.us.userSelections.getSegments())
    self.userSegments.bind("<Button-1>", lambda e: self.__buttonStateChanges(True))

    self.trainInfoButton = ttk.Button(self.buttonsArea, text="Train Info", command=self.__openTrainLink)
    self.deleteButton = ttk.Button(self.buttonsArea, text="Delete", command=self.__doDelete)
    self.moveUpButton = ttk.Button(self.buttonsArea, text="Move Up", command=self.__moveUp)
    self.moveDownButton = ttk.Button(self.buttonsArea, text="Move Down", command=self.__moveDown)
    self.exportButton = ttk.Button(self.buttonsArea, text="Export Itinerary", command=self.doExport)
    self.openResultsButton = ttk.Button(self.buttonsArea, text="Search Results", command=self.__openResults)
    self.mapButton = ttk.Button(self.buttonsArea, text="Journey Map", command=self._callJourneyMap)
    self.__exportButtonCheck()
    self.__buttonStateChanges()

    self.tvScrollHoriz.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.userSegments.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.segmentsArea.pack(fill=tk.BOTH, padx=8, pady=4, expand=True)

    self.exportButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.openResultsButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.trainInfoButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.mapButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.deleteButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.moveUpButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.moveDownButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)

    self.buttonsArea.pack(side=tk.BOTTOM, expand=False, padx=8, pady=4)
    
    self.updateItinerary()
    if spawnExport: self.doExport()
    self.wm_protocol("WM_DELETE_WINDOW", self.__onClose)

  def __onClose(self):
    self.parent.closeItinerary()
    self.destroy()
  
  def getSelection(self):
    """
    Retrieves the currently highlighted item.

    Returns
    -------
    dict
        Index of item, Train object
    """
    item = self.userSegments.focus()
    if item != "":
      myTrain = (self.inViewSavedSegments[self.userSegments.item(item, "text")]) # Train object
      return {"Index": self.userSegments.item(item, "text"), "Train": myTrain}
  
  def _callJourneyMap(self):
    self.parent.openMap()
    _allSegmentInfo = []
    _allCitySegments = []

    _saved = self.parent.us.userSelections.segments
    for segment in _saved:
      _allSegmentInfo.append(_saved[segment].segmentInfo)
      _allCitySegments.extend(_saved[segment].citySegments)
    
    self.parent.mapWindow.drawTrainRoute(_allSegmentInfo, _allCitySegments)

  def __openResults(self):
    # Finds search results index for this segment
    item = self.getSelection()
    num = self.parent.us.userSelections.getSegmentSearchNum(item["Index"])
    self.parent.resultsHeadingArea.changeSearchView(num)

  def __openTrainLink(self):
    item = self.userSegments.item(self.userSegments.focus())
    segmentInfo = self.inViewSavedSegments[item['text']].segmentInfo
    for segment in segmentInfo:
      if segmentInfo[segment]["Type"].upper() == "TRAIN":
        trainName = segmentInfo[segment]["Name"].lower()
        trainName = trainName.replace(' ', '-')
        if ' ' not in trainName:
          if trainName != "NA":
            url = f"https://www.amtrak.com/{trainName}-train"
            webbrowser.open(url, new=1, autoraise=True)

  def __move(self, item, dir, iid):
    """Moves an treeview `item` up or down."""
    self.parent.us.userSelections.swapSegment(item["Index"], dir)
    self.updateItinerary()
    #self.userSegments.focus(iid) # Can't find IID
    #self.userSegments.selection_set(iid)
  def __moveUp(self):
    item = self.getSelection()
    self.__move(item, 'up', self.userSegments.focus())
  def __moveDown(self):
    item = self.getSelection()
    self.__move(item, 'down', self.userSegments.focus())

  def __doDelete(self):
    item = self.getSelection()
    answer = messagebox.askyesno(title="Delete Segment", message=f"Are you sure you want to delete this {item['Train'].name} trip?")
    if answer == True:
      search = self.parent.us.userSelections.deleteSegment(item["Index"])
      self.updateItinerary()
      # Refreshes treeview so we can save the segment again
      self.parent.resultsHeadingArea.changeSearchView(self.parent.resultsHeadingArea.searchNum)

  def doExport(self): # Move to main window?
    """
    Prompts the user for a directory to save to, the desired attributes, and saves the itinerary.
    """
    self.update()
    defaultPath = os.path.join(os.path.expanduser('~/'), 'My Itinerary.csv')
    exportPath = easygui.filesavebox(default=defaultPath, filetypes=['*.csv'])
    if exportPath != None:
      if not exportPath.endswith('.csv'):
        exportPath += '.csv'

      cs = ColumnSettings(self.parent, isExport=True)
      if cs.hasCheckedOne():
        didSucceed = self.parent.us.userSelections.createCsv(exportPath, self.parent.us.exportColumns)
        if didSucceed:
          messagebox.showinfo(title='File Export', message=f'Saved to {exportPath}')
        else:
          messagebox.showwarning(title='File Export', message='Could not save the file.')

  def _test_getGeometry(self):
    print("Itinerary:", self.geometry(None))

  def updateItinerary(self):
    """
    Refreshes the treeview object with new information from the Rail Pass object.
    """
    self.__clearTree()
    self.inViewSavedSegments = self.parent.us.userSelections.getSegments()
    self.__populateTreeview(self.inViewSavedSegments)
    self.__exportButtonCheck()
    self.__buttonStateChanges()
    self.update_idletasks()

  def __exportButtonCheck(self):
    """If there are no segments present, do not allow an export."""
    if self.userSegments.get_children() != ():
      self.exportButton.configure(state='normal')
      self.mapButton.configure(state='normal')
    else:
      self.exportButton.configure(state='disabled')
      self.mapButton.configure(state='disabled')

  def __buttonStateChanges(self, enabled=False):
    """Enables or disables every button besides Export."""
    def doChanges():
      selectionBasedButtons = [self.deleteButton, self.moveDownButton, self.moveUpButton, self.openResultsButton, self.trainInfoButton]

      if enabled:
        sleep(0.05)
        mySelection = self.getSelection()
        for widget in selectionBasedButtons:
          widget.configure(state='normal')
        try:
          if mySelection["Index"] == 1: self.moveUpButton.configure(state='disabled')
          # elif mySelection["Index"] == len(self.inViewSavedSegments): self.moveDownButton.configure(state='disabled')
          elif mySelection["Index"] > len(self.userSegments.get_children()): self.moveDownButton.configure(state='disabled')
          print(len(self.userSegments.get_children()), mySelection["Index"])
        except TypeError:
          self.moveUpButton.configure(state='disabled')
          self.moveDownButton.configure(state='disabled')
      else:
        for widget in selectionBasedButtons:
          widget.configure(state='disabled')
      self.update_idletasks()
    
    self.parent.startThread(doChanges)
    
  def __makeHeadings(self):
    for index, col in enumerate(self.headerCols):
      self.userSegments.heading(self.columns[index], text=col, anchor='w')
      self.userSegments.column(self.columns[index], minwidth=10, width=self.headerCols[col], stretch=True, anchor='w')
    self.userSegments["displaycolumns"] = self.dispCols
  
  def updateDisplayColumns(self):
    """
    Changes which columns are currently shown in the table.
    """
    self.__getDisplayColumns()
    self.userSegments["displaycolumns"] = self.dispCols
    if self.inViewSavedSegments != {}:
      self.__clearTree()
      self.__populateTreeview(self.inViewSavedSegments)
    self.update_idletasks()

  def __getDisplayColumns(self):
    self.dispCols.clear()
    self.columns.clear()
    self.headerCols.clear()
    
    self.dispCols.append("Leg")
    self.columns.append("Leg")
    self.headerCols = {"Leg": 40}

    columns, headerCols, dispCols = self.parent.us.getDisplayColumns()
    self.columns.extend(columns)
    self.headerCols.update(headerCols)
    self.dispCols.extend(dispCols)

    replacements = [('Arrives', 'Arrival Datetime'), ('Departs', 'Departure Datetime')]
    for r in (replacements): # Replace with full dates and times, if selected in display cols
      try:
        thisColVal = self.columns.index(r[0])
        self.columns[thisColVal] = r[1]
        thisDispVal = self.dispCols.index(r[0])
        self.dispCols[thisDispVal] = r[1]
      except ValueError:
        pass
  
  def __clearTree(self):
    for item in self.userSegments.get_children():
      self.userSegments.delete(item)

  def __populateTreeview(self, trains):
    """
    Populates the Treeview object with a list of trains.

    Parameters
    ----------
    trains : dict
        A dict containing search element (key) and Train object.
    """
    getCols = deepcopy(self.columns)
    getCols.remove("Leg")
    for train in trains: # Every element of returned train dict
      vals = [train]
      vals.extend(trains[train].returnSelectedElements(getCols)) # Need different date vals
      self.userSegments.insert('', tk.END, text=train, values=vals)