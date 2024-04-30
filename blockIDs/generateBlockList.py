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
# Find the list of blockIDs and block names elsewhere in the JS. These names don't exactly match the tile names.
# Match up the block names with the tile names so that we know which tile PNG is which blockID.
# Build a README markdown file with a table of blocks.
# Use GitHub Actions to run this script periodically.

import logging
import traceback, sys
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
  error = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback)) #Format exception as str.
  logging.fatal(error) #Log exception to file.
  print("Fatal error. See ./generateBlockList.log")
  print(error) #For debugging GitHub Action.
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

#Get game version from JS. String in double quotes before pixelwalker# room type.
currentGameVersion = re.search('"[^\"]+"[^\"]+(?="pixelwalker\d+")', gameJS).group().split('"')[1]
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
    #Manipulate the tileName a bit to improve get_close_matches().
    #Remove "foreground_" and "decoration" as these don't appear in the JS list of block IDs and names.
    for s in ["foreground_", "decoration_", "hazards_"]:
        tileName = tileName.replace(s,"")
    #Put "background_" at the front of the string.
    if tileName.startswith("background_"): tileName = tileName[11:] + "_background"

    blockImage.save(f"./images/{tileName}.png")
    tileNames.append(tileName)

#Search JS for Empty=0. This is start of a different list containing block IDs and names.
#These names are different from the tile names above, so need to match them together.
#Everything between "Empty=0" and ")"
rawBlockIDs = re.search("(?<=Empty=0)[^)]+(?=\))", gameJS).group().split(",")

#For each item, extract substring between . and ] - e.g. "GravityLeft=1". Ignore first line (block ID 0).
rawBlockNamesAndIDs = [re.search("(?<=\.)[^\]]+(?=])", item).group() for item in rawBlockIDs if "." in item]

#Turn that into a dict where the keys are the names and the values are the block IDs.
blockNamesAndIDs = {0:"Empty"} | {x[1]:x[0] for x in [item.split("=",1) for item in rawBlockNamesAndIDs]}

#tileNames list has the names of the block images in format "background/basic/blue", "foreground/candy/platform_green" etc.
#blockNamesAndIDs has block ID, and names in format "BasicBlue", "CandyPlatformGreen" etc.
#Need to match them up. e.g. "NormalRedBg" and "background_normal_red"

#Make blockNamesAndIDs names more list the other list:
#Assume the strings are PascalCase and convert to snake_case. #Change "bg" to "background".
blockNamesAndIDs = {k:re.sub(r'(?<!^)(?=[A-Z])', '_', v).lower().replace("bg","background")
                    for k,v in blockNamesAndIDs.items()}

blockList = {}

#Do multiple passes at decreasing confidence levels to match up the strings.
#Eliminate each matched pair to improve subsequent matches/iterations.
cutoff = [0.8, 0.5, 0]
for n in cutoff:
    for blockID, blockName in blockNamesAndIDs.copy().items():
        matches = get_close_matches(blockName, tileNames, n=1, cutoff=n)
        if matches: #Non-empty list - i.e. match found at confidence above this cutoff.
            tileName = matches[0]
            blockList[int(blockID)] = {
                "blockName": blockName,
                "imageName": tileName }
            #Remove match from both collections, since we're doing multiple passes.
            tileNames.remove(tileName)
            del blockNamesAndIDs[blockID]
    #For debugging:
    #if len(cutoff) > 1 and n == cutoff[-2]: blockList.clear()
#print(f"{len(blockList)}/{len(blockNamesAndIDs)+len(blockList)} matched. {len(blockNamesAndIDs)} remaining.")

timestamp = str(datetime.utcnow())[:-7] + " UTC"
#Start of markdown file.
s = f"`Generated at {timestamp} using game client version {currentGameVersion}.`\n"
s += "## Block IDs:\n"
s += "**WARNING:** This list is automatically generated using the game client's JS source. "
s += "It may have errors, and it might stop working after an update.  \n"
s += "**NOTE:** The block names below are descriptive and aren't guaranteed to match "
s += "[mappings.json](https://game.pixelwalker.net/mappings).\n\n"
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
