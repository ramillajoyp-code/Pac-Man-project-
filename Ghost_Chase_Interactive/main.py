# main.py
import pygame
import sys
import os
from maze import Maze, SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE
from player import PacMan
from ghost import Ghost
from pellets import PelletManager
from ui import HUD

class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ghost Chase Interactive")
        self.clock = pygame.time.Clock()
        
        self.maze = Maze()
        self.player = PacMan(14, 26)
        
        self.ghosts = [
            Ghost("BLINKY", 15, 17),
            Ghost("PINKY", 14, 17),
            Ghost("INKY", 13, 17),
            Ghost("CLYDE", 12, 17)
        ]
        
        self.pellet_manager = PelletManager(self.maze)
        self.hud = HUD()

        # Engine parameters
        self.score = 0
        self.high_score = self.load_high_score()
        self.lives = 3
        self.level = 1
        
        self.ghosts_eaten_combo = 0  # Track combo for bonus points
        
        # State machine configurations
        self.state = "START_MENU"
        self.state_timer = 0.0
        self.menu_sound_played = False
        
        # Transition effect
        self.transition_alpha = 0
        self.transition_active = False
        self.transition_direction = 0  # 1 for fade in, -1 for fade out
        
        # Mode cycle tracking (Classic Wave Timers)
        self.global_mode = "SCATTER"
        self.mode_timer = 0.0
        self.frightened_timer = 0.0
        
        # Maze blink effect tracking
        self.maze_blink_active = False
        self.maze_blink_timer = 0.0
        self.maze_blink_interval = 0.15  # Blink every 0.15 seconds
        
        self.load_audio_tracks()

    def load_high_score(self):
        if os.path.exists("highscore.txt"):
            try:
                with open("highscore.txt", "r") as f:
                    return int(f.read().strip())
            except Exception:
                return 0
        return 0

    def save_high_score(self):
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def load_audio_tracks(self):
        # Sound container loading setup
        self.sounds = {}
        tracks = ["intro", "pellet", "power_pellet", "ghost_eaten", "death", "bgm", "start_button", "countdown"]
        for t in tracks:
            path = os.path.join("assets", "sounds", f"{t}.wav")
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    self.sounds[t] = sound
                except Exception:
                    self.sounds[t] = None
            else:
                self.sounds[t] = None
        
        # Set BGM to loop
        self.bgm_playing = False

    def trigger_sound(self, name, loops=0):
        try:
            if name in self.sounds and self.sounds[name]:
                self.sounds[name].play(loops=loops)
        except Exception as e:
            # Prevent crash if sound playback fails
            pass

    def reset_positions(self):
        self.player.reset()
        for g in self.ghosts:
            g.reset()
        self.global_mode = "SCATTER"
        self.mode_timer = 0.0
        self.frightened_timer = 0.0
        self.fruit_active = False
        self.fruit_timer = 0
        self.ghosts_eaten_combo = 0
        pygame.mixer.stop()
        self.bgm_playing = False

    def run(self):
        while True:
            try:
                dt = self.clock.tick(60) / 1000.0  # Maintain stable 60 FPS
                self.handle_events()
                self.update(dt)
                self.render()
            except Exception as e:
                # Prevent crash if main loop fails
                pass

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_high_score()
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.KEYDOWN:
                if self.state == "START_MENU":
                    if event.key == pygame.K_SPACE:
                        self.trigger_sound("start_button")
                        self.transition_active = True
                        self.transition_direction = -1  # Fade out
                        self.transition_alpha = 0
                elif self.state == "COUNTDOWN":
                    # Allow player to start moving during countdown
                    if event.key == pygame.K_UP:    self.player.set_buffer_direction(0, -1)
                    if event.key == pygame.K_DOWN:  self.player.set_buffer_direction(0, 1)
                    if event.key == pygame.K_LEFT:  self.player.set_buffer_direction(-1, 0)
                    if event.key == pygame.K_RIGHT: self.player.set_buffer_direction(1, 0)
                elif self.state == "READY":
                    # Allow player to start moving during READY state
                    if event.key == pygame.K_UP:    self.player.set_buffer_direction(0, -1)
                    if event.key == pygame.K_DOWN:  self.player.set_buffer_direction(0, 1)
                    if event.key == pygame.K_LEFT:  self.player.set_buffer_direction(-1, 0)
                    if event.key == pygame.K_RIGHT: self.player.set_buffer_direction(1, 0)
                elif self.state == "PLAYING":
                    if event.key == pygame.K_UP:    self.player.set_buffer_direction(0, -1)
                    if event.key == pygame.K_DOWN:  self.player.set_buffer_direction(0, 1)
                    if event.key == pygame.K_LEFT:  self.player.set_buffer_direction(-1, 0)
                    if event.key == pygame.K_RIGHT: self.player.set_buffer_direction(1, 0)
                    if event.key == pygame.K_p:     self.state = "PAUSED"
                elif self.state == "PAUSED":
                    if event.key == pygame.K_p:     self.state = "PLAYING"
                elif self.state == "GAME_OVER":
                    if event.key == pygame.K_SPACE:
                        self.score = 0
                        self.lives = 3
                        self.level = 1
                        self.pellet_manager.load_pellets()
                        self.reset_positions()
                        self.state = "START_MENU"
                        self.state_timer = 0

    def update(self, dt):
        # Play menu sound when first entering START_MENU
        if self.state == "START_MENU" and not self.menu_sound_played:
            self.trigger_sound("intro")
            self.menu_sound_played = True
        
        # Handle transition effect
        if self.transition_active:
            self.transition_alpha += self.transition_direction * 300 * dt  # Fade speed
            if self.transition_direction == -1 and self.transition_alpha <= 255:
                self.transition_alpha = 255
                # Transition complete, switch state
                self.state = "COUNTDOWN"
                self.state_timer = 3.0
                self.transition_direction = 1  # Start fading in
            elif self.transition_direction == 1 and self.transition_alpha >= 0:
                self.transition_alpha = 0
                self.transition_active = False
        
        if self.state == "COUNTDOWN":
            self.state_timer -= dt
            # Play countdown beep at 3, 2, 1 seconds
            countdown_val = max(0, int(self.state_timer) + 1)
            if countdown_val in [3, 2, 1]:
                # Check if we just reached this countdown number
                prev_val = max(0, int(self.state_timer + dt) + 1)
                if countdown_val < prev_val:
                    self.trigger_sound("countdown")
            
            if self.state_timer <= 0:
                self.trigger_sound("intro")
                self.state = "READY"
                self.state_timer = 0.5
        
        elif self.state == "READY":
            self.state_timer -= dt
            # Show ready screen but allow player input for first move
            if self.state_timer <= 0:
                self.state = "PLAYING"
                
        elif self.state == "PLAYING":
            # Start BGM if not playing
            if not self.bgm_playing and self.sounds.get("bgm"):
                self.trigger_sound("bgm", loops=-1)
                self.bgm_playing = True
            
            try:
                self.pellet_manager.update(dt)
            except Exception as e:
                # Prevent crash if pellet manager update fails
                pass
            try:
                self.update_wave_timers(dt)
            except Exception as e:
                # Prevent crash if wave timer update fails
                pass
            
            # Update players and enemy targets
            try:
                self.player.update(self.maze)
            except Exception as e:
                # Prevent crash if player update fails
                pass
            try:
                blinky_tile = self.ghosts[0].get_tile()
                for g in self.ghosts:
                    g.update(self.maze, self.player, blinky_tile, self.global_mode)
            except Exception as e:
                # Prevent crash if ghost update fails
                pass
                
            try:
                self.process_collisions()
            except Exception as e:
                # Prevent crash if collision processing fails
                pass
            
        elif self.state == "DYING":
            # Update player to animate death
            self.player.update(self.maze)
            
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.lives -= 1
                if self.lives < 0:
                    self.state = "GAME_OVER"
                    self.state_timer = 3.0  # Show game over for 3 seconds
                    if self.score > self.high_score:
                        self.high_score = self.score
                        self.save_high_score()
                else:
                    self.reset_positions()
                    self.state = "READY"
                    self.state_timer = 2.5
                    
        elif self.state == "GAME_OVER":
            self.state_timer -= dt
            if self.state_timer <= 0:
                self.state = "START_MENU"
        
        # Handle maze blinking effect
        if self.maze_blink_active:
            self.maze_blink_timer += dt
            if self.maze_blink_timer >= 2.0:  # Blink for 2 seconds total
                self.maze_blink_active = False
                self.maze_blink_timer = 0.0

    def update_wave_timers(self, dt):
        # Manages global frightened timers or routine state fluctuations
        if self.global_mode == "FRIGHTENED":
            self.frightened_timer -= dt
            if self.frightened_timer <= 0:
                # Revert back to proper baseline settings once power-up clears
                self.global_mode = "CHASE"
                for g in self.ghosts:
                    if g.mode == "FRIGHTENED":
                        g.mode = "CHASE"
                self.ghosts_eaten_combo = 0  # Reset combo when frightened ends
        else:
            self.mode_timer += dt
            # Alternate standard Waves: Scatter 7 seconds, Chase 20 seconds
            if self.global_mode == "SCATTER" and self.mode_timer > 7.0:
                self.global_mode = "CHASE"
                self.mode_timer = 0.0
            elif self.global_mode == "CHASE" and self.mode_timer > 20.0:
                self.global_mode = "SCATTER"
                self.mode_timer = 0.0

    def process_collisions(self):
        player_tile = self.player.get_tile()
        
        # Map item captures
        score_gain, power_activated = self.pellet_manager.check_collisions(player_tile)
        if score_gain > 0:
            self.score += score_gain
            if score_gain == 10:
                self.trigger_sound("pellet")
            elif score_gain == 50:
                self.trigger_sound("power_pellet")
                
        if power_activated:
            self.global_mode = "FRIGHTENED"
            self.frightened_timer = 7.0 # 7 seconds of frightened behavior
            self.ghosts_eaten_combo = 0  # Reset combo when power pellet is eaten
            for g in self.ghosts:
                # Only set frightened mode for ghosts outside the house
                if g.mode != "EATEN" and not g.in_house:
                    g.mode = "FRIGHTENED"

        # Check interaction against ghosts - use distance-based collision
        player_pos = pygame.Vector2(self.player.x, self.player.y)
        for g in self.ghosts:
            ghost_pos = pygame.Vector2(g.x, g.y)
            distance = player_pos.distance_to(ghost_pos)
            collision_distance = TILE_SIZE // 1.5  # Collision buffer
            
            if distance < collision_distance:
                if g.mode == "FRIGHTENED":
                    g.mode = "EATEN"
                    # Combo scoring: 200, 400, 800, 1600 for eating ghosts in succession
                    # Safety check to prevent excessive combo values
                    combo_multiplier = min(self.ghosts_eaten_combo, 4)
                    combo_bonus = 200 * (2 ** combo_multiplier)
                    self.score += combo_bonus
                    self.ghosts_eaten_combo += 1
                    # Decrease frightened timer with each ghost eaten (authentic Pac-Man behavior)
                    self.frightened_timer = max(0, self.frightened_timer - 1.0)
                    self.trigger_sound("ghost_eaten")
                elif g.mode != "EATEN":
                    # Player hit by ghost
                    self.state = "DYING"
                    self.state_timer = 2.0
                    self.player.living = False
                    self.ghosts_eaten_combo = 0  # Reset combo on death
                    self.trigger_sound("death")
                    # Stop only the BGM, not all sounds (so death sound can play)
                    if self.sounds.get("bgm"):
                        self.sounds["bgm"].stop()
                    self.bgm_playing = False
                    break

        # Check for map level cleared state
        if self.pellet_manager.is_empty():
            self.maze_blink_active = True
            self.maze_blink_timer = 0.0
            self.level += 1
            self.pellet_manager.load_pellets()
            self.reset_positions()
            self.state = "READY"
            self.state_timer = 2.5

    def render(self):
        try:
            self.screen.fill((0, 0, 0)) # Authentic black background
            
            # Only draw game elements if not in menu
            if self.state != "START_MENU":
                # Maze blink effect - alternate display
                if self.maze_blink_active:
                    blink_progress = (self.maze_blink_timer / self.maze_blink_interval) % 2.0
                    should_show_maze = blink_progress < 1.0
                    if should_show_maze:
                        self.maze.draw(self.screen)
                else:
                    self.maze.draw(self.screen)
                
                self.pellet_manager.draw(self.screen)
                
                if self.state != "DYING":
                    self.player.draw(self.screen)
                else:
                    self.player.draw_death_animation(self.screen)
                    
                for g in self.ghosts:
                    g.draw(self.screen)
                
            self.hud.draw(self.screen, self.score, self.high_score, self.lives, self.level, self.state, self.state_timer)
        except Exception as e:
            # Prevent crash if rendering fails
            pass
        
        # Draw transition overlay
        try:
            if self.transition_active:
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(int(self.transition_alpha))
                self.screen.blit(overlay, (0, 0))
            
            pygame.display.flip()
        except Exception as e:
            # Prevent crash if display update fails
            pass

if __name__ == "__main__":
    game = GameEngine()
    game.run()