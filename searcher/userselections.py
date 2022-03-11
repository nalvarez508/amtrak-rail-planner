import datetime
import sys

#sys.path.append("../")
from traintracks.train import RailPass

class UserSelections:
  def __init__(self):
    self.origin = None
    self.destination = None
    self.departDate = datetime.date.today()

    self.userSelections = RailPass()
  
  def getPrettyDate(self):
    def getSuffix():
      if (self.departDate.day <= 3) or (self.departDate.day > 20):
        day = self.departDate.day % 10
        if day == 1: suffix = "st"
        elif day == 2: suffix = "nd"
        elif day == 3: suffix = "rd"
        else: suffix = "th"
      else:
        suffix = "th"
      return suffix
    def dayCheck():
      if self.departDate.day < 10: return self.departDate.day
      else: return "%d"
    return datetime.datetime.strftime(self.departDate, f"%A, %b. {dayCheck()}{getSuffix()}, %Y")

  def getDate(self):
    return self.departDate
  
  def getSearchDate(self):
    return datetime.datetime.strftime(self.departDate, "%m/%d/%Y")
  
  def setDate(self, d):
    self.departDate = d
  
  def incrementDate(self, i):
    self.departDate += datetime.timedelta(days=i)

  def set(self, city, side):
    if side == 1:
      self.setOrigin(city)
    elif side == 2:
      self.setDestination(city)

  def setOrigin(self, o):
    self.origin = o
  def getOrigin(self):
    return self.origin
  
  def setDestination(self, d):
    self.destination = d
  def getDestination(self):
    return self.destination
  
  def addSegment(self, t):
    self.userSelections.createSegment(t)