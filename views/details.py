import os
import json
from copy import deepcopy

import tkinter as tk
from tkinter import ttk, messagebox
from easygui import filesavebox

from views.config import BACKGROUND, ICON

class DetailWindow(tk.Toplevel):
  def __init__(self, parent, data, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.data = data
    self.geometry('400x600')
    self.title(f"Detail View - {self.data['Name']}")
    if os.name == 'nt': self.iconbitmap(ICON)
    self.config(background=BACKGROUND)

    self.dataView = tk.Frame(self, background=BACKGROUND)
    self.buttonsArea = tk.Frame(self, background=BACKGROUND)

    ttk.Button(self.buttonsArea, text="Export", command=self.exportData).pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)
    ttk.Button(self.buttonsArea, text="Close", command=self.destroy).pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)

    self.texto = tk.Text(self.dataView, font=("Arial", 14, tk.NORMAL))
    self.yScr = tk.Scrollbar(self.dataView, command=self.texto.yview, orient=tk.VERTICAL)#.grid(row=0, column=1, sticky='ns')
    self.yScr.pack(side=tk.RIGHT, fill=tk.Y)
    # self.xScr = tk.Scrollbar(self.dataView, command=self.texto.xview, orient=tk.HORIZONTAL)#.grid(row=1, column=0, columnspan=2, sticky='ew')
    # self.xScr.pack(side=tk.BOTTOM, fill=tk.X)
    self.texto.configure(yscrollcommand=self.yScr.set)#, xscrollcommand=self.xScr.set)
    self.texto.pack(expand=True, fill=tk.BOTH)
    

    _data = json.dumps(self.data, indent=4)
    _data = _data.replace('"', '')
    self.texto.insert('end', _data)
    self._thatsPrettyBold()
    self.texto.configure(state=tk.DISABLED)

    self.dataView.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
    self.buttonsArea.pack(side=tk.BOTTOM, expand=False, padx=4, pady=4)

    self.wm_protocol('WM_DELETE_WINDOW', self.destroy)
  
  def _dataClean(self, data) -> dict:
    _t = {}
    d = deepcopy(data)
    for key in d["Segment Info"]:
      try:
        _t["Segment Info"][f"Segment {int(key)+1}"] = d["Segment Info"][key]
      except ValueError:
        _t[key] = d[key]
    return _t
  
  def _thatsPrettyBold(self):
    def findKeys(k, before):
      nonlocal _pos
      try:
        for key in before[k].keys():
          _pos = self.texto.search(str(key), _pos, stopindex="end", count=count)
          self.texto.tag_add("bold", _pos, f"{_pos} + {int(count.get())+1}c")
          #_pos = str(float(_pos)+1)
          findKeys(key, before[k])
      except AttributeError:
        pass
    _pos = "1.0"
    count = tk.StringVar()
    for key in self.data.keys():
      _pos = self.texto.search(str(key), _pos, stopindex="end", count=count)
      self.texto.tag_add("bold", _pos, f"{_pos} + {int(count.get())+1}c")
      #_pos = str(float(_pos)+1)
      findKeys(key, self.data)
    self.texto.tag_config("bold", font=("Arial", 14, "bold"))

  def exportData(self):
    _def = os.path.expanduser("~")
    path = filesavebox(msg="Data can be saved in JSON or TXT formats.", title="Export Train Data", default=f"{_def}/data.json", filetypes=["*.json, *.txt"])
    if path != None:
      try:
        with open(path, "w") as f:
          f.write(json.dumps(self.data, indent=2))
      except FileNotFoundError:
        messagebox.showerror(title="Export Train Data", message="Unable to write this to a file.")

if __name__ == "__main__":
  root = tk.Tk()
  _d = {"Name": "California Zephyr", "Number": 6}
  DetailWindow(root, _d)
  root.mainloop()