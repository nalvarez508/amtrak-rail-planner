import requests
import json
from bs4 import BeautifulSoup

class Stations:
  """
  A class to represent all Amtrak stations.

  Attributes
  ----------
  stations : dict
      Dictionary of all Amtrak stations, with display name as key, and elements: Code, Name, City, State.

  Methods
  -------
  returnStationKeys()
      Returns a list of 'Code | Name, State' strings.
  returnCityState(key)
      Returns a 'City, State' string from a key.
  returnStationNameAndState(key)
      Returns a 'Station name, State' string from a key.
  getStationCode(key)
      Returns an Amtrak station code from a key.
  """
  def __init__(self):
    self.stations = dict()
    self.__getAmtrakStations()
  
  def __getAmtrakStations(self):
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
        self.stations[f"{name}, {state} ({code})"] = {"Code":code, "Name":name, "City":city, "State":state}

  def returnStationKeys(self):
    """
    Returns a list of stations in the form 'Name, State (Code)' for use in a Combobox.
    
    Returns
    -------
    list[str]
        List of all Amtrak-defined station codes
    """
    return list(self.stations.keys())
  
  def returnCityState(self, key):
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
  
  def returnStationNameAndState(self, key):
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
  
  def getStationCode(self, key):
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

  def __test_writeToFile(self):
    with open("Stations.json", "w") as f:
      f.write(json.dumps(self.stations, indent=4))