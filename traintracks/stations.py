import requests
import json
from bs4 import BeautifulSoup

from traintracks.maputils import amtrakAddressRequest

class Stations:
  """
  A class to represent all Amtrak stations.

  Attributes
  ----------
  stations : dict
      Dictionary of all Amtrak stations, with display name as key, and elements: Code, Name, City, State.

  Methods
  -------
  returnStationData(key)
      Returns dictionary object for a station.
  returnStationKeys()
      Returns a list of 'Code | Name, State' strings.
  returnCityState(key)
      Returns a 'City, State' string from a key.
  returnStationNameAndState(key)
      Returns a 'Station name, State' string from a key.
  getStationCode(key)
      Returns an Amtrak station code from a key.
  returnCityStateFromCode(code)
      Returns 'City, State' string from a station code.
  returnKeyByCode(code)
      Returns a 'Name, State (Code)' string from a station code.
  """
  def __init__(self) -> None:
    self.stations = dict()
    self.__getAmtrakStations()
  
  def __getAmtrakStations(self) -> None:
    """
    Populates the Station object's active Amtrak station dictionary from a Wikipedia list.
    
    Notes
    -----
    Pulled from `Wikipedia <https://en.wikipedia.org/wiki/List_of_Amtrak_stations>`.
    """
    wiki = requests.get("https://en.wikipedia.org/wiki/List_of_Amtrak_stations").text
    soup = BeautifulSoup(wiki, 'xml')
    table = soup.find('table', {'class': 'wikitable collapsible sortable'})
    table_rows = table.find_all('tr')

    for row in table_rows:
      rowData = row.find_all('td')
      if len(rowData) > 0:
        name = rowData[0].text.strip().replace("\u2013","-") # Amtrak-defined station name
        code = rowData[1].text.strip() # Amtrak-defined station code
        city = rowData[2].text.strip() # City where the station is located
        state = rowData[3].text.strip() # State, as an abbreviation

        routes = []
        _locals = []
        try:
          for route in rowData[4].find_all('a'):
            routes.append(route.text) # Amtrak connections
          for _local in rowData[7].find_all('a'):
            if _local.text != '':
              _locals.append(_local.text) # Local connections (train/lightrail)
        except IndexError:
          pass # Wikipedia formatting issue
        self.stations[f"{name}, {state} ({code})"] = {"Code":code, "Name":name, "City":city, "State":state, "Served By":routes, "Local Transfers":_locals}

  def returnStationData(self, key: str) -> dict:
    """
    Returns the dictionary object associated with each station.

    Parameters
    ----------
    key : str
        City, State (Code)

    Returns
    -------
    dict
        Station information.
    """
    _this = self.stations[key]
    addr = amtrakAddressRequest(_this['Code'])
    try:
      _this['Address'] = addr
    except KeyError:
      pass
    return _this

  def returnStationKeys(self) -> list[str]:
    """
    Returns a list of stations in the form 'Name, State (Code)' for use in a Combobox.
    
    Returns
    -------
    list[str]
        List of all Amtrak-defined station codes
    """
    return list(self.stations.keys())
  
  def returnCityState(self, key: str) -> str:
    """
    Returns a city-state string for a friendly display of location, regardless of station name. Used for image searches.

    Parameters
    ----------
    key : str
        a 'Name, State (Code)' string

    Returns
    -------
    str
        'City, State'
    """
    return f"{self.stations[key]['City']}, {self.stations[key]['State']}"
  
  def returnStationNameAndState(self, key: str) -> str:
    """
    Returns the station name and state to provide context to location, regardless of station name. Used for results header.
    
    Parameters
    ----------
    key : str
        a 'Name, State (Code)' string
    
    Returns
    -------
    str
        'Station name, State'
    """
    return f"{self.stations[key]['Name']}, {self.stations[key]['State']}"
  
  def getStationCode(self, key: str) -> str:
    """
    Returns the Amtrak-defined station code.

    Parameters
    ----------
    key : str
        a 'Name, State (Code)' string
    Returns
    -------
    str
        an Amtrak station code
    """
    return self.stations[key]["Code"]
  
  def _keyFinder(self, code: str) -> str:
    for name in self.stations:
      if code == self.stations[name]["Code"]:
        return name
  
  def returnCityStateByCode(self, code: str) -> str:
    """
    Returns a 'City, State' string from a station code.

    Parameters
    ----------
    code : str
        Amtrak station code, three letters.

    Returns
    -------
    str
        'City, State'
    """
    return self.returnCityState(self._keyFinder(code))

  def __test_writeToFile(self):
    with open("Stations.json", "w") as f:
      f.write(json.dumps(self.stations, indent=4))
  
  def returnKeyByCode(self, code: str) -> str:
    """
    Returns the friendly name for a station.

    Parameters
    ----------
    code : str
        Amtrak station code

    Returns
    -------
    str
        'Name, State (Code)'
    """
    return self._keyFinder(code)

if __name__ == "__main__":
  x = Stations()
  print(x.returnStationData('Washington Union, DC (WAS)'))