import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 720
TILE = 30
FPS = 60

BLACK = (0,0,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
YELLOW = (255,255,0)
RED = (255,0,0)
PINK = (255,105,180)
CYAN = (0,255,255)
ORANGE = (255,165,0)

DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

FRIGHT_TIME = 90
RESPAWN_INVINCIBILITY = 90
