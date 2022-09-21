import json

class RouteCollection:
  """
  An ephemeral class that holds a collection of routes.

  Attributes
  ----------
  routeGroup : dict
      Stores all Route objects.
  tupCoords : list
      Holds tuples of coordinates for the route path.
  stops : dict
      Holds all stations for each combined route.
  
  Methods
  -------
  combineJourneyRoutes(segments)
      Given multiple Train objects in list form, combine routes.
  combineRoutesHelper(names)
      Given a dict of Train(s) data, combine the routes.
  """
  def __init__(self, coll: dict) -> None:
    """
    Initializes the class.

    Parameters
    ----------
    coll : dict
        All available routes.
    """
    self.routeGroup = coll
    self.tupCoords = []
    self.stops = {}
  
  def combineJourneyRoutes(self, segments: list) -> None:
    """
    Loads variables with coordinates from multiple segments.

    Parameters
    ----------
    segments : list
        List of Train objects.
    """
    _ephemRouteCoords = []
    _ephemRouteStops = {}
    for train in segments:
      _coords, _stops = self._combineRoutes(train)
      _ephemRouteCoords.extend(_coords)
      _ephemRouteStops.update(_stops)
    
    self.tupCoords = _ephemRouteCoords
    self.stops = _ephemRouteStops
  
  def combineRoutesHelper(self, names: dict) -> None:
    """
    Public facing helper function to start route combinations.

    Parameters
    ----------
    names : dict
        Routes to combine.
    """
    self.tupCoords, self.stops = self._combineRoutes(names)

  def _combineRoutes(self, names: dict) -> list:
    """
    Combines routes from a dict into variables for path coordinates and stops.
    """
    _ephemRouteCoords = []
    _ephemRouteStops = {}
    for name in names:
      _this = names[name]["Name"]
      if names[name]["Type"].upper() == "TRAIN":
        try:
          _ephemRouteCoords.extend(self.routeGroup[_this].tupCoords)
          _ephemRouteStops.update(self.routeGroup[_this].stops)
        except KeyError:
          pass
    
    return [_ephemRouteCoords, _ephemRouteStops]


class Route:
  """Class created to hold route geojson data."""
  def __init__(self, name: str, data: dict) -> None:
    """
    Initializes the route object.

    Parameters
    ----------
    name : str
        Train that runs this route.
    data : dict
        Geojson data for routes.
    """
    self.name = name

    self.tupCoords = []
    self.stops = {}

    # Path coordinates
    for toplevelItem in data["features"][0]["geometry"]["coordinates"]:
      _temp = []
      for item in toplevelItem:
        _temp.append((item[1], item[0]))
      self.tupCoords.append(_temp)
    
    # Station information
    for item in data["features"][0]["properties"]["route_stops"]:
      _thisCoords = (item["stop"]["geometry"]["coordinates"][1], item["stop"]["geometry"]["coordinates"][0])
      self.stops[item["stop"]["stop_id"]] = {
        "Name": item["stop"]["stop_name"].replace("Amtrak Station", "").replace("Amtrak", "").strip(),
        "Lat": _thisCoords[0],
        "Long": _thisCoords[1]}