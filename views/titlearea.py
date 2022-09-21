import tkinter as tk

from . import config as cfg

class TitleArea(tk.Frame):
  """
  A class to hold UI elements related to the title at the top of the window.
  
  Parameters
  ----------
  tk : Frame
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
    tk.Label(self, text=cfg.APP_NAME, font=(cfg.SYSTEM_FONT, 24, 'bold'), background=cfg.BACKGROUND).pack()
    #tk.Label(self, text="Make the most of your Rail Pass!", font=(cfg.SYSTEM_FONT, 12, 'italic'), background=cfg.BACKGROUND).pack()