import PIL.Image, PIL.ImageTk, PIL.ImageFile
from io import BytesIO
import base64
import urllib.parse
import urllib.request
from tkinter import TclError
from fractions import Fraction

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from .driver import Driver

class ImageSearch:
  """
  A class to search for images of selected cities in the ImageArea.

  Attributes
  ----------
  driver : Driver
  photo_city1 : PhotoImage
  photo_city2 : PhotoImage
  name_city1 : str
  name_city2 : str

  Methods
  -------
  loadImage(c, no, dims)
      Returns an image object for a specified city.
  doCitySwap
      Swaps the city photo objects without finding new ones.
  getCityName(cityNo)
      Returns a city's name.
  setCityPhoto(cityNo, data)
      Sets a city's photo to `data`.
  getCityPhoto(cityNo)
      Returns a city's photo object.
  """
  def __init__(self):
    self.driver = Driver().driver
    PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True

    self.photo_city1 = None
    self.photo_city2 = None
    self.name_city1 = None
    self.name_city2 = None

  def __returnCityPhoto(self, c):
    """
    Searches Google for the first image of a city and saves it.

    Parameters
    ----------
    c : str
        'City, State'

    Returns
    -------
    list[str, bytes]
        Returns a list with type of image (Image "Img" or Base64 "B64") and the raw data.
    """
    URL = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(c)}"
    self.driver.get(URL)
    image = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.XPATH, "//img[@class='rg_i Q4LuWd']")))

    def checkIfB64(src):
      header = src.split(',')[0]
      if header.startswith('data') and ';base64' in header:
        imgType = header.replace('data:image/', '').replace(';base64', '')
        return imgType
      return None
    
    def getHiDef(): # Try and get image from URL and not base64 preview from google
      try:
        self.driver.find_element(By.XPATH, "//div[@class='bRMDJf islir']").click()
        bigImageArea = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//img[@class='n3VNCb']")))
        imageLink = bigImageArea.get_attribute('src')
        with urllib.request.urlopen(imageLink) as connection:
          raw_data = connection.read()
        return ["Img", raw_data]

      except:
        s = image.get_attribute('src')
        if s is not None:
          if checkIfB64(s):
            return ["B64", (s.split(';base64,')[1])]
          else:
            return None
        else:
          return None

    return getHiDef()

  def loadImage(self, c, no, dims):
    """
    Finds an image for a given city and returns an image object with specified dimensions.

    Parameters
    ----------
    c : str
        'City, State'
    no : int
        Accepts 1 (left/origin) or 2 (right/destination).
    dims : list
        Width and height of output image.
    """
    def crop_resize(image):
      ratio = Fraction(dims[0], dims[1])
      size = dims
      # crop to ratio, center
      w, h = image.size
      if w > ratio * h: # width is larger then necessary
        x, y = (w - ratio * h) // 2, 0
      else: # ratio*height >= width (height is larger)
        x, y = 0, (h - w / ratio) // 2
      image = image.crop((x, y, w - x, h - y))

      # resize
      #if image.size > tuple(size): # don't stretch smaller images
      #  image.thumbnail(size, PIL.Image.ANTIALIAS)
      return image
    
    try:
      onlineImage = self.__returnCityPhoto(c)
      if onlineImage[0] == "B64":
        onlineImage[1] = (base64.b64decode(onlineImage[1]))

      fh = BytesIO(onlineImage[1])
      img = PIL.Image.open(fh, mode='r')
      img = crop_resize(img)
      img.thumbnail((dims), PIL.Image.ANTIALIAS)
      render = PIL.ImageTk.PhotoImage(image=img)

      self.setCityPhoto(no, render)
      self.__setCityName(no, c)
      print(img.size)
    except TclError as e:
      print(e)

  def doCitySwap(self):
    """
    Swaps images and city names for the origin and destination.
    """
    tempCity2 = self.getCityName(2)
    self.__setCityName(2, self.getCityName(1))
    self.__setCityName(1, tempCity2)
    tempPhoto2 = self.getCityPhoto(2)
    self.setCityPhoto(2, self.getCityPhoto(1))
    self.setCityPhoto(1, tempPhoto2)

  def __setCityName(self, cityNo, data):
    """
    Updates the stored city name.

    Parameters
    ----------
    cityNo : int
        Accepts 1 (left/origin) or 2 (right/destination).
    data : str
        New city name in the form 'City, State'.
    """
    if cityNo == 1:
      self.name_city1 = data
    elif cityNo == 2:
      self.name_city2 = data
  
  def getCityName(self, cityNo):
    """
    Returns the selected city's name.

    Parameters
    ----------
    cityNo : int
        Accepts 1 (left/origin) or 2 (right/destination).

    Returns
    -------
    str
        City name in the form 'City, State'.
    """
    if cityNo == 1:
      return self.name_city1
    elif cityNo == 2:
      return self.name_city2

  def setCityPhoto(self, cityNo, data):
    """
    Updates the city photo variable with new image data.

    Parameters
    ----------
    cityNo : int
        Accepts 1 (left/origin) or 2 (right/destination).
    data : PhotoImage or None
        Sets the new image, or erases it if None.
    """
    if cityNo == 1:
      self.photo_city1 = data
    elif cityNo == 2:
      self.photo_city2 = data

  def getCityPhoto(self, cityNo):
    """
    Returns the image data for a city.

    Parameters
    ----------
    cityNo : int
        Accepts 1 (left/origin) or 2 (right/destination).

    Returns
    -------
    PhotoImage or None
        The image if one exists, otherwise None.
    """
    if cityNo == 1:
      return self.photo_city1
    elif cityNo == 2:
      return self.photo_city2