import pygame
import os
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
    def __init__(self, map_id, player=None, loaded_data=None, player_spawn_pos=None, on_transition=None):
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

        # player setup

        self.player = player
        self._player_spawn_pos = player_spawn_pos
        self.on_transition = on_transition  # callback for map transitions

        # Transition points: { (x, y): {'target_map_id': ..., 'target_spawn': (x, y)} }
        self.transition_points = {}
        self._last_transition_tile = None  # For debounce

        # sprite setup
        self.create_map(map_id, loaded_data)

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

    def create_map(self, map_id, loaded_data=None):
        # Define transition point mapping here (could be loaded from a file or hardcoded for now)
        # Example: { '9000': {'target_map_id': 'village', 'target_spawn': (5*TILESIZE, 10*TILESIZE)} }
        TRANSITION_CODE_MAP = {
            # From main map to test map (place 9000 in main map)
            '9000': {'target_map_id': 'test', 'target_spawn': (4*TILESIZE, 4*TILESIZE)},
            # From test map back to main map (place 9001 in test map)
            '9001': {'target_map_id': 'default', 'target_spawn': (27*TILESIZE, 6*TILESIZE)},
            # From test map to island (place 9002 in test map)
            '9002': {'target_map_id': 'island', 'target_spawn': (4*TILESIZE, 4*TILESIZE)},
            # From island back to test map (place 9003 in island map)
            '9003': {'target_map_id': 'test', 'target_spawn': (8*TILESIZE, 5*TILESIZE)},
            # From island to new island2 (place 9004 in island2 map)
            '9004': {'target_map_id': 'island2', 'target_spawn': (4*TILESIZE, 4*TILESIZE)},
        }
        # Map file naming convention: map_<map_id>_<layer>.csv
        def map_file(layer):
            return f"../data/map/map_{map_id}_{layer}.csv"

        # Fallback to default if not found
        def file_or_default(path, default):
            return path if os.path.exists(path) else default

        layouts = {
            'boundary': import_csv_layout(file_or_default(map_file('FloorBlocks'), '../data/map/map_FloorBlocks.csv')),
            'grass': import_csv_layout(file_or_default(map_file('Grass'), '../data/map/map_Grass.csv')),
            'object': import_csv_layout(file_or_default(map_file('Objects'), '../data/map/map_Objects.csv')),
            'entities': import_csv_layout(file_or_default(map_file('Entities'), '../data/map/map_Entities.csv')),
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
                    # Transition point check
                    if col in TRANSITION_CODE_MAP:
                        self.transition_points[(x, y)] = TRANSITION_CODE_MAP[col]
                        # Optionally, add a visible marker or invisible tile for debugging
                        Tile((x, y), [self.visible_sprites], 'invisible')
                        continue
                    if col == '394':
                        if self.player is None:
                            # Create new player if not provided
                            spawn_pos = (x, y)
                            if self._player_spawn_pos is not None:
                                spawn_pos = self._player_spawn_pos
                            self.player = Player(
                                spawn_pos,
                                [self.visible_sprites],
                                self.obstacle_sprites,
                                self.create_attack,
                                self.destroy_attack,
                                self.create_magic)
                            if loaded_data and 'player' in loaded_data:
                                self.player.from_dict(loaded_data['player'])
                        else:
                            # Move provided player to spawn
                            if self._player_spawn_pos is not None:
                                self.player.pos.x, self.player.pos.y = self._player_spawn_pos
                                self.player.rect.center = self._player_spawn_pos
                                self.player.hitbox.center = self._player_spawn_pos  # Ensure hitbox is synced
                            self.player.obstacle_sprites = self.obstacle_sprites
                            self.player.create_attack = self.create_attack
                            self.player.destroy_attack = self.destroy_attack
                            self.player.create_magic = self.create_magic
                            self.visible_sprites.add(self.player)
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
                                pathfinding_grid=self.pathfinding_grid, tile_size=TILESIZE)

    def check_transition(self):
        # Check if player is on a transition point (debounced)
        px, py = int(self.player.rect.centerx // TILESIZE) * TILESIZE, int(self.player.rect.centery // TILESIZE) * TILESIZE
        for (tx, ty), data in self.transition_points.items():
            if abs(px - tx) < TILESIZE // 2 and abs(py - ty) < TILESIZE // 2:
                if self._last_transition_tile != (tx, ty):
                    self._last_transition_tile = (tx, ty)
                    if self.on_transition:
                        self.on_transition(data['target_map_id'], data['target_spawn'])
                    return True
                else:
                    return False
        self._last_transition_tile = None
        return False

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
            # Check for map transition
            self.check_transition()


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
