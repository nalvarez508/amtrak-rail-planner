import tkinter as tk

import webbrowser

from . import config as cfg

class MenuOptions(tk.Menu):
  def __init__(self, parent, *args, **kwargs):
    tk.Menu.__init__(self, parent)
    self.parent = parent
    self.helpmenu = tk.Menu(self, tearoff=0)
    self.helpmenu.add_command(label="Open Route Map", command=lambda: self.openLink("https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/Maps/Amtrak-System-Map-1018.pdf"))
    self.helpmenu.add_command(label="About", command=lambda: self.openBox("Amtrak Rail Pass Assistant\nv0.1.0"))
    self.add_cascade(label="Help", menu=self.helpmenu)

  def openLink(self, l):
    webbrowser.open(l, new=1, autoraise=True)
  
  def openBox(self, m):
    tk.messagebox.showinfo(cfg.APP_NAME, message=m)