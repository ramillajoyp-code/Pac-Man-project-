# pellets.py
import pygame
from maze import TILE_SIZE

class PelletManager:
    def __init__(self, maze):
        self.maze = maze
        self.pellets = []
        self.power_pellets = []
        self.flash_timer = 0
        self.flash_visible = True
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
        # Render standard pellets
        for p in self.pellets:
            px = int(p.x * TILE_SIZE + TILE_SIZE // 2)
            py = int(p.y * TILE_SIZE + TILE_SIZE // 2)
            pygame.draw.rect(screen, (255, 184, 174), (px - 2, py - 2, 4, 4))

        # Render flashing Power Pellets
        if self.flash_visible:
            for pp in self.power_pellets:
                px = int(pp.x * TILE_SIZE + TILE_SIZE // 2)
                py = int(pp.y * TILE_SIZE + TILE_SIZE // 2)
                pygame.draw.circle(screen, (255, 184, 174), (px, py), 8)