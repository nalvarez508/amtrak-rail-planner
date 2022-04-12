import tkinter as tk
from tkinter import ttk, messagebox
import easygui

import os

from views.columnsettings import ColumnSettings
from views.config import WIDTH_DIV, BACKGROUND

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
  columns = list
      Selected column names from `Train.organizationalUnit`.
  headerCols = dict
      Selected column display names and their widths. Corresponds to `columns`.
  dispCols : list
      Currently displayed columns.
  userSegments : ttk.Treeview
  tvScroll : ttk.Scrollbar
      Y-axis.
  tvScrollHoriz : ttk.Scrollbar
      X-axis.
  deleteButton : ttk.Button
  moveUpButton : ttk.Button
  moveDownButton : ttk.Button
  exportButton : ttk.Button
  openResultsButton : ttk.Button
      Loads this segment's search results into the train results area.
  
  Methods
  -------
  updateItinerary
      Refreshes the treeview object with new information.
  updateDisplayColumns
      Changes which columns are shown in the table.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.geometry('700x330')
    self.title("Itinerary")
    self.inViewSavedSegments = dict()
    self.segmentsArea = tk.Frame(self)
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

    self.deleteButton = ttk.Button(self.buttonsArea, text="Delete", command=self.__doDelete)
    self.moveUpButton = ttk.Button(self.buttonsArea, text="Move Up")
    self.moveDownButton = ttk.Button(self.buttonsArea, text="Move Down")
    self.exportButton = ttk.Button(self.buttonsArea, text="Export Itinerary", command=self.doExport)
    self.openResultsButton = ttk.Button(self.buttonsArea, text="Search Results")
    self.__exportButtonCheck()
    self.__buttonStateChanges()

    self.tvScrollHoriz.pack(side=tk.BOTTOM, fill=tk.BOTH)
    self.userSegments.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.segmentsArea.pack(fill=tk.BOTH, padx=8, pady=4, expand=True)

    self.exportButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.openResultsButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.deleteButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.moveUpButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)
    self.moveDownButton.pack(side=tk.LEFT, fill=tk.X, anchor=tk.CENTER, padx=4)

    self.buttonsArea.pack(side=tk.BOTTOM, expand=False, padx=8, pady=4)
    
    self.updateItinerary()
    self.wm_protocol("WM_DELETE_WINDOW", self.__onClose)

  def __onClose(self):
    self.parent.closeItinerary()
    self.destroy()
  
  def getSelection(self):
    item = self.userSegments.focus()
    if item != "":
      myTrain = (self.inViewSavedSegments[self.userSegments.item(item, "text")]) # Train object
      return {"Index": self.userSegments.item(item, "text"), "Train": myTrain}
  
  def __doDelete(self):
    item = self.getSelection()
    answer = messagebox.askyesno(title="Delete Segment", message=f"Are you sure you want to delete this {item['Train'].name} trip?")
    if answer == True:
      self.parent.us.userSelections.deleteSegment(item["Index"])
      self.updateItinerary()

  def doExport(self): # Move to main window?
    defaultPath = os.path.join(os.path.expanduser('~/'), 'My Itinerary.csv')
    exportPath = easygui.filesavebox(default=defaultPath, filetypes=['*.csv'])
    if exportPath != None:
      if not exportPath.endswith('.csv'):
        exportPath += '.csv'
      #ColumnSettings(self.parent)
      #self.parent.update()
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
    if self.userSegments.get_children() != (): self.exportButton.configure(state='normal')
    else: self.exportButton.configure(state='disabled')

  def __buttonStateChanges(self, enabled=False):
    """Enables or disables every button besides Export."""
    selectionBasedButtons = [self.deleteButton, self.moveDownButton, self.moveUpButton, self.openResultsButton]
    if enabled:
      for widget in selectionBasedButtons:
        widget.configure(state='normal')
    else:
      for widget in selectionBasedButtons:
        widget.configure(state='disabled')

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
    self.columns, self.headerCols, self.dispCols = self.parent.us.getDisplayColumns()
  
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
    for train in trains: # Every element of returned train dict
      vals = trains[train].returnSelectedElements(self.columns)
      self.userSegments.insert('', tk.END, text=train, values=vals)