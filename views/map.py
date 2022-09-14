import tkinter as tk
from attr import Attribute
import railmapview as mapview

import os
import requests
from bs4 import BeautifulSoup
from lxml import etree
from traintracks.route import RouteCollection

from views.config import ICON

from traintracks.maputils import getCoords, amtrakAddressRequest

class Map(tk.Toplevel):
  def __init__(self, parent, *args, **kwargs):
    tk.Toplevel.__init__(self, parent, *args, **kwargs)
    self.parent = parent
    self.geometry('900x500')
    self.title('Journey View')
    if os.name == 'nt': self.iconbitmap(ICON)
    
    self.originMarker = None
    self.destinationMarker = None
    self.travelPath = None
    self.currentRoute = None
    self.currentStops = None
    self.subsidiaryStopMarkers = []
    self.subsidiaryPaths = []

    self.map = mapview.TkinterMapView(self, width=700, height=500)

    self.map.pack(fill=tk.BOTH, expand=True)
    self.updateOrigin()
    self.updateDestination()
    self.map.set_zoom(4)

    self.wm_protocol("WM_DELETE_WINDOW", self.__onClose)

  def __rapidDelete(self, obj):
    if obj != []:
      for widget in obj:
        self.map.delete(widget)
      obj.clear()

  def __onClose(self):
    self.parent.closeMap()
    self.destroy()

  def __getCoords(self, name) -> tuple:
    code = self.parent.stationsArea.stations.getStationCode(name)
    address = self._amtrakAddressRequest(code)
    try: coords = mapview.convert_address_to_coordinates(f"{address[0].strip()}, {address[1].strip()}")
    except TypeError: coords = None
    if coords == None:
      coords = mapview.convert_address_to_coordinates(f"{address[1]}, United States")
    return coords

  def updateOrigin(self):
    name = self.parent.us.getOrigin()
    _code = self.parent.stationsArea.stations.getStationCode(name)
    coords = getCoords(_code)
    if coords != None:
      try: self.originMarker.delete()
      except AttributeError as e: print(e) # Object does not exist yet
      self.originMarker = self.map.set_marker(coords[0], coords[1], text=name)
    self.__updatePath()
    self.update()
  
  def updateDestination(self):
    name = self.parent.us.getDestination()
    _code = self.parent.stationsArea.stations.getStationCode(name)
    coords = getCoords(_code)
    if coords != None:
      try: self.destinationMarker.delete()
      except AttributeError as e: print(e) # Object does not exist yet
      self.destinationMarker = self.map.set_marker(coords[0], coords[1], text=name)
    self.__updatePath()
    self.update()

  def __updatePath(self):
    try: self.travelPath.delete()
    except AttributeError: pass # Object does not exist yet
    self.__rapidDelete(self.subsidiaryPaths)
    self.__rapidDelete(self.subsidiaryStopMarkers)
    self.subsidiaryStopMarkers, self.subsidiaryPaths = [[], []]
    try:
      self.travelPath = self.map.set_path([self.originMarker.position, self.destinationMarker.position])
      latt = []
      longt = []
      for l in [self.originMarker.position, self.destinationMarker.position]:
        latt.append(l[0])
        longt.append(l[1])
      centerLatt = sum(latt)/2.
      centerLongt = sum(longt)/2.
      self.map.set_zoom(4)
      self.map.set_position(centerLatt, centerLongt)
    except AttributeError: pass # A marker does not have a position yet

  def updateMarker(self, side):
    if side==1: self.updateOrigin()
    elif side==2: self.updateDestination()
  
  def drawTrainRoute(self, name, stops):
    if type(name) == str:
      _curr = self.parent.routes[name]
    elif type(name) == list:
      _curr = RouteCollection(self.parent.routes)
      _curr.combineRoutes(name)
    self.map.delete(self.travelPath)
    self.map.delete(self.originMarker)
    self.map.delete(self.destinationMarker)
    if self.currentRoute != name:
      self.__rapidDelete(self.subsidiaryPaths)
      for coll in _curr.tupCoords:
        self.subsidiaryPaths.append(self.map.set_path(coll, color='black'))
      self.currentRoute = name

      #_myStopsMarker = []
      self.__rapidDelete(self.subsidiaryStopMarkers)
      for item in _curr.stops:
        _this = _curr.stops[item]
        if item not in stops:
          self.subsidiaryStopMarkers.append(self.map.set_marker(_this["Lat"],
                              _this["Long"],
                              text=item,
                              marker_color_outside='',
                              marker_color_circle='orange',
                              font='Helvetica 12 bold'))
        elif item in stops:
          #_myStopsMarker.append([_this["Lat"], _this["Long"], item, 'red', 'red', 'Helvetica 18 bold', 'blue'])
          self.subsidiaryStopMarkers.append(self.map.set_marker(_this["Lat"],
                              _this["Long"],
                              text=_this["Name"],
                              marker_color_outside='red',
                              marker_color_circle='red',
                              font='Helvetica 18 bold', text_color='blue'))
      self.currentStops = sorted(stops)
    self.update()

  def _amtrakAddressRequest(self, stationCode) -> list:
    # Find station page
    # Parse for address
    try:
      webinfo = requests.get(f"https://www.amtrak.com/stations/{stationCode.lower()}")
      soup = BeautifulSoup(webinfo.content, "html.parser")
      dom = etree.HTML(str(soup))
      try:
        addr1 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[0].text
        addr2 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[2].text
      except IndexError:
        addr2 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[1].text
      return [addr1, addr2]
    except:
      return None