import pygame
from settings import *
from maze import MAP, is_wall

class Player:

    def __init__(self):
        self.spawn = (1,1)
        self.reset()

    def reset(self):
        self.x, self.y = self.spawn
        self.timer = 0
        self.delay = 5
        self.score = 0
        self.lives = 3
        self.power = 0
        self.invincible = 0

    def respawn(self):
        self.x, self.y = self.spawn
        self.invincible = RESPAWN_INVINCIBILITY
        self.power = 0

    def update(self, keys):

        if self.invincible > 0:
            self.invincible -= 1

        self.timer += 1

        if self.timer < self.delay:
            return

        self.timer = 0

        dx, dy = 0,0

        if keys[pygame.K_LEFT]:
            dx = -1

        elif keys[pygame.K_RIGHT]:
            dx = 1

        elif keys[pygame.K_UP]:
            dy = -1

        elif keys[pygame.K_DOWN]:
            dy = 1

        nx, ny = self.x + dx, self.y + dy

        if not is_wall(nx, ny):
            self.x, self.y = nx, ny

        if self.power > 0:
            self.power -= 1

        self.eat()

    def eat(self):

        if MAP[self.y][self.x] == ".":
            self.score += 10
            MAP[self.y][self.x] = " "

        elif MAP[self.y][self.x] == "P":
            self.score += 50
            self.power = FRIGHT_TIME
            MAP[self.y][self.x] = " "

    def draw(self, screen):
        pygame.draw.circle(
            screen,
            YELLOW,
            (self.x*TILE+15, self.y*TILE+15),
            12
        )
