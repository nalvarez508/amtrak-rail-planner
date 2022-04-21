import tkinter as tk
from tkinter import ttk, font

from copy import deepcopy

from . import config as cfg

class ResultsHeadingArea(tk.Frame):
  """
  A class to hold UI elements related to current search information.
  
  Parameters
  ----------
  tk : Tk
      The parent frame.
      
  Attributes
  ----------
  titleToAndFrom : StringVar
      Heading for search title (to and from stations).
  searchDate : StringVar
  background : str
  boldItalic : Font
      Custom heading style: large, bold, and italic.
  numberOfTrains : StringVar
  titleLabel = tk.Label
  dateLabel = tk.Label
  numberLabel = tk.Label
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.background = self.parent.resultsBackground
    self.titleInfoFrame = tk.Frame(self, background=self.background)
    self.segmentSearchFrame = tk.Frame(self, background=self.background)

    self.searchNum = 1
    self.searchNumVar = tk.StringVar(self, value=f"Search {self.searchNum}")
    self.titleToAndFrom = tk.StringVar(self, value="Click \"Find Trains\" to start a search!")
    self.searchDate = tk.StringVar(self)

    self.config(background=self.background)
    self.boldItalic = font.Font(family=cfg.SYSTEM_FONT, size=14, weight=font.BOLD, slant=font.ITALIC)
    self.numberOfTrains = tk.StringVar(self)

    self.leftSegmentButton = ttk.Button(self.segmentSearchFrame, text='<', state='disabled', command=self.__goLeft)
    self.rightSegmentButton = ttk.Button(self.segmentSearchFrame, text='>', state='disabled', command=self.__goRight)

    self.leftSegmentButton.pack(side=tk.LEFT, anchor=tk.NW, padx=8)
    #tk.Label(self.segmentSearchFrame, textvariable=self.searchNum, background=self.background).pack(side=tk.LEFT, anchor=tk.CENTER, fill=tk.X, padx=4, expand=True)
    self.titleLabel = tk.Label(self.segmentSearchFrame, textvariable=self.titleToAndFrom, font=self.boldItalic, background=self.background)
    self.titleLabel.pack(side=tk.LEFT, anchor=tk.CENTER, fill=tk.X, padx=4, expand=True)
    self.rightSegmentButton.pack(side=tk.LEFT, anchor=tk.NE, padx=8)

    self.dateLabel = tk.Label(self.titleInfoFrame, textvariable=self.searchDate, font=(cfg.SYSTEM_FONT, 11, font.NORMAL), background=self.background)
    self.dateLabel.pack()
    self.numberLabel = tk.Label(self.titleInfoFrame, textvariable=self.numberOfTrains, background=self.background)
    self.numberLabel.pack()#grid(row=1, column=0)

    self.segmentSearchFrame.pack(fill=tk.X, anchor=tk.CENTER)
    self.titleInfoFrame.pack(padx=4)
  
  def __updateResultsWidgets(self, doTreeviewRefresh=True):
    self.searchNumVar.set(f"Search {self.searchNum}")
    self.__searchButtonToggle()

    # Get updated values
    thisPreviousSearch = deepcopy(self.parent.us.userSelections.getSearch(self.searchNum))
    o = thisPreviousSearch["Origin"]
    d = thisPreviousSearch["Destination"]
    t = thisPreviousSearch["Date"]
    r = thisPreviousSearch["Results"]
    i = thisPreviousSearch["Saved Index"]

    # Set updated values
    self.parent.us.setOrigin(o)
    self.parent.us.setDestination(d)
    self.parent.us.setDate(t)

    # Redraw widgets
    self.titleToAndFrom.set(f"{self.parent.stationsArea.stations.returnStationNameAndState(o)} to {self.parent.stationsArea.stations.returnStationNameAndState(d)}")
    self.searchDate.set(self.parent.us.getPrettyDate())
    if doTreeviewRefresh: self.parent.trainResultsArea.refreshHandler(r, i)

  def getSearchNum(self):
    return self.searchNum

  def changeSearchView(self, searchnum):
    if (searchnum <= self.parent.us.userSelections.numSearches) and (searchnum >= 1):
      self.searchNum = searchnum
    else:
      self.searchNum = self.parent.us.userSelections.numSearches
    self.__updateResultsWidgets(False if searchnum == -1 else True)

  def __goLeft(self):
    # Populate a treeview
    if self.searchNum > 1:
      self.searchNum -= 1
      self.__updateResultsWidgets()
  
  def __goRight(self):
    # Populate a treeview
    if self.searchNum < self.parent.us.userSelections.numSearches:
      self.searchNum += 1
      self.__updateResultsWidgets()

  def __searchButtonToggle(self):
    currentView = self.searchNum
    totalSearches = self.parent.us.userSelections.numSearches

    if currentView == 1:
      self.leftSegmentButton.config(state='disabled')
      if totalSearches == 1:
        self.rightSegmentButton.config(state='disabled')
      elif totalSearches > 1:
        self.rightSegmentButton.config(state='normal')
    elif currentView > 1:
      self.leftSegmentButton.config(state='normal')
      if totalSearches > currentView:
        self.rightSegmentButton.config(state='normal')
      elif totalSearches == currentView:
        self.rightSegmentButton.config(state='disabled')
    
    self.update_idletasks()