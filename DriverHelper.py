import requests
import json
from bs4 import BeautifulSoup

import PIL.Image, PIL.ImageTk, PIL.ImageFile
from io import BytesIO
import base64, gc
from datetime import datetime, date
import sys
import requests
from threading import Thread
from threading import Event as ev
import time
import urllib.parse
import urllib.request
from tkinter import TclError
from fractions import Fraction

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from HelperClasses import Driver

class ImageSearch:
  def __init__(self):
    self.driver = Driver().driver
    PIL.ImageFile.LOAD_TRUNCATED_IMAGES = True

    self.photo_city1 = None
    self.photo_city2 = None

  def returnCityPhoto(self, c): #c=city
    URL = f"https://www.google.com/search?tbm=isch&q={urllib.parse.quote(c)}"
    self.driver.get(URL)
    image = WebDriverWait(self.driver,5).until(EC.presence_of_element_located((By.XPATH, "//img[@class='rg_i Q4LuWd']")))

    def checkIfB64(src):
      header = src.split(',')[0]
      if header.startswith('data') and ';base64' in header:
        imgType = header.replace('data:image/', '').replace(';base64', '')
        return imgType
      return None
    
    def getHiDef():
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
      if image.size > tuple(size): # don't stretch smaller images
        image.thumbnail(size, PIL.Image.ANTIALIAS)
      return image
    
    try:
      onlineImage = self.returnCityPhoto(c)
      if onlineImage[0] == "B64":
        onlineImage[1] = (base64.b64decode(onlineImage[1]))
      fh = BytesIO(onlineImage[1])
      img = PIL.Image.open(fh, mode='r')
      img = crop_resize(img)
      img.thumbnail((dims), PIL.Image.ANTIALIAS)
      render = PIL.ImageTk.PhotoImage(image=img)
      self.setCityPhoto(no, render)
      print(img.size)
    except TclError:
      pass

  def setCityPhoto(self, cityNo, data):
    if cityNo == 1:
      self.photo_city1 = data
    elif cityNo == 2:
      self.photo_city2 = data

  def getCityPhoto(self, cityNo):
    if cityNo == 1:
      return self.photo_city1
    elif cityNo == 2:
      return self.photo_city2
    
if __name__ == "__main__":
  ImageSearch()