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
        pygame.init()
        pygame.display.set_caption('PyZelda RPG')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        # Check for save file
        save_path = 'savegame.json'
        loaded_data = None
        self.show_save_dialog = False
        self.save_dialog_result = None
        if os.path.exists(save_path):
            self.show_save_dialog = True
            self.save_dialog_result = None
        self.level = Level(loaded_data=loaded_data)

        # sound
        main_sound = pygame.mixer.Sound(get_path('../audio/main.ogg'))
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)

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
                font = pygame.font.Font(None, 48)
                text1 = font.render("Save file detected!", True, (255,255,255))
                text2 = font.render("Press C to Continue or N for New Game", True, (255,255,0))
                self.screen.blit(text1, (self.screen.get_width()//2 - text1.get_width()//2, 200))
                self.screen.blit(text2, (self.screen.get_width()//2 - text2.get_width()//2, 300))
                pygame.display.update()
                if self.save_dialog_result:
                    if self.save_dialog_result == 'c':
                        loaded_data = load_game('savegame.json')
                        self.level = Level(loaded_data=loaded_data)
                    elif self.save_dialog_result == 'n':
                        self.level = Level(loaded_data=None)
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
