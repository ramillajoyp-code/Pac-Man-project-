# player.py
try:
    import pygame
except Exception as e:
    print("ERROR: failed to import pygame. Install it in your environment:\n"
          "  python -m pip install pygame\n"
          "Or use your venv python executable to install into the project's venv.")
    raise
import math
import os
from maze import TILE_SIZE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def render_pacman_surface(radius, color, angle=0, mouth_size=0, glow_color=None):
    """Render a Pac-Man wedge shape onto a small transparent surface, centered.

    `angle` is the facing direction in degrees (0=right, 90=up, 180=left, 270=down).
    `mouth_size` of 0 draws a closed circle (mouth shut).
    `glow_color`, if given, draws a soft translucent halo behind the shape -
    used for the fancier custom skins.
    Returns the Surface so callers (gameplay draw, menus, previews) can blit
    or fade it identically.
    """
    pad = int(radius * 0.7) if glow_color else 3
    size = radius * 2 + pad * 2
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    cx, cy = size // 2, size // 2

    if glow_color:
        pygame.draw.circle(surf, (*glow_color, 80), (cx, cy), int(radius * 1.35))

    if mouth_size <= 0:
        pygame.draw.circle(surf, color, (cx, cy), radius)
    else:
        points = [(cx, cy)]
        start_a = angle + mouth_size
        end_a = angle + 360 - mouth_size
        a = start_a
        while a <= end_a + 0.01:
            rad = math.radians(a)
            points.append((int(cx + math.cos(rad) * radius), int(cy - math.sin(rad) * radius)))
            a += 10
        if len(points) > 2:
            pygame.draw.polygon(surf, color, points)

    return surf


def load_pacman_sprite_frames(sprite_name="pacman"):
    """Load custom directional Pac-Man frames from assets/sprites/player."""
    base_dir = os.path.join(BASE_DIR, "assets", "sprites", "player")
    directions = ["right", "left", "up", "down"]
    frames = {}

    if not os.path.isdir(base_dir):
        return None

    for direction in directions:
        frames[direction] = []
        for frame_index in range(4):
            sprite_path = os.path.join(base_dir, f"{sprite_name}_{direction}_frame{frame_index}.png")
            if not os.path.exists(sprite_path):
                return None
            try:
                frames[direction].append(pygame.image.load(sprite_path).convert_alpha())
            except Exception:
                return None

    return frames


def load_player_image(image_name):
    image_path = os.path.join(BASE_DIR, "assets", "sprites", "player", image_name)
    if not os.path.exists(image_path):
        return None

    try:
        image = pygame.image.load(image_path).convert()
        image.set_colorkey(image.get_at((0, 0)))
        return image.convert_alpha()
    except Exception:
        return None


class PacMan:
    def __init__(self, col, row):
        self.start_col = col
        self.start_row = row

        self.color = (255, 255, 0)
        self.glow_color = None

        self.reset()
        
        self.sprite_name = "jerry1"
        self.sprite = load_player_image("jerry1.png")
        self.power_sprite = load_player_image("jerryangry.jpg")
        self.sprite_frames = None
        if not self.sprite:
            self.sprite_frames = load_pacman_sprite_frames("pacman")

    def set_skin(self, color, glow_color=None):
        """Apply a custom color skin (and optional glow halo) chosen from the sprite menu."""
        self.color = color
        self.glow_color = glow_color

    def reset(self):
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_row * TILE_SIZE + TILE_SIZE // 2
        self.speed = 4.0
        self.dir = pygame.Vector2(0, 0)        # No initial movement until player presses button
        self.buffer_dir = pygame.Vector2(0, 0)
        self.last_dir = pygame.Vector2(1, 0)
        self.anim_frame = 0
        self.living = True
        self.death_anim_time = 0.0

    def get_tile(self):
        return pygame.Vector2(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def set_buffer_direction(self, dx, dy):
        self.buffer_dir = pygame.Vector2(dx, dy)

    def _get_display_direction(self):
        if self.dir.x == 1:
            return "right"
        if self.dir.x == -1:
            return "left"
        if self.dir.y == -1:
            return "up"
        if self.dir.y == 1:
            return "down"
        if self.last_dir.x == 1:
            return "right"
        if self.last_dir.x == -1:
            return "left"
        if self.last_dir.y == -1:
            return "up"
        if self.last_dir.y == 1:
            return "down"
        return "right"

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
        if self.dir.length_squared() > 0:
            self.last_dir = self.dir.normalize()

    def draw(self, screen, powered_up=False):
        if not self.living:
            return

        px, py = int(self.x), int(self.y)
        active_sprite = self.power_sprite if powered_up and self.power_sprite else self.sprite

        if self.sprite_frames and not active_sprite:
            direction = self._get_display_direction()
            frames = self.sprite_frames.get(direction)
            if frames:
                sprite = frames[self.anim_frame % len(frames)]
                scaled = pygame.transform.scale(sprite, (TILE_SIZE, TILE_SIZE))
                screen.blit(scaled, (px - TILE_SIZE//2, py - TILE_SIZE//2))
                return

        if active_sprite:
            width = int(TILE_SIZE * 1.35)
            height = TILE_SIZE
            direction = self._get_display_direction()
            scaled = pygame.transform.smoothscale(active_sprite, (width, height))
            if direction == "left":
                scaled = pygame.transform.flip(scaled, True, False)
            elif direction == "up":
                scaled = pygame.transform.rotate(scaled, 90)
            elif direction == "down":
                scaled = pygame.transform.rotate(scaled, -90)
            screen.blit(scaled, (px - scaled.get_width() // 2, py - scaled.get_height() // 2))
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

        surf = render_pacman_surface(TILE_SIZE // 2, self.color, angle, m_size, self.glow_color)
        screen.blit(surf, (px - surf.get_width() // 2, py - surf.get_height() // 2))

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
            pygame.draw.circle(death_surface, (*self.color, alpha), (radius + 2, radius + 2), radius)
            screen.blit(death_surface, (px - radius - 2, py - radius - 2))
