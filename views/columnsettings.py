import tkinter as tk
from tkinter import ttk, messagebox

from views.config import APP_NAME, BACKGROUND, ICON, SYSTEM_FONT

class ColumnSettings(tk.Toplevel):
  """
  A class to create a column settings window, where the user can choose which columns to display on Treeviews.

  Parameters
  ----------
  tk : Toplevel
  
  Attributes
  ----------
  checkbuttonVals : list
      Populated with BooleanVar objects holding each column's selected state.
  isExport : bool
  hasAtLeastOneChecked : bool
  availableCols : dict

  Methods
  -------
  hasCheckedOne
      Spawns the window.
  """
  def __init__(self, parent, isExport=False, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.title("Column Settings")
    self.iconbitmap(ICON)
    self.checkbuttonVals = list()
    self.isExport = isExport
    self.hasAtLeastOneChecked = False
    self.configure(background=BACKGROUND)

    tk.Label(self, text="Select Display Columns", background=BACKGROUND, font=(SYSTEM_FONT, 13, 'bold')).pack(padx=8, pady=1)
    if self.isExport: msg="Choose columns included in the exported file."
    else: msg="Settings will affect the search results table and Itinerary."
    tk.Label(self, text=msg, background=BACKGROUND).pack(padx=8, pady=2)
    self.availableCols = self.parent.us.getColumns()
    self.__createCheckbuttons()
    
    ttk.Button(self, text="Save", command=self.__updateSelections).pack(padx=8, pady=4)

    self.wm_protocol("WM_DELETE_WINDOW", self.destroy)

  def hasCheckedOne(self):
    """Spawns the window and returns True if at least one item is checked."""
    self.wait_window()
    return self.hasAtLeastOneChecked

  def __createCheckbuttons(self):
    for index, col in enumerate(self.availableCols):
      self.checkbuttonVals.append(tk.BooleanVar(self, value=self.availableCols[col]["Selected"]))
      ttk.Checkbutton(self, text=self.availableCols[col]["Display Name"], variable=self.checkbuttonVals[index]).pack(anchor=tk.W, padx=4)

  def __updateSelections(self):
    newValues = dict()
    for index, col in enumerate(self.availableCols):
      newValues[col] = self.checkbuttonVals[index].get()
      if self.checkbuttonVals[index].get() == True: #Item selected
        self.hasAtLeastOneChecked = True

    if self.hasAtLeastOneChecked:
      if self.isExport:
        self.parent.us.setExportColumns(newValues)
      else:
        self.parent.us.setColumns(newValues)
        self.parent.trainResultsArea.updateDisplayColumns()
        try: self.parent.itineraryWindow.updateDisplayColumns() # If visible/open
        except: pass
      self.destroy()
    else:
      messagebox.showerror(title="Display Columns", message="At least one column must be selected.")