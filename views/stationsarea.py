import tkinter as tk
from tkinter import PhotoImage, ttk

import random
import os

from views.details import DetailWindow
from traintracks.stations import Stations
from . import config as cfg

class StationsArea(tk.Frame):
  """
  A class to hold UI elements related to station selection.
  
  Parameters
  ----------
  tk : Frame
      
  Attributes
  ----------
  stations : Stations
      All Amtrak stations.
  stationKeys : list
      Display names for list elements.
  lengthOfList : int
  boxWidth : int
      Combobox width based on OS.
  origin : ttk.Combobox
  destination : ttk.Combobox
  swapButton : ttk.Button
  """
  def __init__(self, parent: tk.Tk, *args, **kwargs) -> None:
    """
    Initializes this area.

    Parameters
    ----------
    parent : tk.Tk
        Parent window.
    """
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.stations = Stations()
    self.stationKeys = self.stations.returnStationKeys()
    self.lengthOfList = len(self.stations.returnStationKeys())
    self.boxWidth = int(35/cfg.WIDTH_DIV)
    self.infoIcon = PhotoImage(file="information.png")
    self.infoIcon = self.infoIcon.zoom(2)
    self.infoIcon = self.infoIcon.subsample(64)
    
    tk.Label(self, text="Origin").grid(row=0, column=1, pady=1)
    tk.Label(self, text="Destination").grid(row=0, column=3, pady=1)

    tk.Button(self, image=self.infoIcon, relief=tk.FLAT, command=lambda: self.__openDetailView(1)).grid(row=1, column=0)
    self.origin = self.__createCombobox(1)
    self.origin.grid(row=1, column=1, padx=4)
    self.destination = self.__createCombobox(2)
    self.destination.grid(row=1, column=3, padx=4)
    tk.Button(self, image=self.infoIcon, relief=tk.FLAT, command=lambda: self.__openDetailView(2)).grid(row=1, column=4)

    self.swapButton = ttk.Button(self, text="<- Swap ->", command=self.__swapStations)
    self.swapButton.grid(row=1, column=2, padx=12)

    self.parent.imageArea.doRefresh(self.stations.returnCityState(self.origin.get()), 1)
    self.parent.imageArea.doRefresh(self.stations.returnCityState(self.destination.get()), 2)
    #if os.name == 'posix': self.parent.imageArea.doRefresh(self.stations.returnCityState(self.destination.get()), 2)
    #self.parent.startThread(self.parent.doRefresh, [self.stations.returnCityState(self.origin.get()), 1])
    #elif os.name == 'nt': self.parent.startThread(self.parent.imageArea.doRefresh, [self.stations.returnCityState(self.destination.get()), 2])

  def __openDetailView(self, side: int):
    if side == 1: _key = self.origin.get()
    elif side == 2: _key = self.destination.get()
    else: _key = {}

    if _key != {}:
      self.parent.startThread(DetailWindow, [self.parent, self.stations.returnStationData(_key)])

  def __swapStations(self) -> None:
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

  def __autocomplete(self, event) -> None:
    """If the user types in the combobox and presses Enter, results with from that query will be displayed."""
    val = event.widget.get()

    if val == '':
      event.widget['values'] = self.stationKeys
    else:
      data = []
      for item in self.stationKeys:
        if val.lower() in item.lower():
          data.append(item)
      event.widget['values'] = data

  def __createCombobox(self, side: int) -> ttk.Combobox:
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
    temp = ttk.Combobox(self, values=self.stationKeys, width=self.boxWidth, height=16, xscrollcommand=self.ignoreHorizontalScroll)
    temp.current(random.randint(0, self.lengthOfList-1))
    temp.bind("<<ComboboxSelected>>", lambda e, widget=temp, side=side, isSwap=False: self.__selectionChangedCallback(widget, side, isSwap, e))
    temp.bind("<Shift-MouseWheel>", self.ignoreHorizontalScroll)
    temp.bind("<KeyRelease>", self.__autocomplete)
    temp.bind("<Return>", lambda e: temp.event_generate("<Down>"))
    temp.bind("<Tab>", lambda e: temp.event_generate("<Down>"))
    #temp.configure(xscrollcommand=self.ignoreHorizontalScroll)
    self.parent.us.set(temp.get(), side)
    return temp

  def __selectionChangedCallback(self, widget: ttk.Combobox, side: int, isSwap: bool=False, e=None) -> None:
    """
    Event handler for item selections in the Combobox.

    Extended Summary
    ----------------
    The UserSelection variable(s) are set with the new values. A Lock is created before the image search begins, so if the user changes another image too quickly, the WebDriver will not fall apart, usually.

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
    if widget.get() != '':
      self.parent.us.set((widget.get()), side)
      city = self.stations.returnCityState(widget.get())
      self.parent.startThread(self.parent.imageArea.doRefresh, [city, side, isSwap])
      self.parent.startThread(self.parent.mapWindow.updateMarker, [side])
    widget['values'] = self.stationKeys