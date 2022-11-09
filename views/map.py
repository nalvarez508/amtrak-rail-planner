import tkinter as tk
import railmapview as mapview

import os

from traintracks.route import RouteCollection
from views.config import ICON
from traintracks.maputils import getCoords, amtrakAddressRequest

class Map(tk.Toplevel):
  """
  A class responsible for making a Map window.

  Parameters
  ----------
  tk : Toplevel
  
  Attributes
  ----------
  originMarker : CanvasPositionMarker
  destinationMarker : CanvasPositionMarker
  travelPath : CanvasPath
      Naive point to point path. Does not reflect actual rails.
  currentRoute : str, list, dict
      Currently displayed route on the map.
  currentStops : list[str]
      Currently displayed stops on the map.
  subsidiaryStopMarkers : list[CanvasPositionMarker]
      Intermediate stops.
  subsidiaryPaths : list[CanvasPath]
      Rail paths.
  importantStopMarkers : list[CanvasPositionMarker]
      Stopping stops (origin/destination).
  map : TkinterMapView

  Methods
  -------
  updateOrigin
  updateDestination
  updateMarker(side)
      Helper for update origin/destination.
  drawTrainRoute(name, stops)
      Draws a rail route on the map.
  """
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
    self.importantStopMarkers = []

    self.map = mapview.TkinterMapView(self, width=700, height=500)

    self.map.pack(fill=tk.BOTH, expand=True)
    self.updateOrigin()
    self.updateDestination()
    self.map.set_zoom(4)

    self.wm_protocol("WM_DELETE_WINDOW", self.__onClose)

  def __rapidDelete(self, obj: list) -> None:
    if obj != []:
      for widget in obj:
        self.map.delete(widget)
      obj.clear()

  def __onClose(self) -> None:
    self.parent.closeMap()
    self.destroy()

  def updateOrigin(self) -> None:
    name = self.parent.us.getOrigin()
    _code = self.parent.stationsArea.stations.getStationCode(name)
    coords = getCoords(_code)
    if coords != None:
      try: self.originMarker.delete()
      except AttributeError as e: print(e) # Object does not exist yet
      self.originMarker = self.map.set_marker(coords[0], coords[1], text=name)
    self.__updatePath()
    self.update()
  
  def updateDestination(self) -> None:
    name = self.parent.us.getDestination()
    _code = self.parent.stationsArea.stations.getStationCode(name)
    coords = getCoords(_code)
    if coords != None:
      try: self.destinationMarker.delete()
      except AttributeError as e: print(e) # Object does not exist yet
      self.destinationMarker = self.map.set_marker(coords[0], coords[1], text=name)
    self.__updatePath()
    self.update()

  def __updatePath(self) -> None:
    """Draws a path between the origin and destination markers."""
    try: self.travelPath.delete()
    except AttributeError: pass # Object does not exist yet
    self.__rapidDelete(self.subsidiaryPaths)
    self.__rapidDelete(self.subsidiaryStopMarkers)
    self.importantStopMarkers.clear()
    self.subsidiaryStopMarkers, self.subsidiaryPaths = [[], []]
    try:
      self.travelPath = self.map.set_path([self.originMarker.position, self.destinationMarker.position])
    except AttributeError: pass
    self.__updateView([self.originMarker, self.destinationMarker])
  
  def __updateView(self, markers) -> None:
    """Centers the map on some number of markers."""
    try:
      _thesePositions = [x.position for x in markers]
      _numCoords = float(len(_thesePositions))
      latt = []
      longt = []
      for l in _thesePositions:
        latt.append(l[0])
        longt.append(l[1])
      centerLatt = sum(latt)/_numCoords
      centerLongt = sum(longt)/_numCoords
      self.map.set_zoom(5)
      self.map.set_position(centerLatt, centerLongt)
    except AttributeError: pass # A marker does not have a position yet

  def updateMarker(self, side: int) -> None:
    """
    General update function for origin/destination markers.

    Parameters
    ----------
    side : int
        1 for origin, 2 for destination.
    """
    if self.subsidiaryPaths != []:
      self.updateOrigin()
      self.updateDestination()
    elif side == 1:
      self.updateOrigin()
    elif side == 2:
      self.updateDestination()
  
  def drawTrainRoute(self, name, stops: list) -> None:
    """
    Creates a path of the train route and adds stops.

    Parameters
    ----------
    name : str, dict, or list
        Name of route (single route), dictionary of routes (multiple routes), or list of routes (journey view).
    stops : list
        Stops to highlight on the map (origin/destinations).
    """
    areStopsShown = True
    if type(name) == str:
      _curr = self.parent.routes[name]
    elif type(name) == dict:
      _curr = RouteCollection(self.parent.routes)
      _curr.combineRoutesHelper(name)
    elif type(name) == list:
      areStopsShown = False
      _curr = RouteCollection(self.parent.routes)
      _curr.combineJourneyRoutes(name)
      _stopIndex = {}
      for index, code in enumerate(stops):
        try: _stopIndex[code].append(index+1)
        except KeyError: _stopIndex[code] = [index+1]

    self.map.delete(self.travelPath)
    self.map.delete(self.originMarker)
    self.map.delete(self.destinationMarker)
    if self.currentRoute != name:
      self.__rapidDelete(self.subsidiaryPaths)
      for coll in _curr.tupCoords:
        self.subsidiaryPaths.append(self.map.set_path(coll, color='black'))
      self.currentRoute = name

      self.__rapidDelete(self.subsidiaryStopMarkers)
      self.importantStopMarkers.clear()
      for item in _curr.stops:
        _this = _curr.stops[item]

        # Intermediate stops
        if item not in stops and areStopsShown:
          self.subsidiaryStopMarkers.append(self.map.set_marker(
            _this["Lat"],
            _this["Long"],
            text=item,
            marker_color_outside='',
            marker_color_circle='orange',
            font='Tahoma 12 bold'))

        # Origin/destination stops
        elif item in stops:
          _label = self.parent.stationsArea.stations.returnCityStateByCode(item)
          if areStopsShown == False: _label = f"{_stopIndex[item]} {_label}"
          _newImportantMarker = (self.map.set_marker(
            _this["Lat"],
            _this["Long"],
            text=_label,
            marker_color_outside='red',
            marker_color_circle='red',
            font='Tahoma 18 bold',
            text_color='blue'))
          self.subsidiaryStopMarkers.append(_newImportantMarker)
          self.importantStopMarkers.append(_newImportantMarker)

      # Any stations not in the route's stop list
      for item in stops:
        if item not in _curr.stops:
          coords = getCoords(item)
          if coords != None:
            self.subsidiaryStopMarkers.append(self.map.set_marker(
              coords[0],
              coords[1],
              text=self.parent.stationsArea.stations.returnCityStateByCode(item),
              marker_color_outside='red',
              marker_color_circle='red',
              font='Tahoma 18 bold',
              text_color='blue'))

      self.currentStops = sorted(stops)
      self.__updateView(self.importantStopMarkers)
    self.update()