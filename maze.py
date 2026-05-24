BASE_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWW",
    "W....W.......W.......W",
    "W.WW.W.WWWWW.W.WWW.W.W",
    "W.W..W...P...W...W..W.W",
    "W.WW.WWW.WWW.WWW.WW.W.W",
    "W.....................W",
    "W.WWWWW.WWWWWWW.WWWWW.W",
    "W.....W.........W.....W",
    "W.WWW.W.WWWWW.W.WWW.W.W",
    "W..P..W...W...W...W..PW",
    "WWWWWWWWWWWWWWWWWWWWWWW"
]

def copy_map():
    return [list(r) for r in BASE_MAP]

MAP = copy_map()

def is_wall(x, y):
    if y < 0 or y >= len(MAP):
        return True
    if x < 0 or x >= len(MAP[0]):
        return True
    return MAP[y][x] == "W"

def check_win():
    for row in MAP:
        if "." in row:
            return False
    return True
