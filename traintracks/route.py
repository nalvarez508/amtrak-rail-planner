import json

class RouteCollection:
  def __init__(self, coll):
    self.routeGroup = coll
    self.tupCoords = []
    self.stops = {}
  
  def combineRoutes(self, names: dict):
    _ephemRouteCoords = []
    _ephemRouteStops = {}
    for name in names:
      _this = names[name]["Name"]
      if names[name]["Type"].upper() == "TRAIN":
        _ephemRouteCoords.extend(self.routeGroup[_this].tupCoords)
        _ephemRouteStops.update(self.routeGroup[_this].stops)
    
    self.tupCoords = _ephemRouteCoords
    self.stops = _ephemRouteStops


class Route:
  def __init__(self, name: str, data: dict):
    self.name = name

    self.tupCoords = []
    self.stops = {}
    for toplevelItem in data["features"][0]["geometry"]["coordinates"]:
      _temp = []
      for item in toplevelItem:
        _temp.append((item[1], item[0]))
      self.tupCoords.append(_temp)
    
    for item in data["features"][0]["properties"]["route_stops"]:
      _thisCoords = (item["stop"]["geometry"]["coordinates"][1], item["stop"]["geometry"]["coordinates"][0])
      self.stops[item["stop"]["stop_id"]] = {
        "Name": item["stop"]["stop_name"].replace("Amtrak Station", "").replace("Amtrak", "").strip(),
        "Lat": _thisCoords[0],
        "Long": _thisCoords[1]}