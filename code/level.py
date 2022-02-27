import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug


class Level:
    def __init__(self):

        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups setup
        self.visible_sprites = pygame.sprite.Group()
        self.obstacles_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

    def create_map(self):
        for row_idx, row in enumerate(WORLD_MAP):
            print(f"{row_idx if row_idx > 9 else '0' + str(row_idx)} {row}")
            for col_idx, col in enumerate(row):
                x = col_idx * TILESIZE
                y = row_idx * TILESIZE
                if col == 'x':
                    Tile((x, y), [self.visible_sprites,
                         self.obstacles_sprites])
                if col == 'p':
                    self.player = Player((x, y), [self.visible_sprites])

    def run(self):
        """Update and draw the game"""
        self.visible_sprites.draw(self.display_surface)
        self.visible_sprites.update()
        debug(self.player.direction)
