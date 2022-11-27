import pygame
from settings import *
from debug import debug
from support import *



class Player(pygame.sprite.Sprite):
    """
    Load image from folder and create pygame object for working with image movements
        and player object values
    """
    def __init__(self,
                 pos: tuple,
                 groups: list,
                 obstacles_sprites: list,
                 create_attack: object,
                 destroy_attack: object):
        super().__init__(groups)

        print('type:', type(create_attack))

        self.image = pygame.image.load(
            r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\test\player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        # graphics setup
        self.import_player_assets()
        self.status = 'up'
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement
        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.attacking = False
        self.attack_cooldown = 400
        self.attack_time = None

        self.obstacles_sprites = obstacles_sprites

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0  # for select different weapons
        self.weapon = list(weapon_data.keys())[self.weapon_index]
        self.can_switch_weapon = True
        self.weapon_switch_time = None
        self.switch_duration_cooldown = 200


    def import_player_assets(self):
        character_path = r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\player'
        self.animations = {
            'up': [], 'down': [], 'left': [], 'right': [],
            'right_idle': [], 'left_idle': [], 'up_idle': [], 'down_idle': [],
            'right_attack': [], 'left_attack': [], 'up_attack': [], 'down_attack': [],
        }

        for animation in self.animations.keys():
            full_path = character_path + '\\' + animation
            self.animations[animation] = import_folder(full_path)


    def input(self):
        """
        Check if symbol was pressed and do action
        """
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # movement input
            if keys[pygame.K_w] or keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            else:
                self.direction.x = 0

            # attack input
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

                debug('attack', 500, 10)

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                debug('magic', 500, 10)

            if keys[pygame.K_q] and self.can_switch_weapon:
                self.can_switch_weapon = False
                self.weapon_switch_time = pygame.time.get_ticks()
                
                if self.weapon_index < len(list(weapon_data.keys()))-1:
                    self.weapon_index += 1
                else:
                    self.weapon_index = 0
                    
                self.weapon = list(weapon_data.keys())[self.weapon_index]


    def get_status(self):
        # idle status
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


    def move(self, speed):
        # magnitude is length of vector: |AB| = v--x**2--+--y**2-/.
        # in pyagem .magnitude() computed automatically
        # for name_object = pygame.math.Vector2() while changing vectors direction

        debug(f"1 vec x,y: {self.direction}", 10, 10)
        debug(f"1 len: {self.direction.magnitude()}", 55, 10)
        debug(f"1 speed: {self.direction * speed}", 100, 10)
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center

        debug(f"2 vec x,y: {self.direction}", 30, 10)
        debug(f"2 len: {self.direction.magnitude()}", 75, 10)
        debug(f"2 speed: {self.direction * speed}", 120, 10)


    def collision(self, direction):
        """
        Check collision between player sprite and other sprites
            and stop character if true  
        """
        if direction == 'horizontal':
            for sprite in self.obstacles_sprites:
                # debug(sprite, 125, 10)
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0:  # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0:  # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == 'vertical':
            for sprite in self.obstacles_sprites:
                # debug(sprite, 145, 10)
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0:  # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0:  # moving up
                        self.hitbox.top = sprite.hitbox.bottom


    def cooldowns(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cooldown:
                self.attacking = False
                self.destroy_attack()

        if not self.can_switch_weapon:
            if current_time - self.weapon_switch_time >= self.switch_duration_cooldown:
                self.can_switch_weapon = True


    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center=self.hitbox.center)


    def update(self):
        self.input()
        self.cooldowns()
        self.get_status()
        self.animate()
        self.move(self.speed)
