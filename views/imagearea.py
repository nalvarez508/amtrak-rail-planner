import tkinter as tk

from searcher.image_searcher import ImageSearch
from . import config as cfg

class ImageArea(tk.Frame):
  """
  A class to hold UI elements related to displaying images of origin/destination cities.
  
  Parameters
  ----------
  tk : Tk
      The parent frame.
      
  Attributes
  ----------
  imageCatcher : ImageSearch
      Creates a driver for the purpose of finding images.
  leftImage : tk.Label
      Origin city picture.
  rightImage : tk.Label
      Destination city picture.
  
  Methods
  -------
  updateImage(side)
      Refreshes the selected image Label.
  """
  def __init__(self, parent, *args, **kwargs):
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.imageCatcher = ImageSearch()

    self.leftImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(1), width=cfg.IMAGE_DIMENSIONS[0], height=cfg.IMAGE_DIMENSIONS[1])
    self.leftImage.grid(row=0, column=0, padx=4, pady=4)
    #self.leftImage.bind("<Configure>", self.resizeImageCallback)

    self.rightImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(2), width=cfg.IMAGE_DIMENSIONS[0], height=cfg.IMAGE_DIMENSIONS[1])
    self.rightImage.grid(row=0, column=1, padx=4, pady=4)

    #self.leftInfo = tk.Label(self, text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")
    #self.leftInfo.grid(row=1, column=0)
    #self.rightInfo = tk.Label(self, text=f"{self.rightImage.winfo_width()}x{self.rightImage.winfo_height()}")
    #self.rightInfo.grid(row=1, column=2)
    #tk.Button(self, text="Update", command=self._test_widgetDims).grid(row=1, column=1)

  def __test_widgetDims(self):
    self.leftInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")
    self.rightInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")

  def updateImage(self, side):
    """
    Gets the new image to be displayed on the appropriate side.

    Parameters
    ----------
    side : int
        Accepts 1 (left/origin label) or 2 (right/destination) label.
    """
    if side == 1:
      self.leftImage.configure(image=self.imageCatcher.getCityPhoto(side))
    elif side == 2:
      self.rightImage.configure(image=self.imageCatcher.getCityPhoto(side))