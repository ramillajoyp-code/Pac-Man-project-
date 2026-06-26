# pellets.py
import os
import pygame
from maze import TILE_SIZE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_pellet_image():
    image_path = os.path.join(BASE_DIR, "assets", "sprites", "items", "cheese.png")
    if not os.path.exists(image_path):
        return None

    try:
        image = pygame.image.load(image_path).convert()
        image.set_colorkey(image.get_at((0, 0)))
        return pygame.transform.smoothscale(image.convert_alpha(), (TILE_SIZE, TILE_SIZE))
    except Exception:
        return None


class PelletManager:
    def __init__(self, maze):
        self.maze = maze
        self.pellets = []
        self.power_pellets = []
        self.flash_timer = 0
        self.flash_visible = True
        self.pellet_image = load_pellet_image()
        self.load_pellets()

    def load_pellets(self):
        self.pellets = []
        self.power_pellets = []
        for r in range(self.maze.rows):
            for c in range(self.maze.cols):
                tile = self.maze.grid[r][c]
                if tile == '.':
                    self.pellets.append(pygame.Vector2(c, r))
                elif tile == 'P':
                    self.power_pellets.append(pygame.Vector2(c, r))

    def update(self, dt):
        self.flash_timer += dt
        if self.flash_timer >= 0.2:  # Classic flashing cycle
            self.flash_visible = not self.flash_visible
            self.flash_timer = 0

    def check_collisions(self, player_tile):
        score_gain = 0
        power_activated = False

        # Regular pellets
        for p in self.pellets[:]:
            if p == player_tile:
                self.pellets.remove(p)
                score_gain += 10

        # Power pellets
        for pp in self.power_pellets[:]:
            if pp == player_tile:
                self.power_pellets.remove(pp)
                score_gain += 50
                power_activated = True

        return score_gain, power_activated

    def is_empty(self):
        return len(self.pellets) == 0 and len(self.power_pellets) == 0

    def draw(self, screen):
        theme = getattr(self.maze, "theme", None) or {}
        pellet_color = theme.get("pellet_color", (255, 184, 174))
        power_color = theme.get("power_pellet_color", (255, 184, 174))

        # Render standard pellets
        for p in self.pellets:
            px = int(p.x * TILE_SIZE + TILE_SIZE // 2)
            py = int(p.y * TILE_SIZE + TILE_SIZE // 2)
            if self.pellet_image:
                screen.blit(self.pellet_image, (px - TILE_SIZE // 2, py - TILE_SIZE // 2))
            else:
                pygame.draw.rect(screen, pellet_color, (px - 2, py - 2, 4, 4))

        # Render flashing Power Pellets
        if self.flash_visible:
            for pp in self.power_pellets:
                px = int(pp.x * TILE_SIZE + TILE_SIZE // 2)
                py = int(pp.y * TILE_SIZE + TILE_SIZE // 2)
                pygame.draw.circle(screen, power_color, (px, py), 8)
