import warnings
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame
import sys
import time
import math
from random import randint
from settings import WIDTH, HEIGHT, FPS, WATER_COLOR
from level import Level
from support import get_path

# Suppress warnings
warnings.simplefilter('ignore', UserWarning)

# UI Constants
START_BG_COLOR = (20, 20, 40)
DEATH_BG_COLOR = (40, 0, 0)
TITLE_COLOR = (255, 215, 0)
SUBTITLE_COLOR = (200, 200, 200)
MENU_COLOR = (255, 255, 255)
DEATH_TITLE_COLOR = (255, 0, 0)
PARTICLE_COLOR = (100, 150, 255)
DEATH_PARTICLE_BASE_COLOR = (100, 0, 0)

TITLE_FONT_SIZE = 72
SUBTITLE_FONT_SIZE = 36
MENU_FONT_SIZE = 48
STATS_FONT_SIZE = 36

TITLE_Y_OFFSET = HEIGHT // 3
SUBTITLE_Y_OFFSET = TITLE_Y_OFFSET + 80
START_MENU_Y_OFFSET = HEIGHT // 2 + 50
QUIT_MENU_Y_OFFSET = HEIGHT // 2 + 120
DEATH_MENU_Y_OFFSET = HEIGHT // 2 + 80
DEATH_QUIT_Y_OFFSET = HEIGHT // 2 + 140

