import tkinter as tk

import webbrowser

from . import config as cfg

class MenuOptions(tk.Menu):
  """
  A class to hold UI elements for the menu bar.

  Parameters
  ----------
  tk : Tk
      The parent frame.

  Attributes
  ----------
  helpmenu : Menu

  Methods
  -------
  openLink(l)
      Opens a link in the default web browser.
  openBox(m)
      Displays an info box with a message.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Menu.__init__(self, parent)
    self.parent = parent
    self.helpmenu = tk.Menu(self, tearoff=0)
    self.helpmenu.add_command(label="Open Route Map", command=lambda: self.openLink("https://www.amtrak.com/content/dam/projects/dotcom/english/public/documents/Maps/Amtrak-System-Map-1018.pdf"))
    self.helpmenu.add_command(label="About", command=lambda: self.openBox("Amtrak Rail Pass Assistant\nv0.1.0"))
    self.add_cascade(label="Help", menu=self.helpmenu)

  def openLink(self, l):
    """
    Opens a link in the default web browser.

    Parameters
    ----------
    l : str
        Fully qualified URL.
    """
    webbrowser.open(l, new=1, autoraise=True)
  
  def openBox(self, m):
    """
    Displays an information messagebox.

    Parameters
    ----------
    m : str
        The message to display.
    """
    tk.messagebox.showinfo(cfg.APP_NAME, message=m)