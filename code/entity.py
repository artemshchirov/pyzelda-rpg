import pygame
from math import sin


class Entity(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(groups)
        self.frame_index = 0
        self.animation_speed = 4
        self.direction = pygame.math.Vector2()

    def move(self, speed, pos, dt):
        self.pos = pos

        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        # horizontal movement
        self.pos.x += self.direction.x * speed * dt
        self.hitbox.centerx = round(self.pos.x)
        self.rect.centerx = self.hitbox.centerx
        self.collision('horizontal')

        # vertical movement
        self.pos.y += self.direction.y * speed * dt
        self.hitbox.centery = round(self.pos.y)
        self.rect.centery = self.hitbox.centery
        self.collision('vertical')

    def collision(self, direction):
        for sprite in self.obstacle_sprites.sprites():
            if hasattr(sprite, 'hitbox'):
                if sprite.hitbox.colliderect(self.hitbox):
                    if direction == 'horizontal':
                        if self.direction.x > 0:  # moving right
                            self.hitbox.right = sprite.hitbox.left
                        if self.direction.x < 0:  # moving left
                            self.hitbox.left = sprite.hitbox.right
                        self.rect.centerx = self.hitbox.centerx
                        self.pos.x = self.hitbox.centerx

                    if direction == 'vertical':
                        if self.direction.y < 0:  # moving up
                            self.hitbox.top = sprite.hitbox.bottom
                        if self.direction.y > 0:  # moving down
                            self.hitbox.bottom = sprite.hitbox.top
                        self.rect.centery = self.hitbox.centery
                        self.pos.y = self.hitbox.centery

    def wave_value(self):
        value = sin(pygame.time.get_ticks())
        if value >= 0:
            return 255
        return 0
