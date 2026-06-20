# ghost.py
import pygame
import random
import os
from maze import TILE_SIZE

# Target Corners for Scatter States
SCATTER_TARGETS = {
    "BLINKY": pygame.Vector2(25, -3),
    "PINKY": pygame.Vector2(2, -3),
    "INKY": pygame.Vector2(27, 34),
    "CLYDE": pygame.Vector2(0, 34)
}

GHOST_COLORS = {
    "BLINKY": (255, 0, 0),     # Red
    "PINKY": (255, 184, 255),  # Pink
    "INKY": (0, 255, 255),     # Cyan
    "CLYDE": (255, 184, 81)    # Orange
}

class Ghost:
    def __init__(self, name, start_col, start_row):
        self.name = name
        self.start_col = start_col
        self.start_row = row = start_row
        self.reset()
        
        self.sprite = None
        sprite_path = os.path.join("assets", "sprites", f"{name.lower()}.png")
        if os.path.exists(sprite_path):
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
            except Exception:
                pass

    def reset(self):
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_row * TILE_SIZE + TILE_SIZE // 2
        self.dir = pygame.Vector2(0, -1)
        self.mode = "SCATTER"  # SCATTER, CHASE, FRIGHTENED, EATEN
        self.speed = 2.5
        self.target = pygame.Vector2(0, 0)
        self.in_house = True  # Start ghosts in the house

    def get_tile(self):
        return pygame.Vector2(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def update_target(self, player, blinky_tile):
        if self.mode == "SCATTER":
            self.target = SCATTER_TARGETS[self.name]
            return

        if self.mode == "EATEN":
            self.target = pygame.Vector2(14, 14) # Head directly back home
            return

        p_tile = player.get_tile()
        p_dir = player.dir

        if self.name == "BLINKY":
            self.target = p_tile

        elif self.name == "PINKY":
            # Targets 4 spaces directly ahead of Pac-Man
            self.target = p_tile + p_dir * 4

        elif self.name == "INKY":
            # Direct vector offset: 2 tiles ahead of Pacman offset doubled against Blinky
            pivot = p_tile + p_dir * 2
            vec = pivot - blinky_tile
            self.target = pivot + vec

        elif self.name == "CLYDE":
            # Aggressive if > 8 tiles away, retreats to corner if closer
            dist = self.get_tile().distance_to(p_tile)
            if dist > 8:
                self.target = p_tile
            else:
                self.target = SCATTER_TARGETS["CLYDE"]

    def update(self, maze, player, blinky_tile, global_mode):
        if self.mode != "FRIGHTENED" and self.mode != "EATEN":
            self.mode = global_mode

        # Set specific speed scaling profiles
        if self.mode == "FRIGHTENED":
            self.speed = 1.5
        elif self.mode == "EATEN":
            self.speed = 5.0
        else:
            self.speed = 2.5

        current_tile = self.get_tile()
        tile_center_x = current_tile.x * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = current_tile.y * TILE_SIZE + TILE_SIZE // 2

        # Evaluate target state modifications
        if self.mode == "EATEN" and current_tile == pygame.Vector2(14, 14):
            self.mode = global_mode

        # Turn logic executed precisely at tile intersections
        if abs(self.x - tile_center_x) < self.speed and abs(self.y - tile_center_y) < self.speed:
            self.x = tile_center_x
            self.y = tile_center_y
            
            self.update_target(player, blinky_tile)
            
            # Form list of available movement paths
            directions = [pygame.Vector2(0, -1), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(1, 0)]
            valid_moves = []

            for d in directions:
                # Authentic Arcade Constraint: Ghosts cannot reverse back on themselves
                if d + self.dir == pygame.Vector2(0, 0):
                    continue
                
                nt = current_tile + d
                if not maze.is_wall(int(nt.x), int(nt.y)):
                    # Restrict access out of house gates except for retreating eyes
                    if maze.is_ghost_house_gate(int(nt.x), int(nt.y)) and self.mode != "EATEN":
                        continue
                    valid_moves.append(d)

            if valid_moves:
                if self.mode == "FRIGHTENED":
                    # Random branching paths during Frightened mode
                    self.dir = random.choice(valid_moves)
                else:
                    # Select paths based on shortest straight line distance to target
                    # Safety check: if target is (0, 0), use first valid move
                    if self.target == pygame.Vector2(0, 0):
                        self.dir = valid_moves[0]
                    else:
                        best_move = valid_moves[0]
                        best_dist = (current_tile + best_move).distance_to(self.target)
                        for m in valid_moves[1:]:
                            d = (current_tile + m).distance_to(self.target)
                            if d < best_dist:
                                best_dist = d
                                best_move = m
                        self.dir = best_move

        self.x += self.dir.x * self.speed
        self.y += self.dir.y * self.speed

        # Tunnel wrap-around boundaries
        if self.x < -TILE_SIZE // 2:
            self.x = maze.cols * TILE_SIZE + TILE_SIZE // 2
        elif self.x > maze.cols * TILE_SIZE + TILE_SIZE // 2:
            self.x = -TILE_SIZE // 2

    def draw(self, screen):
        gx, gy = int(self.x), int(self.y)
        
        if self.sprite and self.mode != "FRIGHTENED" and self.mode != "EATEN":
            scaled = pygame.transform.scale(self.sprite, (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled, (gx - TILE_SIZE//2, gy - TILE_SIZE//2))
            return

        # Core State Renderer
        if self.mode == "FRIGHTENED":
            # Vulnerable blue form - classic Pacman style
            color = (33, 33, 255)
            radius = TILE_SIZE // 2
            # Main body circle
            pygame.draw.circle(screen, color, (gx, gy - 1), radius)
            # Wavy bottom (classic ghost shape)
            pygame.draw.circle(screen, color, (gx - radius + 4, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx - radius + 10, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx + radius - 10, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx + radius - 4, gy + radius - 2), 3)
            # Frightened eyes
            pygame.draw.circle(screen, (255, 255, 255), (gx - 5, gy - 2), 3)
            pygame.draw.circle(screen, (255, 255, 255), (gx + 5, gy - 2), 3)
            pygame.draw.circle(screen, (0, 0, 255), (gx - 5, gy - 2), 1)
            pygame.draw.circle(screen, (0, 0, 255), (gx + 5, gy - 2), 1)
        elif self.mode == "EATEN":
            # Defeated eyes escaping back to base
            pygame.draw.circle(screen, (255, 255, 255), (gx - 5, gy - 2), 3)
            pygame.draw.circle(screen, (255, 255, 255), (gx + 5, gy - 2), 3)
            pygame.draw.circle(screen, (0, 0, 255), (gx - 5 + int(self.dir.x*2), gy - 2 + int(self.dir.y*2)), 2)
            pygame.draw.circle(screen, (0, 0, 255), (gx + 5 + int(self.dir.x*2), gy - 2 + int(self.dir.y*2)), 2)
        else:
            # Classic Pacman arcade ghost style
            color = GHOST_COLORS.get(self.name, (255, 255, 255))
            radius = TILE_SIZE // 2
            
            # Main body circle
            pygame.draw.circle(screen, color, (gx, gy - 1), radius)
            
            # Wavy bottom (4 bumps for classic ghost shape)
            pygame.draw.circle(screen, color, (gx - radius + 4, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx - radius + 10, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx + radius - 10, gy + radius - 2), 3)
            pygame.draw.circle(screen, color, (gx + radius - 4, gy + radius - 2), 3)
            
            # Eyes - white circles with blue pupils that track direction
            eye_spacing = 6
            pygame.draw.circle(screen, (255, 255, 255), (gx - eye_spacing, gy - 3), 4)
            pygame.draw.circle(screen, (255, 255, 255), (gx + eye_spacing, gy - 3), 4)
            
            # Pupils follow direction
            pupil_offset = 1.5
            px1 = gx - eye_spacing + int(self.dir.x * pupil_offset)
            py1 = gy - 3 + int(self.dir.y * pupil_offset)
            px2 = gx + eye_spacing + int(self.dir.x * pupil_offset)
            py2 = gy - 3 + int(self.dir.y * pupil_offset)
            
            pygame.draw.circle(screen, (0, 0, 255), (int(px1), int(py1)), 2)
            pygame.draw.circle(screen, (0, 0, 255), (int(px2), int(py2)), 2)