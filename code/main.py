import pygame
import sys
from settings import *
from debug import debug
from level import Level


class Game:
    def __init__(self):

        # general setup
        pygame.init()
        pygame.display.set_caption('Cyber-RPG')
        self.screen = pygame.display.set_mode((WIDTH, HEIGTH))
        self.clock = pygame.time.Clock()

        self.level = Level()

    def run(self):
        while(True):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            self.screen.fill('black')
            self.level.run()
            # debug('hello')
            pygame.display.update()
            self.clock.tick(FPS)


if __name__ == '__main__':
    game = Game()
    game.run()
