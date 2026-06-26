# maze.py
import os
import pygame

# 19 columns x 21 rows custom layout
# 1: Wall, B: Power Pellet, -: Ghost House Gate, P: Player Start
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
    "XXXXXX.XXXXX XX XXXXX.XXXXXX",
    "XXXXXX.XX          XX.XXXXXX",
    "XXXXXX.XX          XX.XXXXXX",
    "XXXXXX.XX  XGGGGX  XX.XXXXXX",
    "T     .    XHHHHX    .     T",
    "XXXXXX.XX  XXXXXX  XX.XXXXXX",
    "XXXXXX.XX          XX.XXXXXX",
    "XXXXXX.XX          XX.XXXXXX",
    "XXXXXX.XX XXXXXXXX XX.XXXXXX",
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

# Default color theme - grassy plain. Other
# themes (see map_theme.py) override these via set_theme().
DEFAULT_THEME = {
    "id": "grassy_plain",
    "wall_color": (74, 145, 45),
    "wall_border_color": (174, 218, 96),
    "wall_accent_color": (38, 104, 35),
    "gate_color": (221, 185, 92),
    "cage_color": (105, 154, 78),
    "bg_color": (9, 35, 18),
    "pellet_color": (244, 232, 169),
    "power_pellet_color": (255, 246, 190),
}

WALL_TEXTURE_PATH = os.path.join(
    os.path.dirname(__file__),
    "assets",
    "sprites",
    "maze",
    "mazeee.png",
)

class Maze:
    def __init__(self):
        self.grid = [list(row) for row in ORIGINAL_MAZE]
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.theme = DEFAULT_THEME.copy()
        self.wall_texture = self._load_wall_texture()

    def _load_wall_texture(self):
        if not os.path.exists(WALL_TEXTURE_PATH):
            return None

        try:
            texture = pygame.image.load(WALL_TEXTURE_PATH).convert()
            return pygame.transform.smoothscale(
                texture,
                (self.cols * TILE_SIZE, self.rows * TILE_SIZE)
            )
        except pygame.error:
            return None

    def set_theme(self, theme):
        """Apply a custom color theme (see map_theme.py) chosen from the map menu."""
        merged = DEFAULT_THEME.copy()
        merged.update(theme)
        self.theme = merged

    def is_wall(self, col, row):
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            # Handle map wrap-around tunnels safely
            if row == 17 and (col < 0 or col >= self.cols):
                return False
            return True
        return self.grid[row][col] in ('1', 'X', 'G', 'H')

    def is_ghost_house_gate(self, col, row):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self.grid[row][col] in ('-', 'G')
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
                
                if tile in ('1', 'X'):
                    wall_rect = (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2)
                    if self.wall_texture:
                        screen.blit(self.wall_texture, wall_rect, wall_rect)
                    else:
                        pygame.draw.rect(screen, self.theme["wall_color"], wall_rect)
                        accent = self.theme.get("wall_accent_color")
                        if accent:
                            blade_x = x + 5 + ((r * 3 + c * 5) % 9)
                            blade_y = y + 5 + ((r * 7 + c * 2) % 8)
                            pygame.draw.line(screen, accent, (blade_x, blade_y + 6), (blade_x - 2, blade_y), 1)
                            pygame.draw.line(screen, accent, (blade_x + 4, blade_y + 7), (blade_x + 6, blade_y + 1), 1)

                    pygame.draw.rect(screen, self.theme["wall_border_color"], (x + 1, y + 1, TILE_SIZE - 2, TILE_SIZE - 2), 1)
                elif tile in ('-', 'G'):
                    # Ghost Gate - themed horizontal line
                    pygame.draw.rect(screen, self.theme["gate_color"], (x, y + TILE_SIZE//2 - 2, TILE_SIZE, 4))
                elif tile == 'C':
                    # Ghost Cage - themed dotted border (outline only)
                    pygame.draw.rect(screen, self.theme["cage_color"], (x + 2, y + 2, TILE_SIZE - 4, TILE_SIZE - 4), 2)
