import pygame
import sys
import time
from settings import *
from level import Level
from support import get_path


class Game:
    def __init__(self):
        import os
        from save_manager import load_game
        from player import Player
        pygame.init()
        pygame.display.set_caption('PyZelda RPG')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

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

        # Create player and level
        if loaded_data and 'player' in loaded_data:
            # If loading, player will be created by Level and then extracted
            self.level = Level(self.current_map_id, player=None, loaded_data=loaded_data, on_transition=self.handle_transition)
            self.player = self.level.player
        else:
            # New game
            self.player = None  # Will be created by Level
            self.level = Level(self.current_map_id, player=self.player, loaded_data=None, on_transition=self.handle_transition)
            self.player = self.level.player

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

                if self.show_save_dialog:
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
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
