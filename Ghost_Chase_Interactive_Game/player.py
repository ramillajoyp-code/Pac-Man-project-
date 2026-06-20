# player.py
import pygame
import math
import os
from maze import TILE_SIZE

class PacMan:
    def __init__(self, col, row):
        self.start_col = col
        self.start_row = row
        self.reset()
        
        # Load external asset if available, otherwise draw procedurally
        self.sprite = None
        sprite_path = os.path.join("assets", "sprites", "pacman.png")
        if os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception:
                pass

    def reset(self):
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_row * TILE_SIZE + TILE_SIZE // 2
        self.speed = 4.0
        self.dir = pygame.Vector2(0, 0)        # No initial movement until player presses button
        self.buffer_dir = pygame.Vector2(0, 0)
        self.anim_frame = 0
        self.living = True
        self.death_anim_time = 0.0

    def get_tile(self):
        return pygame.Vector2(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def set_buffer_direction(self, dx, dy):
        self.buffer_dir = pygame.Vector2(dx, dy)

    def update(self, maze):
        if not self.living:
            self.death_anim_time += 0.016  # ~60 FPS
            return

        current_tile = self.get_tile()
        tile_center_x = current_tile.x * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = current_tile.y * TILE_SIZE + TILE_SIZE // 2

        # Check if we can shift to buffered direction
        if self.buffer_dir != self.dir and self.buffer_dir != pygame.Vector2(0, 0):
            # If changing to reverse direction, execute instantly
            if self.buffer_dir + self.dir == pygame.Vector2(0, 0):
                self.dir = self.buffer_dir
            # Otherwise, verify grid alignment to make structural turns
            elif abs(self.x - tile_center_x) < self.speed and abs(self.y - tile_center_y) < self.speed:
                next_tile = current_tile + self.buffer_dir
                if not maze.is_wall(int(next_tile.x), int(next_tile.y)):
                    self.x = tile_center_x
                    self.y = tile_center_y
                    self.dir = self.buffer_dir

        # Handle movement step
        next_step_tile = current_tile + self.dir
        is_at_center_x = abs(self.x - tile_center_x) < self.speed
        is_at_center_y = abs(self.y - tile_center_y) < self.speed

        if maze.is_wall(int(next_step_tile.x), int(next_step_tile.y)):
            # Halt object directly on the tile center if the next tile is blocked
            if (self.dir.x != 0 and is_at_center_x) or (self.dir.y != 0 and is_at_center_y):
                self.x = tile_center_x
                self.y = tile_center_y
            else:
                self.x += self.dir.x * self.speed
                self.y += self.dir.y * self.speed
        else:
            self.x += self.dir.x * self.speed
            self.y += self.dir.y * self.speed

        # Map Side Tunnel wrap-around mechanics
        if self.x < -TILE_SIZE // 2:
            self.x = maze.cols * TILE_SIZE + TILE_SIZE // 2
        elif self.x > maze.cols * TILE_SIZE + TILE_SIZE // 2:
            self.x = -TILE_SIZE // 2

        self.anim_frame = (self.anim_frame + 1) % 4

    def draw(self, screen):
        if not self.living:
            return

        px, py = int(self.x), int(self.y)
        
        if self.sprite:
            # Scale and blit external asset if available
            scaled = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled, (px - TILE_SIZE//2, py - TILE_SIZE//2))
            return

        # Procedural retro vector fallback
        angle = 0
        if self.dir.x == 1: angle = 0
        elif self.dir.x == -1: angle = 180
        elif self.dir.y == -1: angle = 90
        elif self.dir.y == 1: angle = 270

        # Cycle through mouth mechanics: open wide, partially open, fully shut
        mouth_sizes = [30, 15, 0, 15]
        m_size = mouth_sizes[self.anim_frame]

        if m_size == 0:
            pygame.draw.circle(screen, (255, 255, 0), (px, py), TILE_SIZE // 2)
        else:
            start_rad = math.radians(angle + m_size)
            end_rad = math.radians(angle + 360 - m_size)
            
            points = [
                (px, py),
                *( (px + int(math.cos(math.radians(a)) * (TILE_SIZE // 2)),
                    py - int(math.sin(math.radians(a)) * (TILE_SIZE // 2)))
                   for a in range(int(angle + m_size), int(angle + 360 - m_size) + 1, 10) )
            ]
            if len(points) > 2:
                pygame.draw.polygon(screen, (255, 255, 0), points)

    def draw_death_animation(self, screen):
        """Draw Pacman death animation with shrinking, flashing, and fade-out."""
        px, py = int(self.x), int(self.y)
        progress = self.death_anim_time / 1.5  # Total animation duration: 1.5 seconds
        
        if progress >= 1.0:
            return  # Animation complete
        
        # Shrinking effect: radius decreases from full size to nearly 0
        radius = int((TILE_SIZE // 2) * (1.0 - progress ** 2))
        
        # Flashing effect: alternate visibility
        flash_cycles = 6
        flash_progress = (progress * flash_cycles) % 1.0
        should_draw = flash_progress < 0.5
        
        # Fade-out effect: alpha decreases from 255 to 0
        alpha = int(255 * (1.0 - progress))
        
        if should_draw and radius > 0:
            # Create a surface with per-pixel alpha for fade-out
            death_surface = pygame.Surface((radius * 2 + 4, radius * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(death_surface, (255, 255, 0, alpha), (radius + 2, radius + 2), radius)
            screen.blit(death_surface, (px - radius - 2, py - radius - 2))
