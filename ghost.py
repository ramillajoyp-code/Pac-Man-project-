import pygame
import random

from settings import *
from maze import is_wall

class Ghost:

    def __init__(self, x, y, color):
        self.start = (x, y)
        self.base_color = color
        self.reset()

    def reset(self):
        self.x, self.y = self.start
        self.timer = 0
        self.delay = 10
        self.color = self.base_color

    def valid_moves(self):

        moves = []

        for d in DIRS:

            nx = self.x + d[0]
            ny = self.y + d[1]

            if not is_wall(nx, ny):
                moves.append(d)

        return moves

    def update(self, player, reserved):

        frightened = player.power > 0

        self.color = BLUE if frightened else self.base_color

        self.timer += 1

        if self.timer < self.delay:
            return

        self.timer = 0

        moves = self.valid_moves()

        if not moves:
            return

        best_move = None
        best_score = -99999

        for d in moves:

            nx = self.x + d[0]
            ny = self.y + d[1]

            if (nx, ny) in reserved:
                continue

            dist = abs(nx - player.x) + abs(ny - player.y)

            if frightened:
                score = dist
            else:
                score = -dist

            score += random.uniform(-0.5, 0.5)

            if score > best_score:
                best_score = score
                best_move = d

        if best_move:
            self.x += best_move[0]
            self.y += best_move[1]

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            self.color,
            (self.x*TILE+15, self.y*TILE+15),
            12
        )
