# map_theme.py
import pygame
import os
import time
from maze import SCREEN_WIDTH, SCREEN_HEIGHT

THEME_FILE = "maze_theme.txt"

# Each entry colors the maze walls/border, the ghost-house gate, the ghost
# cage outline, the overall background wash, and the regular/power pellets.
MAP_THEMES = [
    {
        "id": "grassy_plain", "name": "GRASSY PLAIN",
        "wall_color": (74, 145, 45), "wall_border_color": (174, 218, 96),
        "wall_accent_color": (38, 104, 35),
        "gate_color": (221, 185, 92), "cage_color": (105, 154, 78),
        "bg_color": (9, 35, 18),
        "pellet_color": (244, 232, 169), "power_pellet_color": (255, 246, 190),
        "blurb": "SOFT MEADOW WALLS",
    },
    {
        "id": "classic", "name": "CLASSIC ARCADE",
        "wall_color": (33, 33, 222), "wall_border_color": (66, 66, 255),
        "gate_color": (255, 184, 255), "cage_color": (200, 100, 200),
        "bg_color": (0, 0, 0),
        "pellet_color": (255, 184, 174), "power_pellet_color": (255, 184, 174),
        "blurb": "THE ORIGINAL BLUE MAZE",
    },
    {
        "id": "neon_pink", "name": "NEON NIGHTS",
        "wall_color": (200, 0, 130), "wall_border_color": (255, 60, 180),
        "gate_color": (0, 255, 255), "cage_color": (255, 20, 147),
        "bg_color": (8, 0, 18),
        "pellet_color": (0, 255, 255), "power_pellet_color": (255, 255, 0),
        "blurb": "SYNTHWAVE MAZE",
    },
    {
        "id": "matrix", "name": "DIGITAL RAIN",
        "wall_color": (0, 70, 0), "wall_border_color": (0, 255, 70),
        "gate_color": (0, 255, 0), "cage_color": (0, 150, 0),
        "bg_color": (0, 5, 0),
        "pellet_color": (0, 255, 70), "power_pellet_color": (0, 255, 70),
        "blurb": "ENTER THE CODE",
    },
    {
        "id": "inferno", "name": "INFERNO",
        "wall_color": (130, 20, 0), "wall_border_color": (255, 87, 34),
        "gate_color": (255, 200, 0), "cage_color": (200, 60, 0),
        "bg_color": (18, 0, 0),
        "pellet_color": (255, 160, 0), "power_pellet_color": (255, 200, 0),
        "blurb": "TURN UP THE HEAT",
    },
    {
        "id": "frostbite", "name": "FROSTBITE",
        "wall_color": (20, 60, 120), "wall_border_color": (140, 220, 255),
        "gate_color": (255, 255, 255), "cage_color": (100, 180, 255),
        "bg_color": (0, 8, 24),
        "pellet_color": (200, 240, 255), "power_pellet_color": (255, 255, 255),
        "blurb": "COOL BLUE MAZE",
    },
    {
        "id": "royal", "name": "ROYAL GOLD",
        "wall_color": (55, 0, 85), "wall_border_color": (190, 100, 255),
        "gate_color": (255, 215, 0), "cage_color": (140, 60, 180),
        "bg_color": (8, 0, 18),
        "pellet_color": (255, 215, 0), "power_pellet_color": (255, 255, 255),
        "blurb": "FIT FOR A KING",
    },
    {
        "id": "monochrome", "name": "MONOCHROME",
        "wall_color": (55, 55, 55), "wall_border_color": (190, 190, 190),
        "gate_color": (255, 255, 255), "cage_color": (120, 120, 120),
        "bg_color": (0, 0, 0),
        "pellet_color": (225, 225, 225), "power_pellet_color": (255, 255, 255),
        "blurb": "BLACK & WHITE CLASSIC",
    },
    {
        "id": "toxic", "name": "TOXIC WASTE",
        "wall_color": (35, 85, 5), "wall_border_color": (170, 255, 0),
        "gate_color": (255, 0, 255), "cage_color": (90, 140, 0),
        "bg_color": (4, 14, 0),
        "pellet_color": (170, 255, 0), "power_pellet_color": (255, 0, 255),
        "blurb": "RADIOACTIVE GLOW",
    },
]


