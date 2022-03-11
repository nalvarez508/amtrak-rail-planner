import requests
import json
from bs4 import BeautifulSoup

class Stations:
  def __init__(self):
    self.stations = dict()
    self.getAmtrakStations()
    #self._test_writeToFile()
  
  def getAmtrakStations(self):
    wiki = requests.get("https://en.wikipedia.org/wiki/List_of_Amtrak_stations").text
    soup = BeautifulSoup(wiki, 'xml')
    table = soup.find('table', {'class': 'wikitable collapsible sortable'})
    table_rows = table.find_all('tr')

    for row in table_rows:
      rowData = row.find_all('td')
      if len(rowData) > 0:
        name = rowData[0].text.strip().replace("\u2013","-")
        code = rowData[1].text.strip()
        city = rowData[2].text.strip()
        state = rowData[3].text.strip()
        self.stations[f"{code} | {name}, {state}"] = {"Code":code, "Name":name, "City":city, "State":state}

  def returnStationKeys(self):
    return list(self.stations.keys())
  
  def returnCityState(self, key):
    return f"{self.stations[key]['City']}, {self.stations[key]['State']}"
  
  def returnStationNameAndState(self, key):
    return f"{self.stations[key]['Name']}, {self.stations[key]['State']}"
  
  def getStationCode(self, key):
    return self.stations[key]["Code"]

  def _test_writeToFile(self):
    with open("Stations.json", "w") as f:
      f.write(json.dumps(self.stations, indent=4))