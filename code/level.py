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
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map()

    def create_map(self):
        print()
        for row_idx, row in enumerate(WORLD_MAP):
            print(f"{row_idx if row_idx > 9 else ' ' + str(row_idx)}", *row)
            for col_idx, col in enumerate(row):
                x = col_idx * TILESIZE
                y = row_idx * TILESIZE
                if col == 'x':
                    Tile((x, y), [self.visible_sprites,
                         self.obstacles_sprites])
                if col == 'p':
                    self.player = Player(
                        (x, y), [self.visible_sprites], self.obstacles_sprites)

    def run(self):
        """Update and draw the game"""
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()


class YSortCameraGroup(pygame.sprite.Group):
    """
    Set camera position and implement overlap 
    """

    def __init__(self):

        # general setup()
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            debug(f"offset_rect: {offset_rect}", 145, 10)
            self.display_surface.blit(sprite.image, offset_rect)
        debug(f"rect.topleft: {sprite.rect.topleft}", 215, 10)

        debug(f"self.offset: {self.offset}", 190, 10)

        debug(f"player.rect.centerx: {player.rect.centerx}", 240, 10)
        debug(f"player.rect.centery: {player.rect.centery}", 260, 10)
