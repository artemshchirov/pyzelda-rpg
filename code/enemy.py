import pygame

from settings import *
from support import import_folder
from entity import Entity
from pathfinding_utils import astar, pos_to_grid, grid_to_pos


class Enemy(Entity):
    def __init__(self, monster_name, pos, groups, obstacle_sprites, damage_player, trigger_death_particles, add_exp, trigger_exp_particles=None, pathfinding_grid=None, tile_size=None):
        super().__init__(groups, pos)
        # general setup
        self.sprite_type = 'enemy'

        # graphics setup
        self.import_graphics(monster_name)
        self.status = 'idle'
        self.image = self.animations[self.status][self.frame_index]
        self.rect = self.image.get_rect(topleft=pos)

        # movement
        self.hitbox = self.rect.inflate(0, -10)
        self.obstacle_sprites = obstacle_sprites
        self.pos = pygame.math.Vector2(self.rect.center)

        # stats
        self.monster_name = monster_name
        monster_info = monster_data[self.monster_name]
        self.health = monster_info['health']
        self.exp = monster_info['exp']
        self.speed = monster_info['speed']
        self.attack_damage = monster_info['damage']
        self.resistance = monster_info['resistance']
        self.attack_radius = monster_info['attack_radius']
        self.notice_radius = monster_info['notice_radius']

        # exp orb callback
        self.trigger_exp_particles = trigger_exp_particles
        self.last_player_pos = None
        self.attack_type = monster_info['attack_type']

        # player interaction
        self.can_attack = True
        self.attack_time = None
        self.attack_cooldown = 400
        self.damage_player = damage_player
        self.trigger_death_particles = trigger_death_particles
        self.add_exp = add_exp

        # invisibility timer
        self.vulnerable = True
        self.hit_time = None
        self.invisibility_duration = 300

        # sounds
        self.hit_sound = pygame.mixer.Sound(get_path('../audio/hit.wav'))
        self.death_sound = pygame.mixer.Sound(get_path('../audio/death.wav'))
        self.attack_sound = pygame.mixer.Sound(monster_data[self.monster_name]['attack_sound'])
        self.hit_sound.set_volume(0.6)
        self.death_sound.set_volume(0.6)
        self.attack_sound.set_volume(0.3)

        # Pathfinding
        self.pathfinding_grid = pathfinding_grid
        self.tile_size = tile_size
        self.path = []
        self.last_path_time = 0
        self.path_recalc_interval = 500  # ms
        self._last_player_grid = None

    def import_graphics(self, name):
        self.animations = {'idle': [], 'move': [], 'attack': []}
        for animation in self.animations.keys():
            self.animations[animation] = import_folder(
                f'../graphics/monsters/{name}/' + animation)

    def get_player_distance_direction(self, player):
        enemy_vec = pygame.math.Vector2(self.rect.center)
        player_vec = pygame.math.Vector2(player.rect.center)
        distance = (player_vec - enemy_vec).magnitude()

        if distance > 0:
            direction = (player_vec - enemy_vec).normalize()
        else:
            direction = pygame.math.Vector2()

        return (distance, direction)

    def get_status(self, player):
        distance = self.get_player_distance_direction(player)[0]

        if distance <= self.attack_radius and self.can_attack:
            if self.status != 'attack':
                self.frame_index = 0
            self.status = 'attack'
        elif distance <= self.notice_radius:
            self.status = 'move'
        else:
            self.status = 'idle'
        # Clear path if not moving
        if self.status != 'move':
            self.path = []

    def actions(self, player):
        now = pygame.time.get_ticks()
        if self.status == 'attack':
            self.attack_time = now
            self.damage_player(self.attack_damage, self.attack_type)
            self.attack_sound.play()
        elif self.status == 'move':
            recalc = False
            if not self.path or now - self.last_path_time > self.path_recalc_interval:
                recalc = True
            else:
                # If player moved to a new grid cell, recalc
                current_player_grid = pos_to_grid(player.rect.center, self.tile_size)
                if self._last_player_grid != current_player_grid:
                    recalc = True
            if recalc and self.pathfinding_grid is not None:
                start = pos_to_grid(self.rect.center, self.tile_size)
                goal = pos_to_grid(player.rect.center, self.tile_size)
                self._last_player_grid = goal
                path = astar(self.pathfinding_grid, start, goal)
                if path and len(path) > 1:
                    self.path = path[1:]  # skip current position
                else:
                    self.path = []
                self.last_path_time = now
            # Follow path
            if self.path:
                next_node = self.path[0]
                next_pos = grid_to_pos(next_node, self.tile_size)
                vec_to_next = pygame.math.Vector2(next_pos) - pygame.math.Vector2(self.rect.center)
                if vec_to_next.length() < 4:  # close enough to node
                    self.path.pop(0)
                    if self.path:
                        next_node = self.path[0]
                        next_pos = grid_to_pos(next_node, self.tile_size)
                        vec_to_next = pygame.math.Vector2(next_pos) - pygame.math.Vector2(self.rect.center)
                if vec_to_next.length() > 0:
                    self.direction = vec_to_next.normalize()
                else:
                    self.direction = pygame.math.Vector2()
            else:
                self.direction = pygame.math.Vector2()
        else:
            self.direction = pygame.math.Vector2()

    def animate(self, dt):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            if self.status == 'attack':
                self.can_attack = False
            self.frame_index = 0

        self.image = animation[int(self.frame_index)]

        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def cooldown(self):
        current_time = pygame.time.get_ticks()
        if not self.can_attack:
            current_time = pygame.time.get_ticks()
            if current_time - self.attack_time >= self.attack_cooldown:
                self.can_attack = True

        if not self.vulnerable:
            if current_time - self.hit_time >= self.invisibility_duration:
                self.vulnerable = True

    def get_damage(self, player, attack_type):
        if self.vulnerable:
            self.hit_sound.play()
            self.direction = self.get_player_distance_direction(player)[1]
            if attack_type == 'weapon':
                self.health -= player.get_full_weapon_damage()
            else:  # magic
                self.health -= player.get_full_magic_damage()
            self.hit_time = pygame.time.get_ticks()
            self.vulnerable = False

    def check_death(self):
        if self.health <= 0:
            self.kill()
            self.trigger_death_particles(self.rect.center, self.monster_name)
            self.add_exp(self.exp)
            if self.trigger_exp_particles and self.last_player_pos:
                self.trigger_exp_particles(self.rect.center, self.last_player_pos, self.exp)
            self.death_sound.play()

    def hit_reaction(self):
        if not self.vulnerable:
            self.direction *= -self.resistance

    def update(self, dt):
        self.hit_reaction()
        self.move(self.speed, self.pos, dt)
        self.animate(dt)
        self.cooldown()
        self.check_death()

    def enemy_update(self, player):
        self.get_status(player)
        self.actions(player)
        # Store last player position for exp orb targeting
        self.last_player_pos = player.rect.center
