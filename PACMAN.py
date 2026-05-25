
import pygame
import random
import sys

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
pygame.mixer.init()
pygame.mixer.set_num_channels(8)

WIDTH, HEIGHT = 900, 720
TILE = 30
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 24, bold=True)
BIG = pygame.font.SysFont("Impact", 60)

BLACK = (0,0,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
YELLOW = (255,255,0)
RED = (255,0,0)
PINK = (255,105,180)
CYAN = (0,255,255)
ORANGE = (255,165,0)

DIRS = [(1,0),(-1,0),(0,1),(0,-1)]

STATE = "MENU"
PAUSED = False
bgm_started = False

try:
    sound_bgm = pygame.mixer.Sound("bgm.wav")
    sound_win = pygame.mixer.Sound("win.wav")
    sound_power_pellet = pygame.mixer.Sound("power_pellet.wav")
    sound_pellet = pygame.mixer.Sound("pellet.wav")
    sound_ghost_eaten = pygame.mixer.Sound("ghost_eaten.wav")
    sound_death = pygame.mixer.Sound("death.wav")
    sound_intro = pygame.mixer.Sound("intro.wav")  
    
    sound_bgm.set_volume(0.2)
    sound_pellet.set_volume(0.3)
    sound_power_pellet.set_volume(0.4)
    sound_ghost_eaten.set_volume(0.6)
    sound_death.set_volume(0.5)
    sound_win.set_volume(0.5)
    sound_intro.set_volume(0.5)

except pygame.error as e:
    print(f"Audio loading warning: {e}")
    print("Running in silent fallback mode. Verify file placements!")

    class DummySound:
        def play(self, *args, **kwargs):
            pass

        def stop(self):
            pass

    sound_bgm = sound_win = sound_power_pellet = sound_pellet = DummySound()
    sound_ghost_eaten = sound_death = sound_intro = DummySound()

BASE_MAP = [
    "WWWWWWWWWWWWWWWWWWWWWWW",
    "W....W.......W.......W",
    "W.WW.W.WWWWW.W.WWW.W.W",
    "W.W..W...P...W...W..W.W",
    "W.WW.WWW.WWW.WWW.WW.W.W",
    "W.....................W",
    "W.WWWWW.WWWWWWW.WWWWW.W",
    "W.....W.........W.....W",
    "W.WWW.W.WWWWW.W.WWW.W.W",
    "W..P..W...W...W...W..PW",
    "WWWWWWWWWWWWWWWWWWWWWWW"
]

def copy_map():
    return [list(r) for r in BASE_MAP]

def is_wall(x, y):
    if y < 0 or y >= len(MAP):
        return True
    if x < 0 or x >= len(MAP[0]):
        return True
    return MAP[y][x] == "W"

class Player:
    def __init__(self):
        self.spawn = (1, 1)
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

        dx, dy = 0, 0

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
            sound_pellet.play()

        elif MAP[self.y][self.x] == "P":
            self.score += 50
            self.power = FRIGHT_TIME
            MAP[self.y][self.x] = " "
            sound_power_pellet.play()

    def draw(self):
        pygame.draw.circle(
            screen,
            YELLOW,
            (self.x * TILE + 15, self.y * TILE + 15),
            12
        )

class Ghost:
    def __init__(self, x, y, color):
        self.start = (x, y)
        self.base_color = color
        self.reset()

    def reset(self):
        self.x, self.y = self.start
        self.timer = 0
        self.delay = 13
        self.color = self.base_color

    def valid_moves(self):
        moves = []

        for d in DIRS:
            nx, ny = self.x + d[0], self.y + d[1]

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
            nx, ny = self.x + d[0], self.y + d[1]

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

    def draw(self):
        pygame.draw.circle(
            screen,
            self.color,
            (self.x * TILE + 15, self.y * TILE + 15),
            12
        )

def reset_game():
    global MAP, player, ghosts, STATE, PAUSED

    sound_win.stop()

    MAP = copy_map()

    player.reset()

    ghosts = [
        Ghost(10,5,RED),
        Ghost(11,5,PINK),
        Ghost(12,5,CYAN),
        Ghost(13,5,ORANGE)
    ]

    PAUSED = False
    STATE = "PLAY"

MAP = copy_map()

player = Player()

ghosts = [
    Ghost(10,5,RED),
    Ghost(11,5,PINK),
    Ghost(12,5,CYAN),
    Ghost(13,5,ORANGE)
]

pygame.mixer.Channel(0).play(sound_intro)

def check_win():
    for row in MAP:
        if "." in row or "P" in row:
            return False

    return True

running = True

FRIGHT_TIME = 120
RESPAWN_INVINCIBILITY = 90

while running:
    clock.tick(FPS)

    screen.fill(BLACK)

    keys = pygame.key.get_pressed()

    if (
        not pygame.mixer.Channel(0).get_busy()
        and not bgm_started
        and not PAUSED
    ):
        pygame.mixer.Channel(0).play(sound_bgm, loops=-1)
        bgm_started = True

    for e in pygame.event.get():

        if e.type == pygame.QUIT:
            running = False

        if e.type == pygame.KEYDOWN:

            if STATE == "MENU" and e.key == pygame.K_RETURN:
                reset_game()

            elif STATE == "PLAY" and e.key == pygame.K_p:
                PAUSED = not PAUSED

                if PAUSED:
                    pygame.mixer.Channel(0).pause()
                else:
                    pygame.mixer.Channel(0).unpause()

            elif STATE in ("WIN", "GAMEOVER"):

                if e.key == pygame.K_r:
                    bgm_started = False
                    pygame.mixer.Channel(0).play(sound_intro)
                    reset_game()

                if e.key == pygame.K_q:
                    sound_win.stop()
                    bgm_started = False
                    pygame.mixer.Channel(0).play(sound_intro)
                    STATE = "MENU"

    if STATE == "PLAY":

        if PAUSED:
            screen.blit(BIG.render("PAUSED", True, WHITE), (320,300))
            pygame.display.update()
            continue

        for y, row in enumerate(MAP):

            for x, c in enumerate(row):

                if c == "W":
                    pygame.draw.rect(
                        screen,
                        BLUE,
                        (x * TILE, y * TILE, TILE, TILE)
                    )

                elif c == ".":
                    pygame.draw.circle(
                        screen,
                        WHITE,
                        (x * TILE + 15, y * TILE + 15),
                        4
                    )

                elif c == "P":
                    pygame.draw.circle(
                        screen,
                        WHITE,
                        (x * TILE + 15, y * TILE + 15),
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
                    sound_ghost_eaten.play()

                else:
                    if player.invincible == 0:
                        player.lives -= 1
                        sound_death.play()

                        if player.lives <= 0:
                            pygame.mixer.Channel(0).stop()
                            STATE = "GAMEOVER"

                        else:
                            player.respawn()

        player.draw()

        for g in ghosts:
            g.draw()

        screen.blit(
            FONT.render(
                f"SCORE: {player.score}  LIVES: {player.lives}",
                True,
                WHITE
            ),
            (10, 680)
        )

        if check_win():
            pygame.mixer.Channel(0).stop()
            sound_win.play()
            STATE = "WIN"

    elif STATE == "MENU":
        screen.blit(BIG.render("PAC-MAN", True, YELLOW), (320, 200))
        screen.blit(
            FONT.render("PRESS ENTER TO PLAY", True, WHITE),
            (320, 320)
        )

    elif STATE == "WIN":
        screen.blit(BIG.render("YOU WIN!", True, WHITE), (320, 250))
        screen.blit(
            FONT.render("R=RESTART  Q=MENU", True, WHITE),
            (320, 370)
        )

    elif STATE == "GAMEOVER":
        screen.blit(BIG.render("GAME OVER", True, RED), (300, 250))
        screen.blit(
            FONT.render("R=RESTART  Q=MENU", True, WHITE),
            (320, 370)
        )

    pygame.display.update()

pygame.quit()
sys.exit()
