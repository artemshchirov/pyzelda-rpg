import pygame
from settings import *
from tile import Tile
from player import Player
from support import get_path, import_csv_layout, import_folder
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationPlayer
from magic import MagicPlayer
from upgrade import Upgrade


class Level:
    def get_savable_state(self):
        # Collect defeated enemies and destroyed grass by their initial positions
        defeated_enemies = []
        destroyed_grass = []
        for sprite in self.attackable_sprites:
            if hasattr(sprite, 'sprite_type'):
                if sprite.sprite_type == 'enemy' and not sprite.alive():
                    defeated_enemies.append({'x': sprite.rect.x, 'y': sprite.rect.y})
                if sprite.sprite_type == 'grass' and not sprite.alive():
                    destroyed_grass.append({'x': sprite.rect.x, 'y': sprite.rect.y})
        return {
            'player': self.player.to_dict(),
            'defeated_enemies': defeated_enemies,
            'destroyed_grass': destroyed_grass
        }
    def __init__(self, loaded_data=None):
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.create_map(loaded_data)

        # user interface
        self.ui = UI()
        self.upgrade = Upgrade(self.player)

        # particles
        self.animation_player = AnimationPlayer()
        self.magic_player = MagicPlayer(self.animation_player)

    def trigger_exp_particles(self, enemy_pos, player_pos, exp_amount=0):
        # Use sparkle as placeholder if exp_orb graphics are missing
        animation_type = 'exp_orb' if 'exp_orb' in self.animation_player.frames else 'sparkle'
        self.animation_player.create_exp_particles(enemy_pos, player_pos, self.visible_sprites, amount=5, exp_amount=exp_amount)

    def create_map(self, loaded_data=None):
        layouts = {
            'boundary': import_csv_layout('../data/map/map_FloorBlocks.csv'),
            'grass': import_csv_layout('../data/map/map_Grass.csv'),
            'object': import_csv_layout('../data/map/map_Objects.csv'),
            'entities': import_csv_layout('../data/map/map_Entities.csv'),
        }

        graphics = {
            'grass': import_folder('../graphics/grass'),
            'objects': import_folder('../graphics/objects'),
        }

        # Build pathfinding grid after all obstacles are placed
        from pathfinding_utils import build_grid
        self.pathfinding_grid = None

        for style, layout in layouts.items():
            for row_idx, row in enumerate(layout):
                for col_idx, col in enumerate(row):
                    if col != '-1':
                        x = col_idx * TILESIZE
                        y = row_idx * TILESIZE

                        if style == 'boundary':
                            Tile((x, y),
                                 [self.obstacle_sprites],
                                 'invisible')

                        if style == 'grass':
                            destroyed = False
                            if loaded_data and 'destroyed_grass' in loaded_data:
                                for g in loaded_data['destroyed_grass']:
                                    if g['x'] == x and g['y'] == y:
                                        destroyed = True
                                        break
                            if not destroyed:
                                random_grass_image = choice(graphics['grass'])
                                Tile((x, y),
                                     [self.visible_sprites,
                                         self.obstacle_sprites,  self.attackable_sprites],
                                     'grass',
                                     random_grass_image)

                        if style == 'object':
                            surf = graphics['objects'][int(col)]
                            Tile((x, y),
                                 [self.visible_sprites, self.obstacle_sprites],
                                 'object',
                                 surf)

        # Now build the pathfinding grid
        self.pathfinding_grid = build_grid(WIDTH, HEIGHT, TILESIZE, self.obstacle_sprites)

        # Place entities (player and enemies) after grid is built
        entities_layout = layouts['entities']
        for row_idx, row in enumerate(entities_layout):
            for col_idx, col in enumerate(row):
                if col != '-1':
                    x = col_idx * TILESIZE
                    y = row_idx * TILESIZE
                    if col == '394':
                        self.player = Player(
                            (x, y),
                            [self.visible_sprites],
                            self.obstacle_sprites,
                            self.create_attack,
                            self.destroy_attack,
                            self.create_magic)
                        if loaded_data and 'player' in loaded_data:
                            self.player.from_dict(loaded_data['player'])
                    else:
                        defeated = False
                        if loaded_data and 'defeated_enemies' in loaded_data:
                            for e in loaded_data['defeated_enemies']:
                                if e['x'] == x and e['y'] == y:
                                    defeated = True
                                    break
                        if not defeated:
                            if col == '390':
                                monster_name = 'bamboo'
                            elif col == '391':
                                monster_name = 'spirit'
                            elif col == '392':
                                monster_name = 'raccoon'
                            else:
                                monster_name = 'squid'

                            Enemy(
                                monster_name,
                                (x, y),
                                [self.visible_sprites, self.attackable_sprites],
                                self.obstacle_sprites, self.damage_player, self.trigger_death_particles,
                                self.add_exp, lambda enemy_pos, player_pos, exp_amount=0, self=self: self.trigger_exp_particles(enemy_pos, player_pos, exp_amount),
                                self.pathfinding_grid, TILESIZE)

    def create_attack(self):
        self.current_attack = Weapon(
            self.player, [self.visible_sprites, self.attack_sprites])

    def create_magic(self, style, strength, cost):
        if style == 'heal':
            self.magic_player.heal(self.player, strength, cost, [
                                   self.visible_sprites])

        if style == 'flame':
            self.magic_player.flame(
                self.player, cost, [self.visible_sprites, self.attack_sprites])

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    attack_sprite, self.attackable_sprites, False)
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == 'grass':
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 75)
                            for leaf in range(randint(3, 6)):
                                self.animation_player.create_grass_particles(
                                    pos - offset, [self.visible_sprites])
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(
                                self.player, attack_sprite.sprite_type)

    def damage_player(self, amount, attack_type):
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            self.animation_player.create_particles(
                attack_type, self.player.rect.center, [self.visible_sprites])

    def trigger_death_particles(self, pos, particle_type):
        self.animation_player.create_particles(
            particle_type, pos, self.visible_sprites)

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):
        self.game_paused = not self.game_paused
        # Save game if paused and 'P' is pressed
        if self.game_paused:
            import pygame
            from save_manager import save_game
            keys = pygame.key.get_pressed()
            if keys[pygame.K_p]:
                save_game(self.get_savable_state())
                print("Game saved!")

    def run(self, dt):
        # update and draw the game
        self.visible_sprites.custom_draw(self.player)
        self.ui.display(self.player)

        if self.game_paused:  # display upgrade menu
            self.upgrade.display()
        else:  # run the game
            self.visible_sprites.update(dt)
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        # general setup
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # floor setup
        floor_path = get_path('../graphics/tilemap/ground.png')
        self.floor_surf = pygame.image.load(floor_path).convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):
        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_rect = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_rect)

    def enemy_update(self, player):
        enemy_sprites = [sprite for sprite in self.sprites() if hasattr(
            sprite, 'sprite_type') and sprite.sprite_type == 'enemy']

        for enemy in enemy_sprites:
            enemy.enemy_update(player)
