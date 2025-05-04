import pygame
from settings import *
from support import get_path, import_folder
from entity import Entity


class Player(Entity):
    def to_dict(self):
        return {
            'pos': {'x': self.pos.x, 'y': self.pos.y},
            'health': self.health,
            'energy': self.energy,
            'exp': self.exp,
            'stats': dict(self.stats),
            'max_stats': dict(self.max_stats),
            'upgrade_cost': dict(self.upgrade_cost),
            'weapon_index': self.weapon_index,
            'magic_index': self.magic_index
        }

    def from_dict(self, data):
        self.pos.x = data['pos']['x']
        self.pos.y = data['pos']['y']
        self.rect.center = (self.pos.x, self.pos.y)
        self.health = data['health']
        self.energy = data['energy']
        self.exp = data['exp']
        self.stats = dict(data['stats'])
        self.max_stats = dict(data['max_stats'])
        self.upgrade_cost = dict(data['upgrade_cost'])
        self.weapon_index = data['weapon_index']
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.magic_index = data['magic_index']
        self.magic = list(magic_data.keys())[self.magic_index]
    def __init__(self, pos, groups, obstacle_sprites, create_attack, destroy_attack, create_magic):
        super().__init__(groups, pos)
        player_path = get_path('../graphics/test/player.png')
        self.image = pygame.image.load(player_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(-6, HITBOX_OFFSET['player'])

        # graphics
        self.import_player_assets()
        self.status = 'down'

        # movement
        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None
        self.pos = pygame.math.Vector2(self.rect.center)

        self.obstacle_sprites = obstacle_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200

        # magic
        self.create_magic = create_magic
        self.magic_index = 0
        self.magic = list(magic_data.keys())[self.magic_index]
        self.can_switch_magic = True
        self.weapon_switch_time = None

        # stats
        self.stats = {
            'health': 100,
            'energy': 60,
            'attack': 10,
            'magic': 3,
            'speed': 300
        }
        self.max_stats = {
            'health': 300,
            'energy': 140,
            'attack': 20,
            'magic': 10,
            'speed': 720
        }
        self.upgrade_cost = {
            'health': 100,
            'energy': 100,
            'attack': 100,
            'magic': 100,
            'speed': 100
        }
        self.health = self.stats['health']
        self.energy = self.stats['energy']
        self.speed = self.stats['speed']
        self.exp = 0

        # damage timer
        self.vulnerable = True
        self.hurt_time = None
        self.invulnerability_duration = 500

        # sound
        self.weapon_attack_sound = pygame.mixer.Sound(
            get_path('../audio/sword.wav'))
        self.weapon_attack_sound.set_volume(0.2)

    def import_player_assets(self):
        character_path = get_path('../graphics/player')
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],
        }

        for animation in self.animations.keys():
            full_path = character_path + '/' + animation
            self.animations[animation] = import_folder(full_path)

    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # movement
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # attack
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()
                self.weapon_attack_sound.play()
                self.direction.x = 0
                self.direction.y = 0

            # magic
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

                style = list(magic_data.keys())[self.magic_index]
                strength = list(magic_data.values())[
                    self.magic_index]['strength'] + self.stats['magic']
                cost = list(magic_data.values())[self.magic_index]['cost']
                self.create_magic(style, strength, cost)
                self.direction.x = 0
                self.direction.y = 0

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()

                if self.weapon_index < len(list(weapon_data.keys()))-1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0

                self.weapon = list(weapon_data.keys())[self.weapon_index]

            if keys[pygame.K_e] and self.can_switch_magic:
                self.can_switch_magic = False
                self.magic_switch_time = pygame.time.get_ticks()

                if self.magic_index < len(list(magic_data.keys()))-1:
                    self.magic_index += 1
                else:
                    self.magic_index = 0

                self.magic = list(magic_data.keys())[self.magic_index]

    def get_status(self):
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

            if self.attacking:
                self.direction.x = 0
                self.direction.y = 0
                if not 'attack' in self.status:
                    if 'idle' in self.status:
                        self.status = self.status.replace('_idle', '_attack')
                    else:
                        self.status = self.status + '_attack'
            else:
                if 'attack' in self.status:
                    self.status = self.status.replace('_attack', '')

    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown + weapon_data[self.weapon]['cooldown']:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True

        if not self.can_switch_magic:
            if current_time - self.magic_switch_time >= self.switch_duration_cooldown:
                self.can_switch_magic = True

        if not self.vulnerable:
            if current_time - self.hurt_time >= self.invulnerability_duration:
                self.vulnerable = True

    def animate(self, dt):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(animation):
            self.frame_index = 0
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)

        current_time = pygame.time.get_ticks()
        # flicker
        if not self.vulnerable:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255)

    def get_full_weapon_damage(self):
        base_damage = self.stats['attack']
        weapon_damage = weapon_data[self.weapon]['damage']
        return base_damage + weapon_damage

    def get_full_magic_damage(self):
        base_damage = self.stats['magic']
        spell_damage = magic_data[self.magic]['strength']
        return base_damage + spell_damage

    def get_value_by_index(self, idx):
        return list(self.stats.values())[idx]

    def get_cost_by_index(self, idx):
        return list(self.upgrade_cost.values())[idx]

    def energy_recovery(self, dt):
        if self.energy < self.stats['energy']:
            self.energy += self.stats['magic'] * dt
        else:
            self.energy = self.stats['energy']

    def update(self, dt):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate(dt)
        self.move(self.stats['speed'], self.pos, dt)
        self.energy_recovery(dt)
