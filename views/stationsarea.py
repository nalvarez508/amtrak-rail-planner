import tkinter as tk
from tkinter import ttk

import random

from traintracks.stations import Stations
from . import config as cfg

class StationsArea(tk.Frame):
  """
  A class to hold UI elements related to station selection.
  
  Parameters
  ----------
  tk : Tk
      The parent frame.
      
  Attributes
  ----------
  stations : Stations
      All Amtrak stations.
  lengthOfList : int
  boxWidth : int
      Combobox width based on OS.
  origin : ttk.Combobox
  destination : ttk.Combobox
  swapButton : ttk.Button
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.stations = Stations()
    self.lengthOfList = len(self.stations.returnStationKeys())
    self.boxWidth = int(30/cfg.WIDTH_DIV)
    
    tk.Label(self, text="Origin").grid(row=0, column=0, pady=1)
    tk.Label(self, text="Destination").grid(row=0, column=2, pady=1)

    self.origin = self.__createCombobox(1)
    self.origin.grid(row=1, column=0, padx=4)
    self.destination = self.__createCombobox(2)
    self.destination.grid(row=1, column=2, padx=4)

    self.swapButton = ttk.Button(self, text="<- Swap ->", command=self.__swapStations)
    self.swapButton.grid(row=1, column=1, padx=12)

    self.parent.doRefresh(self.stations.returnCityState(self.origin.get()), 1)
    #self.parent.doRefresh(self.stations.returnCityState(self.destination.get()), 2)
    #self.parent.startThread(self.parent.doRefresh, [self.stations.returnCityState(self.origin.get()), 1])
    self.parent.startThread(self.parent.doRefresh, [self.stations.returnCityState(self.destination.get()), 2])

  def __swapStations(self):
    """Swaps the origin and destination, both Combobox objects and ImageArea labels."""
    newOriginCity = self.destination.current()
    newDestinationCity = self.origin.current()
    self.origin.current(newOriginCity)
    self.destination.current(newDestinationCity)
    self.parent.imageArea.imageCatcher.doCitySwap()
    self.__selectionChangedCallback(self.origin, 1, True)
    self.__selectionChangedCallback(self.destination, 2, True)

  def ignoreHorizontalScroll(self, event=None, *args):
    pass
    #self.origin.xview_scroll(0*(event.delta/120), "units")
    #self.destination.xview_scroll(0*(event.delta/120), "units")

  def __createCombobox(self, side):
    """
    Creates a Combobox widget with all stations and a random initial selection.

    Extended Summary
    ----------------
    With each selection from the Combobox, the UserSelection variables are updated and an image search begins.

    Parameters
    ----------
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).

    Returns
    -------
    ttk.Combobox
        The newly created Combobox.
    """
    temp = ttk.Combobox(self, values=self.stations.returnStationKeys(), width=self.boxWidth, height=16, xscrollcommand=self.ignoreHorizontalScroll)
    temp.current(random.randint(0, self.lengthOfList-1))
    temp.bind("<<ComboboxSelected>>", lambda e, widget=temp, side=side, isSwap=False: self.__selectionChangedCallback(widget, side, isSwap, e))
    temp.bind("<Shift-MouseWheel>", self.ignoreHorizontalScroll)
    #temp.configure(xscrollcommand=self.ignoreHorizontalScroll)
    self.parent.us.set(temp.get(), side)
    return temp

  def __selectionChangedCallback(self, widget, side, isSwap=False, e=None):
    """
    Event handler for item selections in the Combobox.

    Extended Summary
    ----------------
    The UserSelection variable(s) are set with the new values. A Lock is created before the image search begins, so if the user changes another image too quickly, the WebDriver will not fall apart.

    Parameters
    ----------
    widget : ttk.Combobox
        The calling Combobox.
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).
    isSwap : bool, optional
        True if values are being swapped but not changed, by default False
    e : tk.Event, optional
        Not used, by default None
    """
    self.parent.us.set((widget.get()), side)
    lock = self.parent.imageDriverLock
    city = self.stations.returnCityState(widget.get())
    self.parent.startThread(self.parent.doRefresh, [city, side, isSwap, lock])