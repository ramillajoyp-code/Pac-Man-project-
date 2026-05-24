import pygame
import sys

from settings import *
from maze import *
from player import Player
from ghost import Ghost
from ui import *

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

STATE = "MENU"
PAUSED = False

player = Player()

ghosts = [
    Ghost(10,5,RED),
    Ghost(11,5,PINK),
    Ghost(12,5,CYAN),
    Ghost(13,5,ORANGE)
]

def reset_game():

    global MAP, player, ghosts, STATE, PAUSED

    MAP[:] = copy_map()

    player.reset()

    ghosts = [
        Ghost(10,5,RED),
        Ghost(11,5,PINK),
        Ghost(12,5,CYAN),
        Ghost(13,5,ORANGE)
    ]

    PAUSED = False
    STATE = "PLAY"

running = True

while running:

    clock.tick(FPS)

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:

            if STATE == "MENU":

                if e.key == pygame.K_RETURN:
                    reset_game()

            elif STATE == "PLAY":

                if e.key == pygame.K_p:
                    PAUSED = not PAUSED

            elif STATE in ("WIN", "GAMEOVER"):

                if e.key == pygame.K_r:
                    reset_game()

                if e.key == pygame.K_q:
                    STATE = "MENU"

    if STATE == "PLAY":

        if PAUSED:
            draw_text(screen, "PAUSED", BIG, WHITE, 340, 300)
            pygame.display.update()
            continue

        for y, row in enumerate(MAP):

            for x, c in enumerate(row):

                if c == "W":

                    pygame.draw.rect(
                        screen,
                        BLUE,
                        (x*TILE, y*TILE, TILE, TILE)
                    )

                elif c == ".":

                    pygame.draw.circle(
                        screen,
                        WHITE,
                        (x*TILE+15, y*TILE+15),
                        4
                    )

                elif c == "P":

                    pygame.draw.circle(
                        screen,
                        WHITE,
                        (x*TILE+15, y*TILE+15),
                        8
                    )

        player.update(keys)

        reserved = set()

        for g in ghosts:
            g.update(player, reserved)
            reserved.add((g.x, g.y))

        for g in ghosts:

            if g.x == player.x and g.y == player.y:

                if player.power > 0:

                    g.reset()
                    player.score += 200

                else:

                    if player.invincible == 0:

                        player.lives -= 1
                        player.respawn()

                        if player.lives <= 0:
                            STATE = "GAMEOVER"

        player.draw(screen)

        for g in ghosts:
            g.draw(screen)

        draw_text(
            screen,
            f"Score: {player.score} Lives: {player.lives}",
            FONT,
            WHITE,
            10,
            680
        )

        if check_win():
            STATE = "WIN"

    elif STATE == "MENU":

        draw_text(screen, "PAC-MAN", BIG, YELLOW, 320, 200)
        draw_text(screen, "ENTER TO PLAY", FONT, WHITE, 320, 300)

    elif STATE == "WIN":

        draw_text(screen, "YOU WIN!", BIG, WHITE, 300, 250)
        draw_text(screen, "R=Restart  Q=Menu", FONT, WHITE, 300, 350)

    elif STATE == "GAMEOVER":

        draw_text(screen, "GAME OVER", BIG, WHITE, 250, 250)
        draw_text(screen, "R=Restart  Q=Menu", FONT, WHITE, 300, 350)

    pygame.display.update()

pygame.quit()
sys.exit()