PARTICLE_COUNT_START = 20
PARTICLE_COUNT_DEATH = 30  # Reduced for performance


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('PyZelda RPG')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Game states
        self.game_state = 'start'  # 'start', 'game', 'death'

        # Fonts (pre-loaded for performance)
        self.font_title = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.font_subtitle = pygame.font.Font(None, SUBTITLE_FONT_SIZE)
        self.font_menu = pygame.font.Font(None, MENU_FONT_SIZE)
        self.font_stats = pygame.font.Font(None, STATS_FONT_SIZE)

        # Start screen audio
        try:
            self.start_music = pygame.mixer.Sound(get_path('../audio/main.ogg'))
            self.start_music.set_volume(0.3)
            self.menu_move_sound = pygame.mixer.Sound(get_path('../audio/sword.wav'))
            self.menu_select_sound = pygame.mixer.Sound(get_path('../audio/sword.wav'))
            self.menu_move_sound.set_volume(0.5)
            self.menu_select_sound.set_volume(0.5)
        except pygame.error:
            self.start_music = None
            self.menu_move_sound = None
            self.menu_select_sound = None

        # Audio (with error handling)
        try:
            self.death_sound = pygame.mixer.Sound(get_path('../audio/death.wav'))
            self.death_sound.set_volume(0.6)
        except pygame.error:
            print("Warning: Could not load death sound effect")
            self.death_sound = None

        try:
            pygame.mixer.music.load(get_path('../audio/main.ogg'))
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)  # Loop indefinitely
        except pygame.error:
            print("Warning: Could not load background music")

        # Particle animation data
        self.death_particles = []
        self._init_death_particles()

        # Menu state
        self.selected_menu_option = 0  # 0 = Start, 1 = Quit

    def _init_death_particles(self):
        """Initialize death screen particles with random properties"""
        self.death_particles = []
        for _ in range(PARTICLE_COUNT_DEATH):
            particle = {
                'x': randint(0, WIDTH),
                'y': randint(0, HEIGHT),
                'size': randint(1, 4),
                'speed_x': randint(-2, 2),
                'speed_y': randint(-2, 2),
                'color': (randint(100, 255), 0, 0)
            }
            self.death_particles.append(particle)

    def _update_and_draw_death_particles(self):
        """Update and draw animated death particles"""
        for particle in self.death_particles:
            # Update position
            particle['x'] += particle['speed_x']
            particle['y'] += particle['speed_y']

            # Wrap around screen edges
            if particle['x'] < 0:
                particle['x'] = WIDTH
            elif particle['x'] > WIDTH:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = HEIGHT
            elif particle['y'] > HEIGHT:
                particle['y'] = 0

            # Draw particle
            pygame.draw.circle(self.screen, particle['color'],
                             (int(particle['x']), int(particle['y'])), particle['size'])

    def _render_highlighted_text(self, text, font, color, highlight_color, center_pos, selected=False):
        """Render text with optional highlight effect"""
        if selected:
            # Create pulsing highlight effect
            pulse = (pygame.time.get_ticks() // 100) % 2
            if pulse:
                # Draw highlight background
                rendered_text = font.render(text, True, highlight_color)
                highlight_rect = rendered_text.get_rect(center=center_pos)
                highlight_surface = pygame.Surface((highlight_rect.width + 20, highlight_rect.height + 10))
                highlight_surface.fill((50, 50, 50))
                highlight_surface.set_alpha(100)
                self.screen.blit(highlight_surface, highlight_rect.move(-10, -5))
            else:
                rendered_text = font.render(text, True, color)
        else:
            rendered_text = font.render(text, True, color)

        text_rect = rendered_text.get_rect(center=center_pos)
        self.screen.blit(rendered_text, text_rect)

        # Map system
        self.current_map_id = 'default'  # can be changed for other maps
        self.player = None

        # Check for save file
        save_path = 'savegame.json'
        loaded_data = None
        self.show_save_dialog = False
        self.save_dialog_result = None
        if os.path.exists(save_path):
            self.show_save_dialog = True
            self.save_dialog_result = None

        # Create player and level (but only if not in start state)
        if loaded_data and 'player' in loaded_data:
            # If loading, player will be created by Level and then extracted
            self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
            self.player = self.level.player
        else:
            # New game
            self.player = None  # Will be created by Level
            self.level = Level(self.current_map_id, player=self.player, loaded_data=None, on_transition=self.handle_transition)
            self.player = self.level.player

    def show_start_screen(self):
        # Background
        self.screen.fill(START_BG_COLOR)

        # Play start music
        if self.start_music and not pygame.mixer.get_busy():
            self.start_music.play(-1)

        # Animated Title
        current_time = pygame.time.get_ticks()
        title_y_offset = 10 * math.sin(current_time * 0.005)
        title_text = self.font_title.render("PyZelda RPG", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(WIDTH // 2, TITLE_Y_OFFSET + title_y_offset))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        sub_text = self.font_subtitle.render("A Zelda-like Adventure", True, SUBTITLE_COLOR)
        sub_rect = sub_text.get_rect(center=(WIDTH // 2, SUBTITLE_Y_OFFSET))
        self.screen.blit(sub_text, sub_rect)

        # Menu options with highlight
        self._render_highlighted_text("Start Game", self.font_menu, MENU_COLOR, TITLE_COLOR,
                                    (WIDTH // 2, START_MENU_Y_OFFSET), self.selected_menu_option == 0)
        self._render_highlighted_text("Quit Game", self.font_menu, MENU_COLOR, TITLE_COLOR,
                                    (WIDTH // 2, QUIT_MENU_Y_OFFSET), self.selected_menu_option == 1)

        # Instructions
        instruction_text = self.font_subtitle.render("Use ↑↓ to navigate, ENTER to select, ESC to quit", True, SUBTITLE_COLOR)
        instruction_rect = instruction_text.get_rect(center=(WIDTH // 2, HEIGHT - 70))
        self.screen.blit(instruction_text, instruction_rect)

        # Credits
        credit_text = self.font_subtitle.render("PyZelda RPG - Open Source", True, SUBTITLE_COLOR)
        credit_rect = credit_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        self.screen.blit(credit_text, credit_rect)

        # Decorative elements - floating particles
        for i in range(PARTICLE_COUNT_START):
            x = (current_time // 30 + i * 60) % WIDTH
            y = (HEIGHT - 150 - (current_time // 20 + i * 30) % (HEIGHT // 2)) % HEIGHT
            size = 2 + (i % 2)
            pygame.draw.circle(self.screen, PARTICLE_COLOR, (x, y), size)

    def show_death_screen(self):
        # Dark red background
        self.screen.fill(DEATH_BG_COLOR)

        # Death title
        death_text = self.font_title.render("You Died", True, DEATH_TITLE_COLOR)
        death_rect = death_text.get_rect(center=(WIDTH // 2, TITLE_Y_OFFSET))
        self.screen.blit(death_text, death_rect)

        # Stats display
        exp = self.player.exp if self.player else 0
        exp_text = self.font_stats.render(f"Experience Gained: {exp}", True, MENU_COLOR)
        exp_rect = exp_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(exp_text, exp_rect)

        # Restart options
        restart_text = self.font_menu.render("Press R to Restart", True, MENU_COLOR)
        quit_text = self.font_menu.render("Press ESC to Quit", True, MENU_COLOR)

        restart_rect = restart_text.get_rect(center=(WIDTH // 2, DEATH_MENU_Y_OFFSET))
        quit_rect = quit_text.get_rect(center=(WIDTH // 2, DEATH_QUIT_Y_OFFSET))

        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(quit_text, quit_rect)

        # Animated death particles
        self._update_and_draw_death_particles()

    def fade(self, fade_in=False, speed=15):
        # fade_in: if True, fade from black to game; else fade to black
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        clock = pygame.time.Clock()
        if not fade_in:
            for alpha in range(0, 256, speed):
                fade_surface.set_alpha(alpha)
                self.screen.fill((0, 0, 0))
                self.level.run(0)  # draw current frame
                self.screen.blit(fade_surface, (0, 0))
                pygame.display.update()
                clock.tick(FPS // 2)
        else:
            for alpha in range(255, -1, -speed):
                fade_surface.set_alpha(alpha)
                self.screen.fill((0, 0, 0))
                self.level.run(0)  # draw new frame
                self.screen.blit(fade_surface, (0, 0))
                pygame.display.update()
                clock.tick(FPS // 2)

    def handle_transition(self, target_map_id, target_spawn):
        # Fade out
        self.fade(fade_in=False)
        # Switch map
        self.current_map_id = target_map_id
        self.level = Level(
            self.current_map_id,
            player=self.player,
            loaded_data=None,
            player_spawn_pos=target_spawn,
            on_transition=self.handle_transition
        )
        # Fade in
        self.fade(fade_in=True)

    def run(self):
        import pygame
        from save_manager import save_game, load_game
        last_time = time.time()
        while True:
            dt = time.time() - last_time
            last_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if self.game_state == 'start':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            if self.menu_select_sound:
                                self.menu_select_sound.play()
                            if self.selected_menu_option == 0:  # Start Game
                                if self.start_music:
                                    self.start_music.stop()
                                self.game_state = 'game'
                            elif self.selected_menu_option == 1:  # Quit Game
                                pygame.quit()
                                sys.exit()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        elif event.key == pygame.K_UP:
                            if self.menu_move_sound:
                                self.menu_move_sound.play()
                            self.selected_menu_option = (self.selected_menu_option - 1) % 2
                        elif event.key == pygame.K_DOWN:
                            if self.menu_move_sound:
                                self.menu_move_sound.play()
                            self.selected_menu_option = (self.selected_menu_option + 1) % 2

                elif self.game_state == 'death':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            # Restart game
                            self.game_state = 'game'
                            # Reset player health and position
                            if self.player:
                                self.player.health = self.player.stats['health']
                                spawn_pos = self.level._player_spawn_pos if self.level._player_spawn_pos else (100, 100)
                                self.player.pos = pygame.math.Vector2(spawn_pos)
                                self.player.rect.center = spawn_pos
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()

                elif self.show_save_dialog:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_c:
                            self.save_dialog_result = 'c'
                        elif event.key == pygame.K_n:
                            self.save_dialog_result = 'n'

                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_m:
                            self.level.toggle_menu()
                        # Save game when paused and P is pressed
                        if event.key == pygame.K_p and getattr(self.level, 'game_paused', False):
                            save_game(self.level.get_savable_state())
                            self.save_message_time = time.time()

            if self.game_state == 'start':
                self.show_start_screen()
                pygame.display.update()
                self.clock.tick(FPS)
                continue

            elif self.game_state == 'death':
                self.show_death_screen()
                pygame.display.update()
                self.clock.tick(FPS)
                continue

            # Handle save dialog logic
            if self.show_save_dialog:
                self.screen.fill(WATER_COLOR)
                # Draw a rounded rectangle background for the dialog
                dialog_width, dialog_height = 600, 220
                dialog_x = (self.screen.get_width() - dialog_width) // 2
                dialog_y = (self.screen.get_height() - dialog_height) // 2
                dialog_rect = pygame.Rect(dialog_x, dialog_y, dialog_width, dialog_height)
                # Shadow
                shadow_rect = dialog_rect.move(6, 6)
                pygame.draw.rect(self.screen, (0,0,0,80), shadow_rect, border_radius=24)
                # Main box
                pygame.draw.rect(self.screen, (30, 30, 40), dialog_rect, border_radius=24)
                pygame.draw.rect(self.screen, (255, 215, 0), dialog_rect, 4, border_radius=24)

                # Title
                font_title = pygame.font.Font(None, 54)
                text1 = font_title.render("Save file detected!", True, (255,255,255))
                self.screen.blit(text1, (dialog_x + (dialog_width - text1.get_width())//2, dialog_y + 30))

                # Instructions
                font_body = pygame.font.Font(None, 36)
                text2 = font_body.render("Press C to Continue or N for New Game", True, (255,255,0))
                self.screen.blit(text2, (dialog_x + (dialog_width - text2.get_width())//2, dialog_y + 100))

                # Button hints
                font_hint = pygame.font.Font(None, 28)
                c_hint = font_hint.render("[C] Continue", True, (180,255,180))
                n_hint = font_hint.render("[N] New Game", True, (255,180,180))
                self.screen.blit(c_hint, (dialog_x + 80, dialog_y + 160))
                self.screen.blit(n_hint, (dialog_x + dialog_width - n_hint.get_width() - 80, dialog_y + 160))

                pygame.display.update()
                if self.save_dialog_result:
                    if self.save_dialog_result == 'c':
                        loaded_data = load_game('savegame.json')
                        self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
                        self.player = self.level.player
                    elif self.save_dialog_result == 'n':
                        self.level = Level(self.current_map_id, player=None, loaded_data=None, on_transition=self.handle_transition)
                        self.player = self.level.player
                    self.show_save_dialog = False
                self.clock.tick(FPS)
                continue

            self.screen.fill(WATER_COLOR)
            self.level.run(dt)

            # Check for player death
            if self.player and self.player.health <= 0 and self.game_state != 'death':
                self.game_state = 'death'
                if self.death_sound:
                    self.death_sound.play()

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
