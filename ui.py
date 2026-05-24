import pygame
from settings import *

pygame.font.init()

FONT = pygame.font.SysFont("Arial", 26)
BIG = pygame.font.SysFont("Arial", 60)

def draw_text(screen, text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))
