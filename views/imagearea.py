import tkinter as tk

from threading import Lock
import webbrowser
from urllib.parse import quote

from searcher.image_searcher import ImageSearch
from . import config as cfg

class ImageArea(tk.Frame):
  """
  A class to hold UI elements related to displaying images of origin/destination cities.
  
  Parameters
  ----------
  tk : Frame
      
  Attributes
  ----------
  imageCatcher : ImageSearch
      Creates a driver for the purpose of finding images.
  imageDriverLock : threading.Lock
      Used to stop two requests from getting to the WebDriver at the same time.
  leftImage : tk.Label
      Origin city picture.
  rightImage : tk.Label
      Destination city picture.
  
  Methods
  -------
  doRefresh(city, side, isSwap=False)
      Refreshes the images in the window with new cities.
  updateImage(side)
      Refreshes the selected image Label.
  """
  def __init__(self, parent: tk.Tk, *args, **kwargs) -> None:
    """
    One time initialization of an Image Searcher, should be persistent throughout app usage due to cost of launching webdriver.

    Parameters
    ----------
    parent : tk.Tk
        Parent window.
    """
    tk.Frame.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.imageCatcher = ImageSearch()
    self.imageDriverLock = Lock()

    self.leftImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(1), width=cfg.IMAGE_DIMENSIONS[0], height=cfg.IMAGE_DIMENSIONS[1], cursor='hand1')
    self.leftImage.grid(row=0, column=0, padx=4, pady=4)
    self.leftImage.bind("<Button-1>", lambda e: self.__photoClickCallback(1))

    self.rightImage = tk.Label(self, image=self.imageCatcher.getCityPhoto(2), width=cfg.IMAGE_DIMENSIONS[0], height=cfg.IMAGE_DIMENSIONS[1], cursor='hand1')
    self.rightImage.grid(row=0, column=1, padx=4, pady=4)
    self.rightImage.bind("<Button-1>", lambda e: self.__photoClickCallback(2))

  def __test_widgetDims(self):
    self.leftInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")
    self.rightInfo.config(text=f"{self.leftImage.winfo_width()}x{self.leftImage.winfo_height()}")

  def __photoClickCallback(self, side: int) -> None:
    """Opens a tourism link to a selected photo."""
    myCity = self.imageCatcher.getCityName(side)
    baseUrl = "https://duckduckgo.com/?q=!ducky+"
    myCityUrlSuffix = quote((myCity + " tourism official"))
    webbrowser.open(baseUrl + myCityUrlSuffix) # "I'm Feeling Lucky" result

  def doRefresh(self, city: str, side: int, isSwap: bool=False) -> None:
    """
    Refreshes the ImageArea labels with new cities.

    Parameters
    ----------
    city : str
        'City, State'
    side : int
        Accepts 1 (left/origin) or 2 (right/destination).
    isSwap : bool, optional
        True if the images are only being swapped, by default False
    
    Raises
    ------
    AttributeError
        Lock failed, somehow.
    """
    if isSwap == False:
      if city != self.imageCatcher.getCityName(side): # Do not update anything if the same city is selected
        self.imageCatcher.setCityPhoto(side, None) # Remove the photo to indicate something is happening
        self.updateImage(side)
        try:
          with self.imageDriverLock:
            self.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS) # Find a new image
        except AttributeError:
          self.imageCatcher.loadImage(city, side, cfg.IMAGE_DIMENSIONS)
        self.updateImage(side)
    elif isSwap == True: # Do not call search functions
      self.updateImage(side)
    self.update_idletasks()

  def updateImage(self, side: int) -> None:
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