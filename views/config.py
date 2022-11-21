import os

APP_NAME = "USA Rail Planner"
APP_VERSION = "0.9.5"
SEARCH_URL = "https://www.amtrak.com/tickets/departure.html"
IMAGE_DIMENSIONS = [300,225]
DEV_MODE = True
if os.name == 'nt':
  SYSTEM_FONT = "Segoe UI"
  GEOMETRY = "700x875+50+50"
  MINSIZE = [745, 730]
  BACKGROUND = "SystemButtonFace"
  WIDTH_DIV = 1
  ICON = "tracks.ico"
elif os.name == 'posix':
  SYSTEM_FONT = "TkDefaultFont"
  GEOMETRY = "750x680+0+0"
  MINSIZE = [795, 680]
  BACKGROUND = "gray93"
  WIDTH_DIV = 1.5
  ICON = "tracks.icns"