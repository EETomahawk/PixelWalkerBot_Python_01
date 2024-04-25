#Potential dumb way of generating table of block images, names and IDs:

# Download game JS
# Regex search JS for /assets/tile_atlas-######.png to get the tile map PNG name.
# Download tile_atlas PNG
# Parse the subsequent list after the tilemap name in the JS to get the block names and locations in tilemap.
# Use this info to generate separate PNGs for each block, along with their "filename"
# Use this "filename" to find the more colloquial block names and their blockIDs elsewhere in the JS - see below
# Build a markdown-formatted table of blocks
# Consider doing the same with smileys
# Find a way to check the game version programatically - parse client JS probably
  # No need to update block list if version hasn't changed.... hopefully

# Turn the above steps into a Python script
# Look into using Python stdlib for the HTTP GETs to avoid dependency on external requests lib (optional)
# Set up GitHub Action to run script and commit resulting .md table into this repo
  # https://www.python-engineer.com/posts/run-python-github-actions/

JS:
n[n.GravityLeft = 1] = "GravityLeft",
n[n.GravityUp = 2] = "GravityUp",
n[n.GravityRight = 3] = "GravityRight",
n[n.GravityDown = 4] = "GravityDown",
n[n.GravityDot = 5] = "GravityDot",
n[n.GravitySlowDot = 6] = "GravitySlowDot",
n[n.BoostLeft = 7] = "BoostLeft",
n[n.BoostUp = 8] = "BoostUp",
n[n.BoostRight = 9] = "BoostRight",
n[n.BoostDown = 10] = "BoostDown",
...


JS:
"""
const Xo = Yo(Ko)
  , Vo = "/assets/tile_atlas-GalCJu8M.png"
  , Wo = [{
    filename: "background/basic/blue",
    frame: {
        x: 0,
        y: 0,
        w: 16,
        h: 16
    },
    rotated: !1,
    trimmed: !1,
    spriteSourceSize: {
        x: 0,
        y: 0,
        w: 16,
        h: 16
    },
    sourceSize: {
        w: 16,
        h: 16
    }
}, {
    filename: "background/basic/cyan",
    frame: {
        x: 16,
        y: 0,
        w: 16,
        h: 16
    },
    rotated: !1,
    trimmed: !1,
    spriteSourceSize: {
        x: 0,
        y: 0,
        w: 16,
        h: 16
    },
    sourceSize: {
        w: 16,
        h: 16
    }
    },
    ...
"""
