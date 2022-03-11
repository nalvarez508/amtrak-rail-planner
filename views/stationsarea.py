import tkinter as tk
from tkinter import ttk

import random

from traintracks.stations import Stations
from . import config as cfg

class StationsArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.stations = Stations()
    self.lengthOfList = len(self.stations.returnStationKeys())
    self.boxWidth = int(30/cfg.WIDTH_DIV)
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