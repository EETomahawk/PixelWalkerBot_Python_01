#Python 3.10

#Summary:
# Download https://pixelwalker.net/game.html.
# Parse HTML to find game JS file URL and download the JS.
# Search for game version in JS. If no update since last script execution, terminate script.
# Regex search JS for /assets/tile_atlas-######.png to get name of tilemap containing all blocks.
# Download tilemap png.
# Parse the JSON array of tilemap blocks to get the block names and locations in tilemap.
# Use this to extract the PNG of each block from the tilemap, along with its "filename".
# Get the dictionary in the initBlocks() function which lists blocks in block ID order.
# All real block names have forward slashes, else they are block pack names.
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
import json
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
    logging.fatal(f"Failed to update block list for {currentGameVersion}.") #Log note to file.
  else: logging.fatal(f"Failed to update block list.") #Log note to file.
  logging.shutdown() #Flush logs before terminating.
  exit(-1) #Terminate.
sys.excepthook = handle_exception #Call this method for any unhandled exception.

gameURL = "https://client.pixelwalker.net"
gameHTML = requests.get(f"{gameURL}/game.html").text #Download page HTML.

#Game client JS file has format "game-cwptkMuL.js". Find this random string in the HTML using regex.
#Find substring between "/assets/game-" and '.js"'.
clientJSID = re.search(r'(?<="/assets/game-)[^.]+(?=\.js")', gameHTML).group()
jsURL = f"{gameURL}/assets/game-{clientJSID}.js" #Build URL to JS file.
gameJS = requests.get(jsURL).text #Get JS file contents.
gameJS = re.sub(r'\s+', "", gameJS) #Remove all whitespace.

#Get game version from JS. String in double quotes before pixelwalker_YYYY_MM_DD room type.
currentGameVersion = re.search(r'"[^\"]+"[^\"]+(?="pixelwalker_202\d_\d\d_\d\d")', gameJS).group().split('"')[1]
with open("./lastVersionGenerated.txt", "r", encoding="utf-8") as file:
    lastVersionGenerated = file.read()
if currentGameVersion == lastVersionGenerated:
    print("Game version unchanged. Terminating.")
    exit(0)
else: #Delete all PNGs in ./images.
    for f in glob("./images/*.png"): remove(f)

#PNG containing all blocks has similar naming format to JS file. Find it in the JS.
#Find substring between "/assets/tile_atlas-" and '.png"'
tilesetID = re.search(r'(?<="/assets/tile_atlas-)[^.]+(?=\.png")', gameJS).group()
tilesetURL = f"{gameURL}/assets/tile_atlas-{tilesetID}.png" #Build URL to PNG containing all blocks.
tilesetPNG = Image.open(BytesIO(requests.get(tilesetURL).content)) #Download and open PNG.

#Find JSON array containing filename:"background/basic/black"
#This lists all the blocks in the tileset PNG and their names.
tilesetJSArray = gameJS[gameJS.split('{"filename":"background/basic/black"')[0].rfind("["):].split("]",1)[0]
tilesetData = json.loads(tilesetJSArray + "]") #Convert JSON array to Python dict.

tiles = {} #name: Image

#Parse the tileset info dict to extract each block image from the tileset PNG.
for rawTile in tilesetData:
    name = rawTile["filename"] #Get block name.
    #Get x and y coordinates of top-left corner of tile within tileset PNG.
    x = rawTile["frame"]["x"]
    y = rawTile["frame"]["y"]
    #Assume all tiles are 16x16.
    #Portals, coins, water, fire etc. are composed of multiple 16x16 tiles because they're animated,
    #so just use the first 16x16 tile of that section for the block image.
    tiles[name] = tilesetPNG.crop((x, y, x+16, y+16)) #Extract PNG and add to dict with block name.


#Retrieve the initBlocks(){...} function contents. Fragile.
initBlocks = re.search(r"(?<=initBlocks\(\){)[^}]+(?=})", gameJS).group()

#Get every block pack name (string starting with a capital letter). (?<=")[A-Z][^"]*
#Also get every block name (string containing a forward slash). (?<=")[^"]+/[^"]+
rawNames = re.findall('(?<=")[A-Z][^"]*|(?<=")[^"]+/[^"]+', initBlocks)

blocksAndPacks = [] #List containing either pack name (str) or Tuple(blockID, blockName, fileName)
blockID = 0
for name in rawNames:
    if "/" in name: #Block name.
      #Tidy up block name.
      blockName = name.replace("/", "_")
      fileName = f"{blockID}_{blockName}.png"
      blocksAndPacks.append((blockID, blockName, fileName)) #Append block info tuple to list.
      tiles[name].save(f"./images/{fileName}") #Save block as PNG to ./images/ dir.
      blockID += 1
    else: #Block pack name.
      #All whitespace was stripped at beginning of code, so re-insert this.
      #e.g. "InvisibleGravity" -> Invisible Gravity".
      name = re.sub(r"(\w)([A-Z])", r"\1 \2", name)
      blocksAndPacks.append(name)


timestamp = str(datetime.utcnow())[:-7] + " UTC"
#Start of markdown file.
s = f"`Generated at {timestamp} using game client version {currentGameVersion}.`\n"
s += "## Block IDs:\n"
s += "**WARNING:** This list is automatically generated and may have errors. "
s += "It may also be out of date, so check whether the game version above "
s += "matches the client version on pixelwalker.net  \n"
s += "**NOTE**: The block names below do not exactly match the names in https://game.pixelwalker.net/mappings\n\n"
s += "|Image|ID|Name|\n|---|---|---|\n" #Table header.

with open("blockList.md", "w", encoding="utf-8") as file: #Overwrite existing README file.
    file.write(s)
    for item in blocksAndPacks:
        if type(item) is str: #Block pack.
          file.write(f"|||**{item}**|\n")
        elif type(item) is tuple: #Block.
          blockID, blockName, fileName = item
          path = "./images/" + fileName #Relative path to image.
          file.write(f"|![{fileName}]({path})|{blockID}|{blockName}|\n")
with open("./lastVersionGenerated.txt", "w", encoding="utf-8") as file: #Keep record of latest game version.
    file.write(currentGameVersion)

logging.info(f"Generated block list for {currentGameVersion}.")
print(f"Generated block list for {currentGameVersion}.")
