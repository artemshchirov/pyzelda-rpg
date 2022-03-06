import pygame


class Weapon(pygame.sprite.Sprite):
    def __init__(self, player, groups):
        super().__init__(groups)
        direction = player.status.split('_')[0]  # cut '_idle'

        # graphic
        full_path = r'C:\Users\artem\Documents\GitHub\cyber-zelda-rpg\graphics\weapons' + \
            f'\\{player.weapon}\\{direction}.png'
        self.image = pygame.image.load(full_path).convert_alpha()

        # placement
        if direction == 'right':
            self.rect = self.image.get_rect(
                midleft=player.rect.midright + pygame.math.Vector2(0, 16))
        elif direction == 'left':
            self.rect = self.image.get_rect(
                midright=player.rect.midleft + pygame.math.Vector2(0, 16))
        elif direction == 'down':
            self.rect = self.image.get_rect(
                midtop=player.rect.midbottom + pygame.math.Vector2(-10, 0))
        else:  # up
            self.rect = self.image.get_rect(
                midbottom=player.rect.midtop + pygame.math.Vector2(-10, 0))