def load_map_theme():
    """Load the previously equipped maze theme from disk, defaulting to CLASSIC."""
    if os.path.exists(THEME_FILE):
        try:
            with open(THEME_FILE, "r") as f:
                saved_id = f.read().strip()
            for theme in MAP_THEMES:
                if theme["id"] == saved_id:
                    return theme
        except Exception:
            pass
    return MAP_THEMES[0]


def save_map_theme(theme_id):
    try:
        with open(THEME_FILE, "w") as f:
            f.write(theme_id)
    except Exception:
        pass


def render_theme_swatch(theme, size=90):
    """Render a small stylized maze-corner preview swatch for a theme."""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)

    pygame.draw.rect(surf, theme["bg_color"], (0, 0, size, size), border_radius=10)
    pygame.draw.rect(surf, theme["wall_border_color"], (0, 0, size, size), 3, border_radius=10)

    block = size // 5
    pad = 4

    # A small L-shaped cluster of walls, evoking a maze corner
    wall_cells = [(0, 0), (1, 0), (2, 0), (0, 1), (0, 2)]
    for (cx, cy) in wall_cells:
        x = pad + cx * block
        y = pad + cy * block
        w = block - 3
        pygame.draw.rect(surf, theme["wall_color"], (x, y, w, w))
        accent = theme.get("wall_accent_color")
        if accent:
            pygame.draw.line(surf, accent, (x + w // 2, y + w - 4), (x + w // 2 - 2, y + 5), 1)
            pygame.draw.line(surf, accent, (x + w // 2 + 4, y + w - 5), (x + w // 2 + 6, y + 6), 1)
        pygame.draw.rect(surf, theme["wall_border_color"], (x, y, w, w), 1)

    # Ghost-house gate sliver
    gate_w = int(block * 1.6)
    gate_y = pad + 2 * block + block // 2 - 2
    pygame.draw.rect(surf, theme["gate_color"], (size - gate_w - pad, gate_y, gate_w, 4))

    # Scattered pellets
    for i in range(3):
        px = pad + block * 2 + 8 + i * 9
        py = size - 14
        pygame.draw.circle(surf, theme["pellet_color"], (px, py), 2)

    # Power pellet
    pygame.draw.circle(surf, theme["power_pellet_color"], (size - 16, 18), 6)

    return surf


class MapTheme:
    """A character-select style carousel for choosing the maze color theme."""

    def __init__(self):
        self._setup_fonts()

        equipped = load_map_theme()
        self.equipped_id = equipped["id"]
        self.index = 0
        for i, theme in enumerate(MAP_THEMES):
            if theme["id"] == self.equipped_id:
                self.index = i
                break

    def _setup_fonts(self):
        font_path = os.path.join("assets", "fonts", "arcade.ttf")
        loaded = False
        if os.path.exists(font_path):
            try:
                self.font = pygame.font.Font(font_path, 18)
                self.medium_font = pygame.font.Font(font_path, 24)
                self.large_font = pygame.font.Font(font_path, 30)
                self.small_font = pygame.font.Font(font_path, 14)
                loaded = True
            except Exception:
                loaded = False
        if not loaded:
            self.font = pygame.font.SysFont("Verdana", 18, bold=True)
            self.medium_font = pygame.font.SysFont("Verdana", 24, bold=True)
            self.large_font = pygame.font.SysFont("Verdana", 30, bold=True)
            self.small_font = pygame.font.SysFont("Verdana", 14, bold=True)

    def handle_input(self, event):
        """Returns ("CONFIRM", theme_dict) on equip, ("BACK", None) on cancel,
        or None if the event wasn't relevant."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_LEFT:
            self.index = (self.index - 1) % len(MAP_THEMES)
        elif event.key == pygame.K_RIGHT:
            self.index = (self.index + 1) % len(MAP_THEMES)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            theme = MAP_THEMES[self.index]
            save_map_theme(theme["id"])
            self.equipped_id = theme["id"]
            return ("CONFIRM", theme)
        elif event.key == pygame.K_ESCAPE:
            return ("BACK", None)

        return None

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill((0, 0, 35))

        border_color = (255, 255, 0)
        border_margin = 20
        pygame.draw.rect(
            screen, border_color,
            (border_margin, border_margin,
             SCREEN_WIDTH - border_margin * 2, SCREEN_HEIGHT - border_margin * 2),
            4
        )

        title = self.large_font.render("CHOOSE YOUR MAZE", True, (255, 255, 0))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, border_margin + 30))

        top_dot_y = border_margin + 80
        for i in range(12):
            dot_x = border_margin + 30 + i * 40
            pygame.draw.circle(screen, (255, 255, 255), (dot_x, top_dot_y), 3)

        # --- Carousel of themes, center one large, neighbors faded ---
        center_y = 300
        spacing = 100
        offsets = [-2, -1, 0, 1, 2]

        for offset in offsets:
            idx = (self.index + offset) % len(MAP_THEMES)
            theme = MAP_THEMES[idx]
            is_center = offset == 0

            if is_center:
                size, alpha = 92, 255
            elif abs(offset) == 1:
                size, alpha = 60, 170
            else:
                size, alpha = 36, 80

            swatch = render_theme_swatch(theme, size=size)
            swatch.set_alpha(alpha)
            x = SCREEN_WIDTH // 2 + offset * spacing
            screen.blit(swatch, (x - swatch.get_width() // 2, center_y - swatch.get_height() // 2))

        # Browse arrows flanking the carousel
        arrow_color = (255, 255, 255)
        left_arrow = self.medium_font.render("<", True, arrow_color)
        right_arrow = self.medium_font.render(">", True, arrow_color)
        screen.blit(left_arrow, (SCREEN_WIDTH // 2 - spacing * 2 - 30, center_y - 14))
        screen.blit(right_arrow, (SCREEN_WIDTH // 2 + spacing * 2 + 12, center_y - 14))

        # Name + blurb + equipped badge
        current = MAP_THEMES[self.index]
        name_text = self.medium_font.render(current["name"], True, current["wall_border_color"])
        screen.blit(name_text, (SCREEN_WIDTH // 2 - name_text.get_width() // 2, center_y + 80))

        blurb_text = self.small_font.render(current["blurb"], True, (200, 200, 200))
        screen.blit(blurb_text, (SCREEN_WIDTH // 2 - blurb_text.get_width() // 2, center_y + 110))

        if current["id"] == self.equipped_id:
            eq_text = self.small_font.render("* EQUIPPED *", True, (0, 255, 0))
            screen.blit(eq_text, (SCREEN_WIDTH // 2 - eq_text.get_width() // 2, center_y + 135))

        # Position indicator dots
        indicator_y = center_y + 175
        total_width = len(MAP_THEMES) * 18
        start_x = SCREEN_WIDTH // 2 - total_width // 2
        for i in range(len(MAP_THEMES)):
            cx = start_x + i * 18
            if i == self.index:
                pygame.draw.circle(screen, (255, 255, 0), (cx, indicator_y), 5)
            else:
                pygame.draw.circle(screen, (90, 90, 90), (cx, indicator_y), 3)

        bottom_dot_y = SCREEN_HEIGHT - border_margin - 190
        for i in range(12):
            dot_x = border_margin + 30 + i * 40
            pygame.draw.circle(screen, (255, 255, 255), (dot_x, bottom_dot_y), 3)

        # Instructions
        instructions = [
            "ARROW KEYS TO BROWSE",
            "ENTER / SPACE TO EQUIP",
            "ESC TO GO BACK",
        ]
        iy = SCREEN_HEIGHT - border_margin - 150
        for line in instructions:
            t = self.font.render(line, True, (255, 255, 255))
            screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, iy))
            iy += 30

        blink = int(time.time() * 2) % 2
        blink_color = (0, 255, 0) if blink else (0, 100, 0)
        hint = self.medium_font.render("PRESS ENTER TO CONFIRM", True, blink_color)
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - border_margin - 50))
