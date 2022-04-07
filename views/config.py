import os

APP_NAME = "Amtrak Rail Planner"
SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
IMAGE_DIMENSIONS = [300,225]
if os.name == 'nt':
  SYSTEM_FONT = "Segoe UI"
  GEOMETRY = "650x875+50+50"
  MINSIZE = [635, 730]
  BACKGROUND = "SystemButtonFace"
  WIDTH_DIV = 1
elif os.name == 'posix':
  SYSTEM_FONT = "TkDefaultFont"
  GEOMETRY = "700x680+0+0"
  MINSIZE = [700, 680]
  BACKGROUND = "gray93"
  WIDTH_DIV = 1.5