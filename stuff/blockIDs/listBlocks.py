#Python 3.10
import requests #requests==2.31.0
import re
from io import BytesIO
from PIL import Image #pillow==10.3.0
import json

gameURL = "https://pixelwalker.net"
gameHTML = requests.get(f"{gameURL}/game.html").text #Download page HTML.

#Game client JS file has format "game-cwptkMuL.js". Find this random string in the HTML using regex.
clientJSID = re.search('(?<="/assets/game-)[^.]+(?=\.js")', gameHTML).group()
jsURL = f"{gameURL}/assets/game-{clientJSID}.js" #Build URL to JS file.
gameJS = requests.get(jsURL).text #Get JS file contents.

#PNG containing all blocks has similar naming format to JS file. Find it in the JS.
tilesetID = re.search('(?<="/assets/tile_atlas-)[^.]+(?=\.png")', gameJS).group()
tilesetURL = f"{gameURL}/assets/tile_atlas-{tilesetID}.png" #Build URL to PNG containing all blocks.
tilesetPNG = Image.open(BytesIO(requests.get(tilesetURL).content)) #Download PNG and load it into Pillow.

tilesetJSArray = re.search("(?<=\[)[^\]]+(?=])", gameJS.split(tilesetID, 1)[1]).group()
#Cannot easily convert this JS array of objects to JSON for parsing. Instead, manually parse it.

tilesNames = []

rawTileInfo = tilesetJSArray.split("filename:")[1:]
for rawTile in rawTileInfo:
    name = re.search('(?<=")[^"]+(?=")', rawTile).group() #Get name of tile - e.g. "foreground/switches/local_switch"
    frame = re.search("(?<=frame:{)[^}]+(?=})", rawTile).group() #Get tile info - e.g. "x:0,y:0,w:16,h:16"
    #x and y are top left coordinate of tile in PNG. w and h are its width and height (probably always 16x16).
    #Assume x and then y always appear first and extract them.
    #Ignore w and h. Portals, coins, water, fire etc. are composed of multiple 16x10 tiles because they're animated
    #so just use the first 16x16 bit of that section as the block image.
    x, y, _, _ = [int(v.split(":")[1]) for v in frame.split(",")]
    blockImage = tilesetPNG.crop((x, y, x+16, y+16))

    #blockImage.save(f"./images/{name.replace('/','_')}.png")
    tilesNames.append(name)

print(tilesNames)
# im = Image.open("test.jpg")
#
# crop_rectangle = (50, 50, 200, 200)
# cropped_im = im.crop(crop_rectangle)
## Note that the crop region must be given as a 4-tuple - (left, upper, right, lower).
#cropped_im.show()