import pygame
from support import get_path, import_folder
from random import choice


class AnimationPlayer:
    def create_floating_text(self, text, pos, groups, color=(255, 255, 0), font_size=18, duration=1.2, rise_distance=30):
        """
        Spawn floating text at pos that rises and fades out.
        """
        FloatingText(text, pos, groups, color, font_size, duration, rise_distance)
    def __init__(self):
        self.frames = {
            # magic
            'flame': import_folder('../graphics/particles/flame/frames'),
            'aura': import_folder('../graphics/particles/aura'),
            'heal': import_folder('../graphics/particles/heal/frames'),

            # attacks
            'claw': import_folder('../graphics/particles/claw'),
            'slash': import_folder('../graphics/particles/slash'),
            'sparkle': import_folder('../graphics/particles/sparkle'),
            'leaf_attack': import_folder('../graphics/particles/leaf_attack'),
            'thunder': import_folder('../graphics/particles/thunder'),

            # monster deaths
            'squid': import_folder('../graphics/particles/smoke_orange'),
            'raccoon': import_folder('../graphics/particles/raccoon'),
            'spirit': import_folder('../graphics/particles/nova'),
            'bamboo': import_folder('../graphics/particles/bamboo'),

            # leafs
            'leaf': (
                import_folder('../graphics/particles/leaf1'),
                import_folder('../graphics/particles/leaf2'),
                import_folder('../graphics/particles/leaf3'),
                import_folder('../graphics/particles/leaf4'),
                import_folder('../graphics/particles/leaf5'),
                import_folder('../graphics/particles/leaf6'),
                self.reflect_images(import_folder('../graphics/particles/leaf1')),
                self.reflect_images(import_folder('../graphics/particles/leaf2')),
                self.reflect_images(import_folder('../graphics/particles/leaf3')),
                self.reflect_images(import_folder('../graphics/particles/leaf4')),
                self.reflect_images(import_folder('../graphics/particles/leaf5')),
                self.reflect_images(import_folder('../graphics/particles/leaf6')),
            ),
            # exp orb
            'exp_orb': import_folder('../graphics/particles/exp_orb'),
        }
    def create_exp_particles(self, pos, target_pos, groups, amount=5, speed=250, exp_amount=None):
        """
        Spawn several exp orb particles at pos, moving towards target_pos.
        """
        from random import uniform
        for _ in range(amount):
            # Add a small random offset to spawn position for spread
            offset = pygame.math.Vector2(uniform(-10, 10), uniform(-10, 10))
            spawn_pos = (pos[0] + offset.x, pos[1] + offset.y)
            MovingParticleEffect(
                spawn_pos,
                self.frames['exp_orb'],
                groups,
                target_pos=target_pos,
                speed=speed,
                sprite_type='exp_orb',
            )
        # Spawn floating text if exp_amount is provided
        if exp_amount is not None:
            self.create_floating_text(f"+{exp_amount} XP", pos, groups)
# FloatingText sprite for displaying temporary text in the world
class FloatingText(pygame.sprite.Sprite):
    def __init__(self, text, pos, groups, color=(255, 255, 0), font_size=18, duration=1.2, rise_distance=30):
        super().__init__(groups)
        self.font = pygame.font.Font(get_path('../font/joystix.ttf'), font_size)
        self.text = text
        self.color = color
        self.image = self.font.render(self.text, True, self.color)
        self.rect = self.image.get_rect(center=pos)
        self.start_pos = pygame.math.Vector2(pos)
        self.duration = duration
        self.elapsed = 0
        self.rise_distance = rise_distance
        self.alpha = 255

    def update(self, dt):
        self.elapsed += dt
        # Move up over time
        progress = min(self.elapsed / self.duration, 1.0)
        offset_y = -self.rise_distance * progress
        self.rect.center = (self.start_pos.x, self.start_pos.y + offset_y)
        # Fade out
        self.alpha = int(255 * (1 - progress))
        self.image.set_alpha(self.alpha)
        if self.elapsed >= self.duration:
            self.kill()
        }

    def reflect_images(self, frames):
        new_frames = []
        for frame in frames:
            flipped_frame = pygame.transform.flip(frame, True, False)
            new_frames.append(flipped_frame)

        return new_frames

    def create_grass_particles(self, pos, groups):
        grass_animation_frames = choice(self.frames['leaf'])
        ParticleEffect(pos, grass_animation_frames, groups)

    def create_particles(self, animation_type, pos, groups):
        animation_frames = self.frames[animation_type]
        ParticleEffect(pos, animation_frames, groups)



class ParticleEffect(pygame.sprite.Sprite):
    def __init__(self, pos, animation_frames, groups, sprite_type='magic'):
        super().__init__(groups)
        self.sprite_type = sprite_type
        self.frame_index = 0
        self.animation_speed = 15
        self.frames = animation_frames
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=pos)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index >= len(self.frames):
            self.kill()
        else:
            self.image = self.frames[int(self.frame_index)]

    def update(self, dt):
        self.animate(dt)


# MovingParticleEffect for exp orbs
class MovingParticleEffect(ParticleEffect):
    def __init__(self, pos, animation_frames, groups, target_pos, speed=250, sprite_type='exp_orb', max_lifetime=1.5):
        super().__init__(pos, animation_frames, groups, sprite_type)
        self.target_pos = pygame.math.Vector2(target_pos)
        self.pos = pygame.math.Vector2(pos)
        self.speed = speed  # pixels per second
        self.max_lifetime = max_lifetime  # seconds
        self.lifetime = 0

    def update(self, dt):
        # Move towards target
        direction = self.target_pos - self.pos
        distance = direction.length()
        if distance > 0:
            direction = direction.normalize()
            move_dist = min(self.speed * dt, distance)
            self.pos += direction * move_dist
            self.rect.center = (round(self.pos.x), round(self.pos.y))

        # Animate
        self.animate(dt)

        # Lifetime
        self.lifetime += dt
        if distance < 16 or self.lifetime > self.max_lifetime:
            self.kill()
