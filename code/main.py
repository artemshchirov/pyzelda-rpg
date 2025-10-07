import warnings
import os
import pygame
import sys
import time
import math
from random import randint
import settings
from settings import WIDTH, HEIGHT, FPS, WATER_COLOR, GAME_VERSION
from level import Level
from support import get_path
from audio_utils import play_sound, stop_sound

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

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

PARTICLE_COUNT_START = 20
PARTICLE_COUNT_DEATH = 30  # Reduced for performance

BASE_HEIGHT = 720
MIN_WINDOW_WIDTH = 640
MIN_WINDOW_HEIGHT = 360


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('PyZelda RPG')
        self.base_height = BASE_HEIGHT
        self.window_flags = pygame.RESIZABLE
        self.min_window_width = MIN_WINDOW_WIDTH
        self.min_window_height = MIN_WINDOW_HEIGHT
        self._init_display()
        self.clock = pygame.time.Clock()

        # Game states
        self.game_state = 'start'  # 'start', 'game', 'death'

        # Fonts (pre-loaded for performance)
        self.font_title = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.font_subtitle = pygame.font.Font(None, SUBTITLE_FONT_SIZE)
        self.font_menu = pygame.font.Font(None, MENU_FONT_SIZE)
        self.font_stats = pygame.font.Font(None, STATS_FONT_SIZE)

        self.background_music_path = get_path('../audio/main.ogg')
        self.background_music_volume = 0.3

        # Start screen audio
        try:
            self.start_music = pygame.mixer.Sound(self.background_music_path)
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

        self._start_background_music()

        # Particle animation data
        self.death_particles = []
        self._init_death_particles()

        # Menu state
        self.selected_menu_option = 0  # 0 = Start, 1 = Quit

        # Overlay menus
        self.overlay_state = None  # None, 'pause', 'settings'
        self.pause_menu_options = ['Resume', 'Settings']
        self.pause_menu_index = 0
        self.settings_menu_options = ['Sound', 'Back']
        self.settings_menu_index = 0
        self.prev_level_pause = False

        # Map system
        self.current_map_id = 'default'
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
            self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
            self.player = self.level.player
        else:
            self.player = None  # Will be created by Level
            self.level = Level(self.current_map_id, player=self.player, loaded_data=None, on_transition=self.handle_transition)
            self.player = self.level.player

    def _init_death_particles(self):
        """Initialize death screen particles with random properties"""
        self.death_particles = []
        for _ in range(PARTICLE_COUNT_DEATH):
            particle = {
                'x': randint(0, self.width),
                'y': randint(0, self.height),
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
                particle['x'] = self.width
            elif particle['x'] > self.width:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = self.height
            elif particle['y'] > self.height:
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

    def _start_background_music(self):
        if not getattr(self, 'background_music_path', None):
            return
        if not settings.IS_MUSIC_ENABLED:
            pygame.mixer.music.stop()
            return
        try:
            if not pygame.mixer.music.get_busy():
                pygame.mixer.music.load(self.background_music_path)
                pygame.mixer.music.set_volume(self.background_music_volume)
                pygame.mixer.music.play(-1)
            else:
                pygame.mixer.music.set_volume(self.background_music_volume)
        except pygame.error:
            print("Warning: Could not load background music")
            self.background_music_path = None

    def _init_display(self):
        self.is_fullscreen = False
        self.desktop_width, self.desktop_height = self._get_desktop_size()
        width_candidate = WIDTH if WIDTH and WIDTH > 0 else None
        height_candidate = HEIGHT if HEIGHT and HEIGHT > 0 else None
        if not width_candidate and self.desktop_width:
            width_candidate = int(self.desktop_width * 0.6)
        if not height_candidate and self.desktop_height:
            height_candidate = int(self.desktop_height * 0.6)
        if not width_candidate:
            width_candidate = 1280
        if not height_candidate:
            height_candidate = 720
        window_width = max(width_candidate, self.min_window_width)
        window_height = max(height_candidate, self.min_window_height)
        self.windowed_size = (window_width, window_height)
        self._prepare_window_position(window_width, window_height)
        self.screen = pygame.display.set_mode(self.windowed_size, self.window_flags)
        self._after_display_surface_change()
        self._center_window(window_width, window_height)

    def _get_desktop_size(self):
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            return sizes[0]
        info = pygame.display.Info()
        if getattr(info, 'current_w', 0) and getattr(info, 'current_h', 0):
            return info.current_w, info.current_h
        return 0, 0

    def _prepare_window_position(self, width, height):
        if not self.desktop_width or not self.desktop_height:
            return
        pos_x = max((self.desktop_width - width) // 2, 0)
        pos_y = max((self.desktop_height - height) // 2, 0)
        os.environ['SDL_VIDEO_WINDOW_POS'] = f"{pos_x},{pos_y}"

    def _center_window(self, width, height):
        if not self.desktop_width or not self.desktop_height:
            return
        pos_x = max((self.desktop_width - width) // 2, 0)
        pos_y = max((self.desktop_height - height) // 2, 0)
        set_position = getattr(pygame.display, 'set_window_position', None)
        if callable(set_position):
            try:
                set_position(pos_x, pos_y)
            except pygame.error:
                pass

    def _update_dimensions(self, width, height):
        global WIDTH, HEIGHT
        self.width = width
        self.height = height
        self.height_scale = self.height / self.base_height if self.base_height else 1
        self._update_layout_metrics()
        settings.WIDTH = width
        settings.HEIGHT = height
        WIDTH = width
        HEIGHT = height

    def _update_layout_metrics(self):
        scale = self.height_scale
        self.title_y_offset = self.height // 3
        self.subtitle_y_offset = self.title_y_offset + int(80 * scale)
        half_height = self.height // 2
        self.start_menu_y_offset = half_height + int(50 * scale)
        self.quit_menu_y_offset = half_height + int(120 * scale)
        self.death_menu_y_offset = half_height + int(80 * scale)
        self.death_quit_y_offset = half_height + int(140 * scale)

    def _after_display_surface_change(self):
        self.screen = pygame.display.get_surface()
        width, height = self.screen.get_size()
        self._update_dimensions(width, height)
        if hasattr(self, 'death_particles'):
            self._init_death_particles()
        if hasattr(self, 'level'):
            self.level.on_window_resized()

    def _apply_resize(self, width, height):
        if self.is_fullscreen:
            return
        resized_width = max(width, self.min_window_width)
        resized_height = max(height, self.min_window_height)
        self.windowed_size = (resized_width, resized_height)
        self.screen = pygame.display.set_mode(self.windowed_size, self.window_flags)
        self._after_display_surface_change()

    def toggle_fullscreen(self, force_fullscreen=None):
        target_fullscreen = (not self.is_fullscreen) if force_fullscreen is None else force_fullscreen
        if target_fullscreen == self.is_fullscreen:
            return
        if target_fullscreen:
            self.windowed_size = self.screen.get_size()
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.is_fullscreen = True
        else:
            self.screen = pygame.display.set_mode(self.windowed_size, self.window_flags)
            self.is_fullscreen = False
            self._center_window(*self.windowed_size)
        self._after_display_surface_change()

    def _apply_audio_settings(self):
        if not settings.IS_MUSIC_ENABLED:
            pygame.mixer.music.stop()
            stop_sound(self.start_music)
        else:
            if self.game_state == 'start':
                if self.start_music and not pygame.mixer.get_busy():
                    play_sound(self.start_music, loops=-1)
            else:
                self._start_background_music()

    def open_pause_menu(self):
        if self.overlay_state is None:
            self.overlay_state = 'pause'
            self.pause_menu_index = 0
            if hasattr(self, 'level'):
                self.prev_level_pause = getattr(self.level, 'game_paused', False)
                self.level.game_paused = True

    def close_pause_menu(self):
        self.overlay_state = None
        self.pause_menu_index = 0
        if hasattr(self, 'level'):
            self.level.game_paused = self.prev_level_pause
        self.prev_level_pause = False

    def show_pause_menu(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font_title.render("Paused", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title_text, title_rect)

        base_y = self.height // 2
        spacing = 70
        for idx, option in enumerate(self.pause_menu_options):
            center = (self.width // 2, base_y + idx * spacing)
            self._render_highlighted_text(option, self.font_menu, MENU_COLOR, TITLE_COLOR, center, idx == self.pause_menu_index)

    def show_settings_menu(self):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font_title.render("Settings", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.width // 2, self.height // 3))
        self.screen.blit(title_text, title_rect)

        options = [
            f"Sound: {'On' if settings.IS_MUSIC_ENABLED else 'Off'}",
            "Back"
        ]
        base_y = self.height // 2
        spacing = 70
        for idx, option in enumerate(options):
            center = (self.width // 2, base_y + idx * spacing)
            self._render_highlighted_text(option, self.font_menu, MENU_COLOR, TITLE_COLOR, center, idx == self.settings_menu_index)

    def handle_pause_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.pause_menu_index = (self.pause_menu_index - 1) % len(self.pause_menu_options)
            play_sound(self.menu_move_sound)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_menu_index = (self.pause_menu_index + 1) % len(self.pause_menu_options)
            play_sound(self.menu_move_sound)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            play_sound(self.menu_select_sound)
            if self.pause_menu_index == 0:
                self.close_pause_menu()
            elif self.pause_menu_index == 1:
                self.overlay_state = 'settings'
                self.settings_menu_index = 0
        elif event.key == pygame.K_ESCAPE:
            self.close_pause_menu()

    def handle_settings_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if event.key in (pygame.K_UP, pygame.K_w):
            self.settings_menu_index = (self.settings_menu_index - 1) % len(self.settings_menu_options)
            play_sound(self.menu_move_sound)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.settings_menu_index = (self.settings_menu_index + 1) % len(self.settings_menu_options)
            play_sound(self.menu_move_sound)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            if self.settings_menu_index == 0:
                settings.IS_MUSIC_ENABLED = not settings.IS_MUSIC_ENABLED
                self._apply_audio_settings()
                play_sound(self.menu_select_sound)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if self.settings_menu_index == 0:
                settings.IS_MUSIC_ENABLED = not settings.IS_MUSIC_ENABLED
                self._apply_audio_settings()
                play_sound(self.menu_select_sound)
            else:
                self.overlay_state = 'pause'
                play_sound(self.menu_select_sound)
        elif event.key == pygame.K_ESCAPE:
            self.overlay_state = 'pause'

    def show_start_screen(self):
        # Background
        self.screen.fill(START_BG_COLOR)

        # Play start music
        if self.start_music and not pygame.mixer.get_busy():
            play_sound(self.start_music, loops=-1)

        # Animated Title
        current_time = pygame.time.get_ticks()
        title_y_offset = 10 * math.sin(current_time * 0.005)
        title_text = self.font_title.render("PyZelda RPG", True, TITLE_COLOR)
        title_rect = title_text.get_rect(center=(self.width // 2, self.title_y_offset + title_y_offset))
        self.screen.blit(title_text, title_rect)

        # Subtitle
        sub_text = self.font_subtitle.render("A Zelda-like Adventure", True, SUBTITLE_COLOR)
        sub_rect = sub_text.get_rect(center=(self.width // 2, self.subtitle_y_offset))
        self.screen.blit(sub_text, sub_rect)

        # Menu options with highlight
        self._render_highlighted_text("Start Game", self.font_menu, MENU_COLOR, TITLE_COLOR,
                                    (self.width // 2, self.start_menu_y_offset), self.selected_menu_option == 0)
        self._render_highlighted_text("Quit Game", self.font_menu, MENU_COLOR, TITLE_COLOR,
                                    (self.width // 2, self.quit_menu_y_offset), self.selected_menu_option == 1)

        # Instructions
        instruction_text = self.font_subtitle.render("Use ↑↓ to navigate, ENTER to select, ESC to quit", True, SUBTITLE_COLOR)
        instruction_offset = int(70 * self.height_scale)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height - instruction_offset))
        self.screen.blit(instruction_text, instruction_rect)

        # Credits
        credit_text = self.font_subtitle.render("PyZelda RPG - Open Source", True, SUBTITLE_COLOR)
        credit_offset = int(30 * self.height_scale)
        credit_rect = credit_text.get_rect(center=(self.width // 2, self.height - credit_offset))
        self.screen.blit(credit_text, credit_rect)

        # Version info
        version_text = self.font_stats.render(f"Version {GAME_VERSION}", True, SUBTITLE_COLOR)
        version_rect = version_text.get_rect(bottomright=(self.width - 20, self.height - 20))
        self.screen.blit(version_text, version_rect)

        # Decorative elements - floating particles
        for i in range(PARTICLE_COUNT_START):
            x = (current_time // 30 + i * 60) % max(self.width, 1)
            y = (self.height - 150 - (current_time // 20 + i * 30) % (max(self.height // 2, 1))) % max(self.height, 1)
            size = 2 + (i % 2)
            pygame.draw.circle(self.screen, PARTICLE_COLOR, (x, y), size)

    def show_death_screen(self):
        # Dark red background
        self.screen.fill(DEATH_BG_COLOR)

        # Death title
        death_text = self.font_title.render("You Died", True, DEATH_TITLE_COLOR)
        death_rect = death_text.get_rect(center=(self.width // 2, self.title_y_offset))
        self.screen.blit(death_text, death_rect)

        # Stats display
        exp = self.player.exp if self.player else 0
        exp_text = self.font_stats.render(f"Experience Gained: {exp}", True, MENU_COLOR)
        exp_rect = exp_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(exp_text, exp_rect)

        # Restart options
        restart_text = self.font_menu.render("Press R to Restart", True, MENU_COLOR)
        quit_text = self.font_menu.render("Press ESC to Quit", True, MENU_COLOR)

        restart_rect = restart_text.get_rect(center=(self.width // 2, self.death_menu_y_offset))
        quit_rect = quit_text.get_rect(center=(self.width // 2, self.death_quit_y_offset))

        self.screen.blit(restart_text, restart_rect)
        self.screen.blit(quit_text, quit_rect)

        # Animated death particles
        self._update_and_draw_death_particles()

    def fade(self, fade_in=False, speed=15):
        # fade_in: if True, fade from black to game; else fade to black
        fade_surface = pygame.Surface((self.width, self.height))
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

                if event.type == pygame.VIDEORESIZE:
                    self._apply_resize(event.w, event.h)
                    continue

                if event.type == pygame.WINDOWEVENT:
                    if event.event == pygame.WINDOWEVENT_MAXIMIZED and not self.is_fullscreen:
                        self.toggle_fullscreen(True)
                        continue
                    if event.event == pygame.WINDOWEVENT_RESTORED and self.is_fullscreen:
                        self.toggle_fullscreen(False)
                        continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                    continue

                if self.overlay_state == 'pause':
                    self.handle_pause_event(event)
                    continue
                if self.overlay_state == 'settings':
                    self.handle_settings_event(event)
                    continue

                if self.game_state == 'start':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            play_sound(self.menu_select_sound)
                            if self.selected_menu_option == 0:  # Start Game
                                stop_sound(self.start_music)
                                self.game_state = 'game'
                                self._start_background_music()
                            elif self.selected_menu_option == 1:  # Quit Game
                                pygame.quit()
                                sys.exit()
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit()
                            sys.exit()
                        elif event.key in (pygame.K_UP, pygame.K_w):
                            play_sound(self.menu_move_sound)
                            self.selected_menu_option = (self.selected_menu_option - 1) % 2
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            play_sound(self.menu_move_sound)
                            self.selected_menu_option = (self.selected_menu_option + 1) % 2

                elif self.game_state == 'death':
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.game_state = 'game'
                            if self.player:
                                self.player.health = self.player.stats['health']
                                spawn_pos = self.level._player_spawn_pos if self.level._player_spawn_pos else (100, 100)
                                self.player.pos = pygame.math.Vector2(spawn_pos)
                                self.player.rect.center = spawn_pos
                            self._start_background_music()
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
                        if event.key == pygame.K_ESCAPE:
                            self.open_pause_menu()
                        elif event.key == pygame.K_m:
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
            if self.overlay_state:
                self.level.visible_sprites.custom_draw(self.player)
                self.level.ui.display(self.player)
                if self.overlay_state == 'pause':
                    self.show_pause_menu()
                elif self.overlay_state == 'settings':
                    self.show_settings_menu()
            else:
                self.level.run(dt)

            # Check for player death
            if self.player and self.player.health <= 0 and self.game_state != 'death':
                self.game_state = 'death'
                if self.overlay_state:
                    self.close_pause_menu()
                play_sound(self.death_sound)

            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
