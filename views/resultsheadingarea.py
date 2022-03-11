import tkinter as tk
from tkinter import ttk, font

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

    self.titleToAndFrom = tk.StringVar(self)
    self.searchDate = tk.StringVar(self)
    self.background = self.parent.resultsBackground
    self.config(background=self.background)
    self.boldItalic = font.Font(family=cfg.SYSTEM_FONT, size=14, weight=font.BOLD, slant=font.ITALIC)
    self.numberOfTrains = tk.StringVar(self)

    self.titleLabel = tk.Label(self, textvariable=self.titleToAndFrom, font=self.boldItalic, background=self.background)
    self.titleLabel.pack()#grid(row=0, column=0, pady=4)
    self.dateLabel = tk.Label(self, textvariable=self.searchDate, font=(cfg.SYSTEM_FONT, 11, font.NORMAL), background=self.background)
    self.dateLabel.pack()
    self.numberLabel = tk.Label(self, textvariable=self.numberOfTrains, background=self.background)
    self.numberLabel.pack()#grid(row=1, column=0)