import tkinter as tk
from tkinter import ttk, font
import os
import random
import sys
from threading import Thread, Event, Lock

from HelperClasses import Train, RailPass, Driver, UserSelections, Stations
from DriverHelper import ImageSearch
from AmtrakSearcher import AmtrakSearch

APP_NAME = "Amtrak Rail Planner"
IMAGE_DIMENSIONS = [245,183]
if os.name == 'nt':
  SYSTEM_FONT = "Segoe UI"
elif os.name == 'posix':
  SYSTEM_FONT = "TkDefaultFont"
#DefaultFont = None

class TitleArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    tk.Label(self, text=APP_NAME, font=(SYSTEM_FONT, 24, 'bold')).pack()
    tk.Label(self, text="Make the most of your Rail Pass!", font=(SYSTEM_FONT, 12, 'italic')).pack()#, font=(SYSTEM_FONT, 12, 'italic')).pack()

class ImageArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.imageCatcher = ImageSearch()
    #self.imageCatcher.loadImage(self.parent.us.getOrigin(), 1)
    #self.imageCatcher.loadImage(self.parent.us.getDestination(), 2)

    self.leftImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(1), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.leftImage.grid(row=0, column=0, padx=4, pady=16)
    #self.leftImage.bind("<Configure>", self.resizeImageCallback)

    self.rightImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(2), width=IMAGE_DIMENSIONS[0], height=IMAGE_DIMENSIONS[1])
    self.rightImage.grid(row=0, column=1, padx=4, pady=16)

  def updateImage(self, side):
    if side == 1:
      self.leftImage.configure(image=self.imageCatcher.getCityPhoto(side))
    elif side == 2:
      self.rightImage.configure(image=self.imageCatcher.getCityPhoto(side))


class StationsArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.stations = Stations()
    lengthOfList = len(self.stations.returnStationKeys())

    self.origin = ttk.Combobox(self, values=self.stations.returnStationKeys())
    self.origin.grid(row=0, column=0, padx=4)
    self.origin.current(random.randint(0, lengthOfList-1))
    self.origin.bind("<<ComboboxSelected>>", lambda e, widget=self.origin, side=1: self.selectionChangedCallback(widget, side, e))
    self.parent.us.setOrigin(self.stations.getStationCode(self.origin.get()))

    self.destination = ttk.Combobox(self, values=self.stations.returnStationKeys())
    self.destination.grid(row=0, column=2, padx=4)
    self.destination.current(random.randint(0, lengthOfList-1))
    self.destination.bind("<<ComboboxSelected>>", lambda e, widget=self.destination, side=2: self.selectionChangedCallback(widget, side, e))
    self.parent.us.setDestination(self.stations.getStationCode(self.destination.get()))

    self.searchButton = tk.Button(self, text="Find Trains", command=self.startSearch)
    self.searchButton.grid(row=0, column=1, padx=4)

    self.parent.doRefresh(self.stations.returnCityState(self.origin.get()), 1)
    self.parent.doRefresh(self.stations.returnCityState(self.destination.get()), 2)

  def startSearch(self):
    pass

  def selectionChangedCallback(self, widget, side, e=None):
    city = self.stations.returnCityState(widget.get())
    self.parent.us.setOrigin(self.origin.get())
    self.parent.us.setDestination(self.destination.get())
    self.parent.startThread(self.parent.doRefresh, [city, side, self.parent.imageDriverLock])

class MainWindow(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("Rail Pass Planner")
    self.iconbitmap("Amtrak_square.ico")
    self.us = UserSelections()
    self.imageDriverLock = Lock()

    self.titleArea = TitleArea(self)
    self.imageArea = ImageArea(self)
    self.stationsArea = StationsArea(self)

    self.titleArea.pack()
    self.imageArea.pack()
    self.stationsArea.pack()

  def startThread(self, function, args=[None]):
    t1 = Thread(target=function, args=args)
    t1.start()

  def onClose(self):
    self.imageArea.imageCatcher.driver.close()
    self.imageArea.imageCatcher.driver.quit()
    self.destroy()
    sys.exit()

  def doRefresh(self, city, side, lock=None):
    if city != self.imageArea.imageCatcher.getCityName(side):
      try:
        with lock:
          self.imageArea.imageCatcher.loadImage(city, side, IMAGE_DIMENSIONS)
      except AttributeError:
        self.imageArea.imageCatcher.loadImage(city, side, IMAGE_DIMENSIONS)
      self.imageArea.updateImage(side)
      self.update_idletasks()

if __name__ == "__main__":
  app = MainWindow()
  app.wm_protocol("WM_DELETE_WINDOW", app.onClose)
  app.mainloop()