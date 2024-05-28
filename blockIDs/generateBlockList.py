#Python 3.10

#Summary:
# Download https://pixelwalker.net/game.html.
# Parse HTML to find game JS link - e.g. https://pixelwalker.net/assets/game-cwptkMuL.js.
# Download game JS.
# Check if game version has changed. If not, terminate.
# Regex search JS for /assets/tile_atlas-######.png to get name of tilemap of all blocks.
# Download tilemap png.
# Parse the subsequent list after the tilemap name in the JS to get the block names and locations in tilemap.
# Use this info to pull out the PNG of each block from the tilemap, along with its "filename".
# Download https://game.pixelwalker.net/mappings JSON.
# Do some voodoo to match up the block names with the tiles' "filenames".
# Build a README markdown file with a table of blocks.
# Use GitHub Actions to run this script periodically.

exit(-1) #TESTING

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
tilesetPNG = Image.open(BytesIO(requests.get(tilesetURL).content)) #Download PNG and load it into Pillow.

#Find substring after tileset filename between square brackets.
#This is JS array of objects describing the blocks in the tileset and their names.
tilesetJSArray = re.search("(?<=\[)[^\]]+(?=])", gameJS.split(tilesetID, 1)[1]).group()
#Cannot easily convert this JS array of objects to JSON for parsing. Instead, manually parse it.

tileNames = []

#Split JS array of tileset blocks apart using the block name and iterate it.
for rawTile in tilesetJSArray.split("filename:")[1:]:
    name = re.search('(?<=")[^"]+(?=")', rawTile).group() #Get name of tile - e.g. "foreground/switches/local_switch"
    frame = re.search("(?<=frame:{)[^}]+(?=})", rawTile).group() #Get tile info - e.g. "x:0,y:0,w:16,h:16"
    #x and y are top left coordinate of tile in PNG. w and h are its width and height (probably always 16x16).
    #Assume x and then y always appear first and extract them.
    #Ignore w and h. Portals, coins, water, fire etc. are composed of multiple 16x16 tiles because they're animated,
    #so just use the first 16x16 tile of that section for the block image.
    x, y, _, _ = [int(v.split(":")[1]) for v in frame.split(",")]
    blockImage = tilesetPNG.crop((x, y, x+16, y+16))

    tileName = name.replace('/','_')

    #Manipulate the tileName a bit to improve matching.
    #Remove prefixes that don't appear in mappings JSON.
    for s in ["foreground_", "decoration_", "hazards_", "keys_",
              "coin_doors_and_gates_", "extra_", "coins_", "generic_",
              "death_", "spawn_", "liquids_", "switches_"]:
        if tileName.startswith(s): tileName = tileName.removeprefix(s)

    #Move "background_" to end of string and change to "_bg".
    if tileName.startswith("background_"): tileName = tileName[11:] + "_bg"
    #Rearrange local/global switch strings to improve matching.
    # elif tileName.startswith("switches_local"):
    #     tileName = tileName.replace("switches_local", "local_switch")
    # elif tileName.startswith("switches_global"):
    #     tileName = tileName.replace("switches_global", "global_switch")

    blockImage.save(f"./images/{tileName}.png")
    tileNames.append(tileName)

mappingsURL = "https://game.pixelwalker.net/mappings"
mappings = requests.get(mappingsURL).json() #Download mappings JSON. Convert to dict.

blockList = {}
#Do multiple passes at decreasing confidence levels to match up the strings.
#Eliminate each matched pair to improve subsequent matches/iterations.
cutoff = [1, 0.9, 0.8, 0.7, 0.5, 0]
for n in cutoff:
    for blockName, blockID in mappings.copy().items():
        matches = get_close_matches(blockName, tileNames, n=1, cutoff=n)
        if matches: #Non-empty list - i.e. match found at confidence above this cutoff.
            tileName = matches[0]
            blockList[blockID] = {
                "blockName": blockName,
                "imageName": tileName }
            #Remove match from both collections, since we're doing multiple passes.
            tileNames.remove(tileName)
            del mappings[blockName]

    #For debugging:
#=============================================================================================
#    if len(cutoff) > 1 and n == cutoff[-2]: blockList.clear()
# print(f"{len(blockList)}/{len(mappings)+len(blockList)} matched. {len(mappings)} remaining.")
#
# with open("./mappings.txt", "w", encoding="utf-8") as file:
#     file.writelines("\n".join(mappings))
# with open("./tileset.txt", "w", encoding="utf-8") as file:
#     file.writelines("\n".join(tileNames))
#=============================================================================================

timestamp = str(datetime.utcnow())[:-7] + " UTC"
#Start of markdown file.
s = f"`Generated at {timestamp} using game client version {currentGameVersion}.`\n"
s += "## Block IDs:\n"
s += "**WARNING:** This list is automatically generated and may have errors. "
s += "Double-check whether the game version above matches the client version "
s += "on pixelwalker.net\n\n"
s += "|Image|ID|Name|\n|---|---|---|\n" #Table header.

with(open("./README.md", "w", encoding="utf-8") as file): #Overwrite markdown file.
    file.write(s)
    for ID, info in sorted(blockList.items()): #Sort by blockID.
        n = info["imageName"] + ".png" #Filename for image alt text.
        p = "./images/" + n #Relative path to image.
        file.write(f"|![{n}]({p})|{ID}|{info['blockName']}|\n")

with open("./lastVersionGenerated.txt", "w", encoding="utf-8") as file: #Keep record of latest game version.
    file.write(currentGameVersion)

logging.info(f"Generated block list for {currentGameVersion}.")
print(f"Generated block list for {currentGameVersion}.")
