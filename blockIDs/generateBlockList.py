#Python 3.10

#Summary:
# Download https://pixelwalker.net/game.html.
# Parse HTML to find game JS file URL and download the JS.
# Search for game version in JS. If no update since last script execution, terminate script.
# Regex search JS for /assets/tile_atlas-######.png to get name of tilemap containing all blocks.
# Download tilemap png.
# Parse the JS array of tilemap blocks to get the block names and locations in tilemap.
# Use this to extract the PNG of each block from the tilemap, along with its "filename".
# Get the dictionary in the initBlocks() function which lists blocks in block ID order.
# All(?) real blocks have forward slashes, else they are block pack names.
# The block names exactly match the tilemap block names.
# Save all the block PNGs to ./images
# Build a README table with the embedded block images, names and IDs.

#TODO: decode JS initSmileys() to get smileys as well.

import logging
from traceback import format_exception
import sys
import requests #requests==2.31.0
import re
from glob import glob
from os import remove
from io import BytesIO
from PIL import Image #pillow==10.3.0
from difflib import get_close_matches
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(filename="./generateBlockList.log", #Logging to file.
                    filemode='a',
                    encoding="utf-8",
                    format='%(asctime)s UTC | %(levelname)s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO)

def handle_exception(exc_type, exc_value, exc_traceback):
  error = "".join(format_exception(exc_type, exc_value, exc_traceback)) #Format exception as str.
  print(error)
  if "currentGameVersion" in globals(): #If variable currentGameVersion is defined.
    logging.fatal(f"Failed to update block list for v{currentGameVersion}.") #Log note to file.
  else: logging.fatal(f"Failed to update block list.") #Log note to file.
  logging.shutdown() #Flush logs before terminating.
  exit(-1) #Terminate.
sys.excepthook = handle_exception #Call this method for any unhandled exception.

gameURL = "https://pixelwalker.net"
gameHTML = requests.get(f"{gameURL}/game.html").text #Download page HTML.

#Game client JS file has format "game-cwptkMuL.js". Find this random string in the HTML using regex.
#Find substring between "/assets/game-" and '.js"'.
clientJSID = re.search('(?<="/assets/game-)[^.]+(?=\.js")', gameHTML).group()
jsURL = f"{gameURL}/assets/game-{clientJSID}.js" #Build URL to JS file.
gameJS = requests.get(jsURL).text #Get JS file contents.
gameJS = re.sub("\s+", "", gameJS) #Remove all whitespace to make regex searching consistent.

#Get game version from JS. String in double quotes before pixelwalker_YYYY_MM_DD room type.
currentGameVersion = re.search('"[^\"]+"[^\"]+(?="pixelwalker_202\d_\d\d_\d\d")', gameJS).group().split('"')[1]
with open("./lastVersionGenerated.txt", "r", encoding="utf-8") as file:
    lastVersionGenerated = file.read()
if currentGameVersion == lastVersionGenerated:
    print("Game version unchanged. Terminating.")
    exit(0)
else: #Delete all PNGs in ./images.
    for f in glob("./images/*.png"): remove(f)

#PNG containing all blocks has similar naming format to JS file. Find it in the JS.
#Find substring between "/assets/tile_atlas-" and '.png"'
tilesetID = re.search('(?<="/assets/tile_atlas-)[^.]+(?=\.png")', gameJS).group()
tilesetURL = f"{gameURL}/assets/tile_atlas-{tilesetID}.png" #Build URL to PNG containing all blocks.
tilesetPNG = Image.open(BytesIO(requests.get(tilesetURL).content)) #Download and open PNG.

#Find JS array [] containing filename:"background/basic/black"
#This lists all the blocks in the tileset PNG and their names.
tilesetJSArray = gameJS[gameJS.split('filename:"background/basic/black"')[0].rfind("["):].split("]",1)[0]

tiles = {} #name: Image

#Split JS array of tileset blocks apart using the block name and iterate it.
for rawTile in tilesetJSArray.split("filename:")[1:]:
    name = re.search('(?<=")[^"]+(?=")', rawTile).group() #Get name of tile - e.g. "foreground/switches/local_switch"
    frame = re.search("(?<=frame:{)[^}]+(?=})", rawTile).group() #Get tile info - e.g. "x:0,y:0,w:16,h:16"
    #x and y are top left coordinate of tile in PNG. w and h are its width and height (probably always 16x16).
    #Assume x and then y always appear first and extract them.
    #Ignore w and h. Portals, coins, water, fire etc. are composed of multiple 16x16 tiles because they're animated,
    #so just use the first 16x16 tile of that section for the block image.
    x, y, _, _ = [int(v.split(":")[1]) for v in frame.split(",")]
    tiles[name] = tilesetPNG.crop((x, y, x+16, y+16))


#Retrieve the JS object of block names from the initBlocks() function.
#Find substring between { and } AFTER initBlocks(){
blockObject = re.search("(?<={)[^}]+", gameJS.split("initBlocks(){")[1]).group()
#Get a list of the strings in the object. These are the package and block names.
blockList = re.findall('"(.*?)"', blockObject)

blocks = [] #List with either package name (str) or Tuple(blockID, blockName, fileName)
bID = 0
for item in blockList:
    if "/" not in item: #String is name of block pack.
        continue
        #blocks.append(item)
    else: #String is block name.
        #Tidy up block name.
        #blockName = item.replace("extra/","").replace("foreground/","").replace("background/","")
        blockName = item.replace("/", "_")
        fileName = f"{bID}_{blockName}.png"
        blocks.append((bID, blockName, fileName)) #Append block info tuple to list.
        tiles[item].save(f"./images/{fileName}") #Save block as PNG to ./images/ dir.
        bID += 1


timestamp = str(datetime.utcnow())[:-7] + " UTC"
#Start of markdown file.
s = f"`Generated at {timestamp} using game client version {currentGameVersion}.`\n"
s += "## Block IDs:\n"
s += "**WARNING:** This list is automatically generated and may have errors. "
s += "Double-check whether the game version above matches the client version "
s += "on pixelwalker.net\n\n"
#s += "|Package|Image|ID|Name|\n|---|---|---|\n" #Table header.
s += "|Image|ID|Name|\n|---|---|---|\n" #Table header.

with(open("./README.md", "w", encoding="utf-8") as file): #Overwrite existimng README file.
    file.write(s)
    for item in blocks:
        # if type(item) is str:
        #     pass
        # else:
        blockID, blockName, fileName = item
        path = "./images/" + fileName #Relative path to image.
        file.write(f"|![{fileName}]({path})|{blockID}|{blockName}|\n")

with open("./lastVersionGenerated.txt", "w", encoding="utf-8") as file: #Keep record of latest game version.
    file.write(currentGameVersion)

logging.info(f"Generated block list for {currentGameVersion}.")
print(f"Generated block list for {currentGameVersion}.")
