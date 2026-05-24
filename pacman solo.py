import pygame
import random
import sys

pygame.init()

WIDTH, HEIGHT = 900, 720
TILE = 30
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("Arial", 26)
BIG = pygame.font.SysFont("Arial", 60)

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

# ================= SETTINGS =================
FRIGHT_TIME = 90
RESPAWN_INVINCIBILITY = 90  # prevents instant double-hit

# ---------------- MAP ----------------
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
    if y < 0 or y >= len(MAP): return True
    if x < 0 or x >= len(MAP[0]): return True
    return MAP[y][x] == "W"

# ---------------- PLAYER ----------------
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
        # ONLY position reset, NOT full reset
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
        if keys[pygame.K_LEFT]: dx = -1
        elif keys[pygame.K_RIGHT]: dx = 1
        elif keys[pygame.K_UP]: dy = -1
        elif keys[pygame.K_DOWN]: dy = 1

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

    def draw(self):
        pygame.draw.circle(screen, YELLOW,
                           (self.x*TILE+15, self.y*TILE+15), 12)

# ---------------- GHOST ----------------
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
            nx, ny = self.x + d[0], self.y + d[1]
            if not is_wall(nx, ny):
                moves.append(d)
        return moves

    # 🔥 IMPROVED AI (less random, more consistent chase)
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

            # frightened = run away
            if frightened:
                score = dist  # maximize distance
            else:
                score = -dist  # minimize distance (chase)

            # slight randomness so they don't stack perfectly
            score += random.uniform(-0.5, 0.5)

            if score > best_score:
                best_score = score
                best_move = d

        if best_move:
            self.x += best_move[0]
            self.y += best_move[1]

    def draw(self):
        pygame.draw.circle(screen, self.color,
                           (self.x*TILE+15, self.y*TILE+15), 12)

# ---------------- RESET GAME ----------------
def reset_game():
    global MAP, player, ghosts, STATE, PAUSED

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

# ---------------- INIT ----------------
MAP = copy_map()
player = Player()

ghosts = [
    Ghost(10,5,RED),
    Ghost(11,5,PINK),
    Ghost(12,5,CYAN),
    Ghost(13,5,ORANGE)
]

def check_win():
    for row in MAP:
        if "." in row:
            return False
    return True

# ---------------- GAME LOOP ----------------
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

    # ---------------- PLAY ----------------
    if STATE == "PLAY":

        if PAUSED:
            screen.blit(BIG.render("PAUSED", True, WHITE), (340,300))
            pygame.display.update()
            continue

        # draw map
        for y, row in enumerate(MAP):
            for x, c in enumerate(row):
                if c == "W":
                    pygame.draw.rect(screen, BLUE, (x*TILE, y*TILE, TILE, TILE))
                elif c == ".":
                    pygame.draw.circle(screen, WHITE, (x*TILE+15, y*TILE+15), 4)
                elif c == "P":
                    pygame.draw.circle(screen, WHITE, (x*TILE+15, y*TILE+15), 8)

        player.update(keys)

        reserved = set()

        # ghost movement
        for g in ghosts:
            g.update(player, reserved)
            reserved.add((g.x, g.y))

        # ================= COLLISION FIX =================
        for g in ghosts:
            if g.x == player.x and g.y == player.y:

                if player.power > 0:
                    g.reset()
                    player.score += 200
                else:
                    # only lose life ONCE per hit
                    if player.invincible == 0:
                        player.lives -= 1
                        player.respawn()  # ✅ FIX: proper respawn

                        if player.lives <= 0:
                            STATE = "GAMEOVER"

        player.draw()
        for g in ghosts:
            g.draw()

        screen.blit(FONT.render(
            f"Score: {player.score} Lives: {player.lives}",
            True, WHITE
        ), (10, 680))

        if check_win():
            STATE = "WIN"

    # ---------------- MENU ----------------
    elif STATE == "MENU":
        screen.blit(BIG.render("PAC-MAN", True, YELLOW), (320, 200))
        screen.blit(FONT.render("ENTER TO PLAY", True, WHITE), (320, 300))

    # ---------------- WIN ----------------
    elif STATE == "WIN":
        screen.blit(BIG.render("YOU WIN!", True, WHITE), (300, 250))
        screen.blit(FONT.render("R=Restart  Q=Menu", True, WHITE), (300, 350))

    # ---------------- GAME OVER ----------------
    elif STATE == "GAMEOVER":
        screen.blit(BIG.render("GAME OVER", True, WHITE), (250, 250))
        screen.blit(FONT.render("R=Restart  Q=Menu", True, WHITE), (300, 350))

    pygame.display.update()

pygame.quit()
sys.exit()
