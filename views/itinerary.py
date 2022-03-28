import tkinter as tk
from tkinter import ttk

from views.config import WIDTH_DIV

class Itinerary(tk.Toplevel):
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel(self, parent, *args, **kwargs)
    self.parent = parent
    self.inViewSavedSegments = dict()
    self.segmentsArea = tk.Frame(self)

    self.columns = []
    self.headerCols = []
    self.userSegments = ttk.Treeview(self.segmentsArea, columns=self.columns, show='headings', cursor='hand2', selectmode='browse', height=12/WIDTH_DIV)
    self.__makeHeadings()
    self.tvScroll = ttk.Scrollbar(self.segmentsArea, orient='vertical', command=self.userSegments.yview)
    self.userSegments.configure(yscrollcommand=self.tvScroll.set)

    self.userSegments.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    self.tvScroll.pack(side=tk.RIGHT, fill=tk.BOTH)
    self.segmentsArea.pack(fill=tk.BOTH, padx=8, pady=4, expand=True)

  def __makeHeadings(self):
    dispCols = list()
    for index, col in enumerate(self.headerCols):
      self.userSegments.heading(self.columns[index], text=col, anchor='w')
      self.userSegments.column(self.columns[index], minwidth=10, width=self.headerCols[col], stretch=True, anchor='w')
      dispCols.append(self.columns[index])
    self.userSegments["displaycolumns"] = dispCols # Creates mapping so we can retrieve Train objects later