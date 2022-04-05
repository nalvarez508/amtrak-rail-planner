import tkinter as tk
from tkinter import ttk

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
  availableCols : dict
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.checkbuttonVals = list()

    tk.Label(self, text="Select Display Columns").pack()
    self.availableCols = self.parent.us.getColumns()
    self.__createCheckbuttons()
    
    ttk.Button(self, text="Save", command=self.__updateSelections).pack()

    self.wm_protocol("WM_DELETE_WINDOW", self.destroy)

  def __createCheckbuttons(self):
    for index, col in enumerate(self.availableCols):
      self.checkbuttonVals.append(tk.BooleanVar(self, value=self.availableCols[col]["Selected"]))
      ttk.Checkbutton(self, text=self.availableCols[col]["Display Name"], variable=self.checkbuttonVals[index]).pack(anchor=tk.W)

  def __updateSelections(self):
    newValues = dict()
    for index, col in enumerate(self.availableCols):
      newValues[col] = self.checkbuttonVals[index].get()
    self.parent.us.setColumns(newValues)
    self.parent.trainResultsArea.updateDisplayColumns()
    try: self.parent.itineraryWindow.updateDisplayColumns()
    except: pass
    self.destroy()