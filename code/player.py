import pygame
from settings import *
from debug import debug


class Player(pygame.sprite.Sprite):
    """
    Load image from folder and create pygame object for working with image movements
        and player object values
    """

    def __init__(self, pos: tuple, groups: list, obstacles_sprites: list):
        super().__init__(groups)
        self.image = pygame.image.load(
            r'D:\prog\cyber-zelda-rpg\graphics\test\player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.hitbox = self.rect.inflate(0, -26)

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.obstacles_sprites = obstacles_sprites

    def input(self):
        """
        Check if symbol was pressed and do action
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
        else:
            self.direction.x = 0

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

    def update(self):
        self.input()
        self.move(self.speed)
