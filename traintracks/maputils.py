import requests
import json
from bs4 import BeautifulSoup
from lxml import etree
import os
from tkintermapview import convert_address_to_coordinates

from traintracks.route import Route

def amtrakAddressRequest(stationCode: str) -> list[str]:
  """
  Given a station code, returns address of the station from a web request to Amtrak.

  Parameters
  ----------
  stationCode : str
      Amtrak station code (three letter string)

  Returns
  -------
  list[str]
      [Street number and name, City/State/Zip] or None if nothing was found.
  """
  # Find station page
  # Parse for address
  try:
    webinfo = requests.get(f"https://www.amtrak.com/stations/{stationCode.lower()}")
    soup = BeautifulSoup(webinfo.content, "html.parser")
    dom = etree.HTML(str(soup))
    try:
      addr1 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[0].text
      _addr2 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[2].text
    except IndexError:
      _addr2 = dom.xpath("//*[@class='hero-banner-and-info__card_block-address']")[1].text
    addr2 = _addr2.replace('  ','').replace('\r\n', ' ')
    return [addr1, addr2]
  except:
    return None

def getCoords(code: str) -> list[float]:
  """
  Finds coordinates of an Amtrak station.

  Parameters
  ----------
  code : str
      Amtrak station code, three letter string.

  Returns
  -------
  list[float]
      [Latitude, Longitude] or None.
  """
  address = amtrakAddressRequest(code)
  try: coords = convert_address_to_coordinates(f"{address[0].strip()}, {address[1].strip()}")
  except (TypeError, IndexError):
    coords = None
    print(f"Could not find coordinates for station {code}: {address}")
  if coords == None:
    try:
      _isCA = None
      canadianStates = ['ON', 'QC', 'NS', 'NB', 'MB', 'BC', 'PE', 'SK', 'AB', 'NL']
      for state in canadianStates:
        if state in address[1]:
          _isCA = state
          break

      if _isCA != None:
        address[1] = address[1].split(_isCA)[0]+_isCA
        coords = convert_address_to_coordinates(f"{address[0]}, {address[1]}, Canada")
      else:
        coords = convert_address_to_coordinates(f"{address[1]}, United States")
    except IndexError:
      coords = None
      print(f"Could not find coordinates for station {code}: {address}")
  return coords

def _loadAllRoutes() -> dict[Route]:
  """Finds the routes folder in the project directory and returns a dict of the route geojson data."""
  cwd = os.path.dirname(os.path.realpath(__file__))
  _folder = os.path.join(cwd, "routes")

  if "routes" in os.listdir(cwd):
    _folder = os.path.join(cwd, "routes")
  elif "routes" in os.listdir(os.path.dirname(cwd)):
    _folder = os.path.join(os.path.dirname(cwd), "routes")
  else: return None

  _allRoutes = {}
  for file in os.listdir(_folder):
    if file.endswith(".geojson"):
      with open(os.path.join(_folder,file), 'r') as f:
        _name = file.replace("Amtrak - ", "").replace(".geojson", "")
        _allRoutes[_name] = Route(_name, json.loads(f.read()))
  return _allRoutes

if __name__ == "__main__":
  _loadAllRoutes()