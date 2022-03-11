import tkinter as tk

from . import config as cfg

class TitleArea(tk.Frame):
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    tk.Label(self, text=cfg.APP_NAME, font=(cfg.SYSTEM_FONT, 24, 'bold'), background=cfg.BACKGROUND).pack()
    tk.Label(self, text="Make the most of your Rail Pass!", font=(cfg.SYSTEM_FONT, 12, 'italic'), background=cfg.BACKGROUND).pack()

if __name__ == "__main__":
  TitleArea(None)