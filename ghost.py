# ghost.py
import pygame
import random
import os
from collections import deque
from maze import TILE_SIZE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Target Corners for Scatter States
SCATTER_TARGETS = {
    "BLINKY": pygame.Vector2(25, -3),
    "PINKY": pygame.Vector2(2, -3),
    "INKY": pygame.Vector2(27, 34),
    "CLYDE": pygame.Vector2(0, 34)
}

HOUSE_EXIT_TARGET = pygame.Vector2(14, 15)

GHOST_COLORS = {
    "BLINKY": (255, 0, 0),     # Red
    "PINKY": (255, 184, 255),  # Pink
    "INKY": (0, 255, 255),     # Cyan
    "CLYDE": (255, 184, 81)    # Orange
}

GHOST_SPRITES = {
    "BLINKY": "tom1.png",
    "PINKY": "birdie.png",
    "INKY": "tom3.png",
    "CLYDE": "doggy.png",
}


def load_ghost_image(image_name):
    image_path = os.path.join(BASE_DIR, "assets", "sprites", "ghosts", image_name)
    if not os.path.exists(image_path):
        return None

    try:
        image = pygame.image.load(image_path).convert()
        image.set_colorkey(image.get_at((0, 0)))
        return image.convert_alpha()
    except Exception:
        return None

class Ghost:
    def __init__(self, name, start_col, start_row):
        self.name = name
        self.start_col = start_col
        self.start_row = row = start_row
        self.reset()
        
        self.sprite = load_ghost_image(GHOST_SPRITES.get(name, ""))

    def reset(self):
        self.x = self.start_col * TILE_SIZE + TILE_SIZE // 2
        self.y = self.start_row * TILE_SIZE + TILE_SIZE // 2
        self.dir = pygame.Vector2(0, -1)
        self.mode = "SCATTER"  # SCATTER, CHASE, FRIGHTENED, EATEN
        self.speed = 2.5
        self.normal_speed = 2.5
        self.frightened_speed = 1.5
        self.eaten_speed = 5.0
        self.target = pygame.Vector2(0, 0)
        self.in_house = True  # Start ghosts in the house

    def get_tile(self):
        return pygame.Vector2(int(self.x // TILE_SIZE), int(self.y // TILE_SIZE))

    def can_enter_tile(self, maze, col, row):
        if row < 0 or row >= maze.rows or col < 0 or col >= maze.cols:
            return row == 17 and (col < 0 or col >= maze.cols)

        tile = maze.grid[row][col]
        if tile in ('G', 'H'):
            return self.in_house or self.mode == "EATEN"
        return tile not in ('1', 'X')

    def update_house_state(self, maze):
        tile = self.get_tile()
        col, row = int(tile.x), int(tile.y)
        if 0 <= row < maze.rows and 0 <= col < maze.cols:
            self.in_house = maze.grid[row][col] in ('G', 'H')

    def update_target(self, player, blinky_tile):
        if self.in_house and self.mode != "EATEN":
            self.target = HOUSE_EXIT_TARGET
            return

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

    def get_path_direction(self, maze, start_tile, target_tile, valid_moves):
        start = (int(start_tile.x), int(start_tile.y))
        target = (int(target_tile.x), int(target_tile.y))

        if start == target:
            return None

        queue = deque([(start, None)])
        visited = {start}
        directions = [pygame.Vector2(0, -1), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(1, 0)]

        while queue:
            (col, row), first_step = queue.popleft()
            for direction in directions:
                next_col = col + int(direction.x)
                next_row = row + int(direction.y)
                next_pos = (next_col, next_row)

                if next_pos in visited:
                    continue
                if not self.can_enter_tile(maze, next_col, next_row):
                    continue

                next_first_step = first_step or direction
                if next_pos == target:
                    if any(next_first_step == move for move in valid_moves):
                        return next_first_step
                    return None

                visited.add(next_pos)
                queue.append((next_pos, next_first_step))

        return None

    def sync_mode(self, global_mode):
        if self.mode == "EATEN":
            return

        if global_mode == "FRIGHTENED":
            if not self.in_house:
                self.mode = "FRIGHTENED"
            return

        self.mode = global_mode

    def update(self, maze, player, blinky_tile, global_mode):
        self.update_house_state(maze)
        self.sync_mode(global_mode)

        # Set specific speed scaling profiles
        if self.mode == "FRIGHTENED":
            self.speed = self.frightened_speed
        elif self.mode == "EATEN":
            self.speed = self.eaten_speed
        else:
            self.speed = self.normal_speed

        current_tile = self.get_tile()
        tile_center_x = current_tile.x * TILE_SIZE + TILE_SIZE // 2
        tile_center_y = current_tile.y * TILE_SIZE + TILE_SIZE // 2
        center_offset = pygame.Vector2(self.x - tile_center_x, self.y - tile_center_y)
        near_tile_center = abs(center_offset.x) <= self.speed and abs(center_offset.y) <= self.speed
        moving_toward_center = self.dir.length_squared() == 0 or center_offset.dot(self.dir) <= 0

        # Evaluate target state modifications
        if self.mode == "EATEN" and current_tile == pygame.Vector2(14, 14):
            self.mode = "CHASE" if global_mode == "FRIGHTENED" else global_mode

        # Turn logic executed precisely at tile intersections
        if near_tile_center and moving_toward_center:
            self.x = tile_center_x
            self.y = tile_center_y
            
            self.update_target(player, blinky_tile)
            
            # Form list of available movement paths. Ghosts use their own
            # passability so they can leave/enter the ghost house cleanly.
            directions = [pygame.Vector2(0, -1), pygame.Vector2(-1, 0), pygame.Vector2(0, 1), pygame.Vector2(1, 0)]
            valid_moves = []
            reverse_moves = []

            for d in directions:
                nt = current_tile + d
                if self.can_enter_tile(maze, int(nt.x), int(nt.y)):
                    if d + self.dir == pygame.Vector2(0, 0):
                        reverse_moves.append(d)
                    else:
                        valid_moves.append(d)

            if not valid_moves:
                valid_moves = reverse_moves

            if valid_moves:
                if self.mode == "FRIGHTENED":
                    # Random branching paths during Frightened mode
                    self.dir = random.choice(valid_moves)
                elif self.mode == "CHASE":
                    chase_moves = valid_moves + [m for m in reverse_moves if not any(m == v for v in valid_moves)]
                    path_dir = self.get_path_direction(maze, current_tile, player.get_tile(), chase_moves)
                    if path_dir:
                        self.dir = path_dir
                    else:
                        self.dir = chase_moves[0]
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

        next_tile = current_tile + self.dir
        is_at_turn_point = near_tile_center and moving_toward_center
        if is_at_turn_point and not self.can_enter_tile(maze, int(next_tile.x), int(next_tile.y)):
            self.dir *= -1

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
            size = int(TILE_SIZE * 1.45)
            scaled = pygame.transform.smoothscale(self.sprite, (size, size))
            screen.blit(scaled, (gx - scaled.get_width() // 2, gy - scaled.get_height() // 2))
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
