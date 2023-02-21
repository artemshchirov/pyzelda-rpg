import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice
from weapon import Weapon


class Level:
    def __init__(self):
        # get the display surface
        self.display_surface = pygame.display.get_surface()

        # sprite groups setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None

        # sprite setup
        self.create_map()

    def create_map(self):
        layouts = {
            'boundary': import_csv_layout(r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\code\map\map_FloorBlocks.csv'),
            'grass': import_csv_layout(r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\code\map\map_Grass.csv'),
            'object': import_csv_layout(r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\code\map\map_Objects.csv'),
        }

        graphics = {
            'grass': import_folder(r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\grass'),
            'objects': import_folder(r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\objects'),
        }
        # print('\ngraphics: \n', graphics)

        for style, layout in layouts.items():
            print('style: ', style)
            for row_idx, row in enumerate(layout):
                for col_idx, col in enumerate(row):
                    if col != '-1':
                        x = col_idx * TILESIZE
                        y = row_idx * TILESIZE

                        if style == 'boundary':
                            Tile((x, y),
                                 [self.obstacles_sprites],
                                 'invisible')

                        if style == 'grass':
                            random_grass_image = choice(graphics['grass'])
                            Tile((x, y),
                                 [self.visible_sprites, self.obstacles_sprites],
                                 'grass',
                                 random_grass_image)

                        if style == 'objects':
                            print('col')
                            surf = graphics['objects'][int(col)]
                            print('surf: ', surf)
                            Tile((x, y),
                                 [self.visible_sprites, self.obstacles_sprites],
                                 'object',
                                 surf)

        self.player = Player(
            (2000, 1430), [self.visible_sprites], self.obstacles_sprites, self.create_attack, self.destroy_attack)

    def create_attack(self):
        self.current_attack = Weapon(self.player, [self.visible_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def run(self):
        """Update and draw the game"""
        self.visible_sprites.custom_draw(self.player)
        self.visible_sprites.update()
        debug(self.player.status, 400, 10)


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

        # creating floor
        self.floor_surf = pygame.image.load(
            r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\tilemap\ground.png').convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

        print(f"self.floor_stuf : {self.floor_surf}")

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)

            debug(f"offset_rect: {offset_rect}", 145, 10)
        debug(f"rect.topleft: {sprite.rect.topleft}", 215, 10)
        debug(f"self.offset: {self.offset}", 190, 10)
        debug(f"player.rect.centerx: {player.rect.centerx}", 240, 10)
        debug(f"player.rect.centery: {player.rect.centery}", 260, 10)
