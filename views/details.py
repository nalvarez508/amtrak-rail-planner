import os
import json
from copy import deepcopy

import tkinter as tk
from tkinter import TclError, ttk, messagebox
from easygui import filesavebox

from views.config import BACKGROUND, ICON, SYSTEM_FONT

class DetailWindow(tk.Toplevel):
  """
  A class to create a JSON viewer window.

  Parameters
  ----------
  tk : Toplevel
  
  Attributes
  ----------
  parent : tk.Tk
  data : dict
  dataView : tk.Frame
  buttonsArea : tk.Frame
  texto : tk.Text

  Methods
  -------
  exportData
      Saves a txt or json file with the extra data.
  """
  def __init__(self, parent: tk.Tk, data: dict, *args, **kwargs) -> None:
    """
    Initializes a detail view window.

    Parameters
    ----------
    parent : tk.Tk
        Owner of the window, can be a frame or Toplevel.
    data : dict
        Train object organizational unit.
    """
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.data = data
    self.geometry('450x650')
    self.title(f"Detail View - {self.data['Name']}")
    if os.name == 'nt': self.iconbitmap(ICON)
    self.config(background=BACKGROUND)

    self.dataView = tk.Frame(self, background=BACKGROUND)
    self.buttonsArea = tk.Frame(self, background=BACKGROUND)

    ttk.Button(self.buttonsArea, text="Export", command=self.exportData).pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)
    ttk.Button(self.buttonsArea, text="Close", command=self.destroy).pack(side=tk.LEFT, anchor=tk.CENTER, padx=4)

    self.texto = tk.Text(self.dataView, font=(SYSTEM_FONT, 14, tk.NORMAL))
    self.yScr = tk.Scrollbar(self.dataView, command=self.texto.yview, orient=tk.VERTICAL)
    self.yScr.pack(side=tk.RIGHT, fill=tk.Y)
    self.texto.configure(yscrollcommand=self.yScr.set)
    self.texto.pack(expand=True, fill=tk.BOTH)

    self.texto.insert('end', self._dataClean())
    self._thatsPrettyBold()
    self.texto.configure(state=tk.DISABLED)

    self.dataView.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
    self.buttonsArea.pack(side=tk.BOTTOM, expand=False, padx=4, pady=4, anchor=tk.S)

    self.wm_protocol('WM_DELETE_WINDOW', self.destroy)
  
  def _dataClean(self) -> str:
    _data = json.dumps(self.data, indent=0)
    _data = _data.replace('"', '').replace(',', '')
    _data = _data.replace('{', '').replace('}', '')
    _data = _data.replace('[', '').replace('\n]', '').replace(']', '')
    _data = _data.replace('Segment Info:', '\n\nSegment Info')
    _data = _data.replace('\n\n', '\n').replace('\n      ', '\n')
    _data = _data.replace('\n      ', '\n')
    _data = _data.replace(': ', ':  ')
    _data = _data.replace('null', 'N/A')
    _data = _data.strip()
    return _data

  def _thatsPrettyBold(self) -> None:
    """Makes dictionary keys **BOLD.**"""
    def findKeys(k: str, before: dict):
      nonlocal _pos
      try:
        for key in before[k].keys():
          _pos = self.texto.search(str(key), _pos, stopindex="end", count=count)
          if k == "Segment Info":
            self.texto.delete(_pos, f"{_pos} + {int(count.get())+1}c")
            self.texto.insert(_pos, f"\nSegment {int(key)+1}")
            _pos = self.texto.search(f"\nSegment {int(key)+1}", _pos, stopindex="end", count=count)
            self.texto.tag_add("blue", _pos, f"{_pos} + {int(count.get())+1}c")
          self.texto.tag_add("bold", _pos, f"{_pos} + {int(count.get())+1}c")
          _pos = str(int(float(_pos))+1)+".0"
          #_pos = str(float(_pos)+1)
          findKeys(key, before[k])
      except AttributeError:
        pass
    _pos = "1.0"
    count = tk.StringVar()
    for key in self.data.keys():
      _pos = self.texto.search(str(key), _pos, stopindex="end", count=count)
      self.texto.tag_add("bold", _pos, f"{_pos} + {int(count.get())+1}c")
      _pos = str(int(float(_pos))+1)+".0"
      #_pos = str(float(_pos)+1)
      findKeys(key, self.data)

    try:
      _pos = self.texto.search("Segment Info", '1.0', stopindex="end", count=count)
      self.texto.tag_add("underline", _pos, f"{_pos} + {int(count.get())+1}c")
    except TclError:
      pass

    self.texto.tag_config("bold", font=(SYSTEM_FONT, 14, "bold"))
    self.texto.tag_config("blue", font=(SYSTEM_FONT, 14, 'bold', 'italic'), foreground='blue')
    self.texto.tag_config("underline", font=(SYSTEM_FONT, 16, 'bold', 'underline'))

  def _convertToHTML(self, data) -> str:
    """Converts JSON data to a formatted HTML string."""
    def findTypes(p, d):
      nonlocal outStr
      if type(p[d]) == list:
        outStr += f"<b>{d}</b><br>\n"
        for x in p[d]:
          outStr += f"<li>{x}</li>\n"
      elif type(p[d]) == dict:
        outStr += f"<h2>{d}</h2>\n"
        for key in p[d]:
          outStr += f"{'<br>' if int(key) > 0 else ''}<u>Segment {int(key)+1}</u><br>"
          for item2 in p[d][key]:
            findTypes(p[d][key], item2)
      else:
        outStr += f"<b>{d}:</b> {p[d]}<br>\n"
    outStr = ""
    outStr += f"<h1>{data['Name']}</h1>\n"
    for item in data:
      findTypes(data, item)
    return outStr

  def exportData(self) -> None:
    """Saves the JSON data to a text or json file."""
    _def = os.path.expanduser("~")
    path = filesavebox(msg="Data can be saved in HTML, JSON or TXT formats.", title="Export Train Data", default=f"{_def}/data - {self.data['Name']}.html", filetypes=["*.html, *.json, *.txt"])
    if path != None:
      if path.endswith('.html'):
        dataToWrite = self._convertToHTML(self.data)
      else:
        dataToWrite = json.dumps(self.data, indent=2)
      try:
        with open(path, "w") as f:
          f.write(dataToWrite)
      except FileNotFoundError:
        messagebox.showerror(title="Export Train Data", message="Unable to write this to a file.")

if __name__ == "__main__":
  root = tk.Tk()
  _d = {"Name": "California Zephyr", "Number": 6}
  DetailWindow(root, _d)
  root.mainloop()