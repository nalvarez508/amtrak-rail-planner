import tkinter as tk
from tkinter import font

class DevTools(tk.Toplevel):
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.title("Dev Tools")
    tk.Label(self, text="Development Tools", font=('', 16, font.NORMAL)).pack()
    tk.Button(self, text="Print Geometry", command=self.parent._test_getGeometry).pack()
    tk.Button(self, text="Print Column Info", command=self.parent.trainResultsArea._test_getColInfo).pack()
    tk.Button(self, text="Print Selection", command=self.parent.trainResultsArea.getSelection).pack()
    tk.Button(self, text="Print Widget Background", command=self.parent._test_getBackground).pack()