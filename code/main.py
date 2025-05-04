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
        if os.path.exists(save_path):
            # Prompt user in terminal for continue/new game
            print("Save file detected. Type 'c' to continue or 'n' for new game:")
            choice = input().strip().lower()
            if choice == 'c':
                loaded_data = load_game(save_path)
        self.level = Level(loaded_data=loaded_data)

        # sound
        main_sound = pygame.mixer.Sound(get_path('../audio/main.ogg'))
        main_sound.set_volume(0.5)
        main_sound.play(loops=-1)

    def run(self):
        last_time = time.time()
        while (True):
            dt = time.time() - last_time
            last_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_m:
                        self.level.toggle_menu()

            self.screen.fill(WATER_COLOR)
            self.level.run(dt)
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
