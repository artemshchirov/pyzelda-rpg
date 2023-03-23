import pygame
import sys
import time
from settings import *
from level import Level


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('PyZelda RPG')
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.level = Level()

    def run(self):
        last_time = time.time()
        while (True):
            dt = time.time() - last_time
            last_time = time.time()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('black')
            self.level.run(dt)
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
