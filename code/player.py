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
            r'D:\prog\pygame_cyber-rpg\graphics\test\player.png').convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)

        self.direction = pygame.math.Vector2()
        self.speed = 5

        self.obstacles_sprites = obstacles_sprites

    def input(self):
        """
        Check if symbol was pressed and do action
        """
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.direction.y = -1
        elif keys[pygame.K_s]:
            self.direction.y = 1
        else:
            self.direction.y = 0

        if keys[pygame.K_d]:
            self.direction.x = 1
        elif keys[pygame.K_a]:
            self.direction.x = -1
        else:
            self.direction.x = 0

    def move(self, speed):

        # magnitude is length of vector: |AB| = v--x**2--+--y**2-/.
        # in pyagem .magnitude() computed automatically
        # for name_object = pygame.math.Vector2() while changing vectors direction

        debug(f"1 vector x,y: {self.direction}", 10, 10)
        debug(f"1 len vec: {self.direction.magnitude()}", 30, 10)

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()
        debug(self.direction * speed, 100, 10)
        # self.rect.center += self.direction * speed
        self.rect.x += self.direction.x * speed
        self.collision('horizontal')
        self.rect.y += self.direction.y * speed
        self.collision('vertical')

        debug(f"2 vector x,y: {self.direction}", 55, 10)
        debug(f"2 len vec: {self.direction.magnitude()}", 75, 10)

    def collision(self, direction):
        """
        Check collision between player sprite and other sprites
            and stop character if true  
        """
        if direction == 'horizontal':
            for sprite in self.obstacles_sprites:
                debug(sprite, 125, 10)
                if sprite.rect.colliderect(self.rect):
                    if self.direction.x > 0:  # moving right
                        self.rect.right = sprite.rect.left
                    if self.direction.x < 0:  # moving left
                        self.rect.left = sprite.rect.right

        if direction == 'vertical':
            for sprite in self.obstacles_sprites:
                debug(sprite, 145, 10)
                if sprite.rect.colliderect(self.rect):
                    if self.direction.y > 0:  # moving down
                        self.rect.bottom = sprite.rect.top
                    if self.direction.y < 0:  # moving up
                        self.rect.top = sprite.rect.bottom

    def update(self):
        self.input()
        self.move(self.speed)
