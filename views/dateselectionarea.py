import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar as Cal

import time
import datetime

from . import config as cfg

class DateSelectionArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.isCalendarShown = False
    self.incrementWidth = int(3/cfg.WIDTH_DIV)
    self.dateDisplay = tk.StringVar(self, self.parent.us.getPrettyDate())
    self.incrementButton = ttk.Style()
    self.incrementButton.configure('inc.TButton', font=(cfg.SYSTEM_FONT, 10))
    self.incrementArea = tk.Frame(self)
    ttk.Button(self, text="Select Departure Date", command=self.showCalendar).grid(row=0, column=0)
    self.currentDate = tk.Label(self, textvariable=self.dateDisplay, width=25, relief=tk.SUNKEN, cursor="hand2")
    self.currentDate.grid(row=0, column=1, padx=8)
    ttk.Button(self.incrementArea, text="-", command=lambda d=-1:self.changeDate(d), width=self.incrementWidth, style="inc.TButton").grid(row=0, column=0)
    ttk.Button(self.incrementArea, text="+", command=lambda d=1:self.changeDate(d), width=self.incrementWidth, style="inc.TButton").grid(row=0, column=1)
    self.incrementArea.grid(row=0, column=2)
    self.calendar = self.createCalendarArea()

    self.currentDate.bind("<Button-1>", lambda e: self.showCalendar())

  def changeDate(self, d):
    if type(d) == int:
      self.parent.us.incrementDate(d)
    elif type(d) == datetime.date:
      self.parent.us.setDate(d)
    self.dateDisplay.set(self.parent.us.getPrettyDate())
    self.update_idletasks()
  
  def callbackCalendar(self, e=None):
    self.changeDate(self.calendar.selection_get())
    self.removeCal()
  
  def removeCal(self):
    time.sleep(0.15)
    self.calendar.grid_remove()
    self.isCalendarShown = False
    self.update_idletasks()

  def showCalendar(self):
    if self.isCalendarShown == False:
      self.calendar.grid(row=1, column=0, columnspan=4, pady=8)
      self.isCalendarShown = True
    else:
      self.removeCal()
    self.update_idletasks()

  def createCalendarArea(self):
    rightNow = self.parent.us.getDate()
    cal = Cal(self, selectmode='day', year=rightNow.year, month=rightNow.month, day=rightNow.day, firstweekday="sunday", mindate=rightNow, date_pattern="m/d/y")
    cal.bind("<<CalendarSelected>>", self.callbackCalendar)
    return cal

  def createCalendarPopupWindow(self):
    def getCalDate():
      date = cal.selection_get()
      #date = datetime.datetime.strptime(date, "%m/%d/%Y")
      #date = datetime.date(year=date.year, month=date.month, day=date.day)
      self.changeDate(cal.selection_get())
    calWindow = tk.Toplevel(self.parent)
    rightNow = self.parent.us.getDate()
    cal = Cal(calWindow, selectmode='day', year=rightNow.year, month=rightNow.month, day=rightNow.day)
    cal.pack()
    tk.Button(cal, text="Select", command=getCalDate).pack()
    calWindow.wm_protocol("WM_DELETE_WINDOW", calWindow.destroy)
    calWindow.mainloop()