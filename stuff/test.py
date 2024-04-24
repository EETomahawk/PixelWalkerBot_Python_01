#Potential dumb way of generating table of block images, names and IDs:

# Download https://game.pixelwalker.net/mappings
# Download game JS
# Regex search JS for /assets/tile_atlas-dasdas.png to get the tile map PNG name.
# Download tile_atlas... .png
# Parse the subsequent list after the tilemap name in the JS to get the block names and locations in tilemap.
# Match the block names in the JS against the block names in the mappings JSON

Mapping:
"gravity_left": 1,
"gravity_up": 2,
"gravity_right": 3,
"gravity_down": 4,
"gravity_dot": 5,
"gravity_slow_dot": 6,
"boost_left": 7,
"boost_up": 8,
"boost_right": 9,

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
"""