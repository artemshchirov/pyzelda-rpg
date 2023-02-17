import pygame
from settings import *
from tile import Tile
from player import Player
from support import *
from random import choice
from weapon import Weapon


class Level:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()

        # setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacles_sprites = pygame.sprite.Group()

        # attack
        self.current_attack = None

        self.create_map()

    def create_map(self):

        boundary_map_path = get_path('../data/map/map_FloorBlocks.csv')
        grass_map_path = get_path('../data/map/map_Grass.csv')
        object_map_path = get_path('../data/map/map_Objects.csv')

        grass_path = get_path('../graphics/grass')
        objects_path = get_path('../graphics/objects')

        layouts = {
            'boundary': import_csv_layout(boundary_map_path),
            'grass': import_csv_layout(grass_map_path),
            'object': import_csv_layout(object_map_path),
        }

        graphics = {
            'grass': import_folder(grass_path),
            'objects': import_folder(objects_path),
        }

        for style, layout in layouts.items():
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
                            surf = graphics['objects'][int(col)]
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


class YSortCameraGroup(pygame.sprite.Group):
    """
    Set camera position and implement overlap 
    """

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # floor setup
        floor_path = get_path('../graphics/tilemap/ground.png')
        self.floor_surf = pygame.image.load(floor_path).convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)
