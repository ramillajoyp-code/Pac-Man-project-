# ui.py
import pygame
import os
import time
from maze import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE

class HUD:
    def __init__(self):
        # Try to load custom arcade font, fallback to system font
        self.small_font = None
        self.font = None
        self.medium_font = None
        self.large_font = None
        self.extra_small_font = None
        
        font_path = os.path.join("assets", "fonts", "arcade.ttf")
        if os.path.exists(font_path):
            try:
                self.small_font = pygame.font.Font(font_path, 16)
                self.font = pygame.font.Font(font_path, 20)
                self.medium_font = pygame.font.Font(font_path, 24)
                self.large_font = pygame.font.Font(font_path, 32)
                self.extra_small_font = pygame.font.Font(font_path, 12)
            except Exception:
                pass
        
        # Fallback to standard monospaced text
        if not self.small_font:
            self.small_font = pygame.font.SysFont("Verdana", 16, bold=True)
        if not self.font:
            self.font = pygame.font.SysFont("Verdana", 20, bold=True)
        if not self.medium_font:
            self.medium_font = pygame.font.SysFont("Verdana", 24, bold=True)
        if not self.large_font:
            self.large_font = pygame.font.SysFont("Verdana", 32, bold=True)
        if not self.extra_small_font:
            self.extra_small_font = pygame.font.SysFont("Verdana", 12, bold=True)

    def draw(self, screen, score, high_score, lives, level, state, state_timer=0):
        # Only show HUD elements when not in START_MENU
        if state != "START_MENU":
            # 1UP Header Elements
            score_lbl = self.font.render("1UP", True, (255, 255, 255))
            score_val = self.font.render(str(score).zfill(6), True, (255, 255, 255))
            screen.blit(score_lbl, (4, 20))
            screen.blit(score_val, (4, 40))

            # HIGH SCORE Top Anchors
            hs_lbl = self.font.render("HIGH SCORE", True, (255, 255, 255))
            hs_val = self.font.render(str(high_score).zfill(6), True, (255, 255, 255))
            screen.blit(hs_lbl, (SCREEN_WIDTH - 200, 20))
            screen.blit(hs_val, (SCREEN_WIDTH - 170, 40))

            # Footer Health/Level indicators
            for i in range(lives):
                lx = 30 + (i * TILE_SIZE * 1.5)
                ly = 36 * TILE_SIZE + 15
                pygame.draw.circle(screen, (255, 255, 0), (int(lx), int(ly)), TILE_SIZE // 2)
                # Give footer tracking circles classic open mouths
                pygame.draw.polygon(screen, (0, 0, 0), [(lx, ly), (lx + 15, ly - 8), (lx + 15, ly + 8)])

            # Level Tracker Items
            lbl_text = self.font.render(f"LVL: {level}", True, (255, 255, 0))
            screen.blit(lbl_text, (SCREEN_WIDTH - 120, 36 * TILE_SIZE + 10))

        # Screen Overlays (START/READY/GAME OVER)
        if state == "START_MENU":
            # Draw dark blue background for Pac-Man style
            pygame.draw.rect(screen, (0, 0, 50), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
            
            # Draw decorative border
            border_color = (255, 255, 0)
            border_thickness = 4
            border_margin = 20
            pygame.draw.rect(screen, border_color, (border_margin, border_margin, SCREEN_WIDTH - border_margin * 2, SCREEN_HEIGHT - border_margin * 2), border_thickness)
            
            # Title - large, centered at top with Pac-Man yellow
            title_text = self.large_font.render("GHOST CHASE", True, (255, 255, 0))
            title_x = SCREEN_WIDTH // 2 - title_text.get_width() // 2
            title_y = border_margin + 30
            screen.blit(title_text, (title_x, title_y))
            
            # Interactive subtitle
            sub_text = self.font.render("INTERACTIVE", True, (255, 255, 0))
            sub_x = SCREEN_WIDTH // 2 - sub_text.get_width() // 2
            sub_y = title_y + 40
            screen.blit(sub_text, (sub_x, sub_y))
            
            # Decorative Pac-Man style dots line
            dot_y = sub_y + 30
            for i in range(12):
                dot_x = border_margin + 30 + i * 40
                pygame.draw.circle(screen, (255, 255, 255), (dot_x, dot_y), 4)
            
            # High Score Display - centered
            hs_lbl = self.font.render("HIGH SCORE", True, (255, 0, 255))
            hs_lbl_x = SCREEN_WIDTH // 2 - hs_lbl.get_width() // 2
            hs_val = self.font.render(str(high_score).zfill(6), True, (255, 0, 255))
            hs_val_x = SCREEN_WIDTH // 2 - hs_val.get_width() // 2
            hs_y = dot_y + 40
            screen.blit(hs_lbl, (hs_lbl_x, hs_y))
            screen.blit(hs_val, (hs_val_x, hs_y + 25))
            
            # Controls - Pac-Man style with better spacing
            controls_start_y = hs_y + 45
            controls = [
                ("ARROW KEYS TO MOVE", controls_start_y),
                ("EAT ALL PELLETS", controls_start_y + 35),
                ("AVOID THE GHOSTS", controls_start_y + 70)
            ]
            
            for control_text, y_pos in controls:
                text = self.font.render(control_text, True, (255, 255, 255))
                text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
                screen.blit(text, (text_x, y_pos))
            
            # Decorative bottom dots
            bottom_dot_y = controls_start_y + 110
            for i in range(12):
                dot_x = border_margin + 30 + i * 40
                pygame.draw.circle(screen, (255, 255, 255), (dot_x, bottom_dot_y), 4)
            
            # Start instruction with blinking effect - centered at bottom
            blink = int(time.time() * 2) % 2
            blink_color = (0, 255, 0) if blink else (0, 100, 0)
            s_text = self.medium_font.render("PRESS SPACE TO START", True, blink_color)
            s_x = SCREEN_WIDTH // 2 - s_text.get_width() // 2
            s_y = SCREEN_HEIGHT - border_margin - 40
            screen.blit(s_text, (s_x, s_y))
        
        elif state == "COUNTDOWN":
            countdown_num = max(1, int(state_timer) + 1)
            countdown_text = self.large_font.render(str(countdown_num), True, (255, 255, 0))
            screen.blit(countdown_text, (SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, 20 * TILE_SIZE - 12))
            
        elif state == "READY":
            r_text = self.large_font.render("READY!", True, (255, 255, 0))
            screen.blit(r_text, (SCREEN_WIDTH // 2 - r_text.get_width() // 2, 20 * TILE_SIZE - 12))
            
        elif state == "GAME_OVER":
            go_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
            screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 20 * TILE_SIZE - 12))
            restart_text = self.font.render("PRESS SPACE TO RESTART", True, (255, 255, 255))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 22 * TILE_SIZE))
            
        elif state == "PAUSED":
            p_text = self.large_font.render("PAUSED", True, (0, 255, 255))
            screen.blit(p_text, (SCREEN_WIDTH // 2 - p_text.get_width() // 2, 20 * TILE_SIZE - 12))