# maze.py
import pygame

# 28 columns x 36 rows arcade layout
# X: Wall, .: Pellet, P: Power Pellet, G: Ghost House Gate, H: Ghost House, C: Cage, ' ': Empty Space
ORIGINAL_MAZE = [
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "X............XX............X",
    "X.XXXX.XXXXX.XX.XXXXX.XXXX.X",
    "XPX  X.X   X.XX.X   X.X  XPX",
    "X.XXXX.XXXXX.XX.XXXXX.XXXX.X",
    "X..........................X",
    "X.XXXX.XX.XXXXXXXX.XX.XXXX.X",
    "X.XXXX.XX.XXXXXXXX.XX.XXXX.X",
    "X......XX....XX....XX......X",
    "XXXXXX.XXXXX XX XXXXX.XXXXXX",
    "     X.XXXXX XX XXXXX.X     ",
    "     X.XX          XX.X     ",
    "     X.XX          XX.X     ",
    "XXXXXX.XX  XGGGGX  XX.XXXXXX",
    "T     .    XHHHHX    .     T",
    "XXXXXX.XX  XXXXXX  XX.XXXXXX",
    "     X.XX          XX.X     ",
    "     X.XX          XX.X     ",
    "     X.XX XXXXXXXX XX.X     ",
    "XXXXXX.XX XXXXXXXX XX.XXXXXX",
    "X............XX............X",
    "X.XXXX.XXXXX.XX.XXXXX.XXXX.X",
    "X.XXXX.XXXXX.XX.XXXXX.XXXX.X",
    "XP..XX.......  .......XX..PX",
    "XXX.XX.XX.XXXXXXXX.XX.XX.XXX",
    "XXX.XX.XX.XXXXXXXX.XX.XX.XXX",
    "X......XX....XX....XX......X",
    "X.XXXXXXXXXX.XX.XXXXXXXXXX.X",
    "X.XXXXXXXXXX.XX.XXXXXXXXXX.X",
    "X..........................X",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXX"
]

TILE_SIZE = 20
SCREEN_WIDTH = 28 * TILE_SIZE
SCREEN_HEIGHT = 38* TILE_SIZE

class Maze:
    def __init__(self):
        self.grid = [list(row) for row in ORIGINAL_MAZE]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])

    def is_wall(self, col, row):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            # Handle map wrap-around tunnels safely
            if row == 17 and (col < 0 or col >= self.cols):
                return False
            return True
        return self.grid[row][col] == 'X' or self.grid[row][col] == 'G' or self.grid[row][col] == 'H'

    def is_ghost_house_gate(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 'G'
        return False

    def is_cage(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 'C'
        return False

    def is_ghost_house(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] == 'H'
        return False

    def draw(self, screen):
        for r in range(self.rows):
            for c in range(self.cols):
                tile = self.grid[r][c]
                x = c * TILE_SIZE
                y = r * TILE_SIZE
                
                if tile == 'X':
                    # Classic Pacman arcade wall style - solid filled with blue color
                    pygame.draw.rect(screen, (33, 33, 222), (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2))
                    # Add border for definition
                    pygame.draw.rect(screen, (66, 66, 255), (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 1)
                elif tile == 'G':
                    # Ghost Gate - pink horizontal line
                    pygame.draw.rect(screen, (255, 184, 255), (x, y + TILE_SIZE//2 - 2, TILE_SIZE, 4))
                elif tile == 'C':
                    # Ghost Cage - pink dotted border (outline only)
                    pygame.draw.rect(screen, (200, 100, 200), (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)