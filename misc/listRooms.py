#Correct as of 2024-04-24.
import requests
from pprint import pprint #For pretty printing.

url = "https://game.pixelwalker.net/room/list/pixelwalker3"
#Substitute pixelwalker3 with the correct room type if different.
#Check room type using browser devtools network tab: find file called pixelwalker# where # is a number.

#Do an HTTP GET request, get the JSON response, and get the visibleRooms array from that.
visibleRooms = requests.get(url).json()["visibleRooms"]

pprint(visibleRooms)