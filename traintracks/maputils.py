import requests
import json
from bs4 import BeautifulSoup
from lxml import etree
import os
from tkintermapview import convert_address_to_coordinates

from traintracks.route import Route

def amtrakAddressRequest(stationCode):
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

def getCoords(code) -> list:
  address = amtrakAddressRequest(code)
  try: coords = convert_address_to_coordinates(f"{address[0].strip()}, {address[1].strip()}")
  except (TypeError, IndexError):
    coords = None
    print(f"Could not find coordinates for station {code}: {address}")
  if coords == None:
    try:
      coords = convert_address_to_coordinates(f"{address[1]}, United States")
    except IndexError:
      coords = None
      print(f"Could not find coordinates for station {code}: {address}")
  return coords

def _coordinatesRequest(address):
  # Make a request to API
  # Parse the JSON
  # Return lat/lon
  data = f"locate={address}, United States&region=US&geoit=JSON&strictmode=1"
  print(address)
  response = requests.get("https://geocode.xyz", data=data)
  print(data)
  try:
    apiJsonData = response.json()
    try:
      return [apiJsonData["latt"], apiJsonData["longt"]]
    except:
      return None
  except json.JSONDecodeError: return None

def _loadAllRoutes() -> dict:
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