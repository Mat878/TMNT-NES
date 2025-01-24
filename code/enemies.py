import pygame
from random import choice
from pygame.math import Vector2 as vector
from timer import Timer
from math import sin

ANIMATION_SPEED = 5

class Enemy1(pygame.sprite.Sprite):
    """Class to create enemy"""
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()

        self.collision_sprites = collision_sprites

        self.direction = vector(choice((-1, 1)),)
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 100
        self.gravity = 400

    def update(self, dt):
        """Animate and move enemy sprite"""
        
        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        if self.direction.x < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # move horizontally
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # move vertically
        self.direction.y += self.gravity / 2 * dt
        self.rect.y += self.direction.y * dt
        self.direction.y += self.gravity / 2 * dt
        self.collision('vertical')

        # reverse direction
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1, -1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1, -1))

        if floor_rect_right.collidelist(self.collision_rects) > 0 and self.direction.x > 0 or \
            floor_rect_left.collidelist(self.collision_rects) > 0 and self.direction.x < 0:
            self.direction.x *= -1

    def collision(self, axis):
        """Handle collision with wall or other sprites"""
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'horizontal':
                    # Moving left
                    if self.direction.x < 0:
                        self.rect.left = sprite.rect.right
                    # Moving right
                    elif self.direction.x > 0:
                        self.rect.right = sprite.rect.left

                elif axis == 'vertical':
                    # Moving up
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                    # Moving down
                    elif self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    self.direction.y = 0


class Enemy2(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 100

    def update(self, dt):

        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        if self.direction < 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # move
        self.rect.x += self.direction * self.speed * dt

        # reverse direction
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1,-1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,-1))

        if floor_rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0 or \
            floor_rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            self.direction *= -1

class Enemy3(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, player, create_shuriken):
        super().__init__(groups)

        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        self.player = player
        self.shoot_timer = Timer(500)
        self.has_fired = False
        self.create_shuriken = create_shuriken

    def state_management(self):
        # conditions where shoots: on screen, in line
        player_pos, enemy_pos = vector(self.player.hitbox_rect.center), vector(self.rect.center)
        player_near = enemy_pos.distance_to(player_pos) < 200
        player_level = abs(enemy_pos.y - player_pos.y) < 30

        if player_near and player_level and not self.shoot_timer.active:
            self.state = 'attack'
            self.frame_index = 0
            self.shoot_timer.activate()

    def update(self, dt):
        self.shoot_timer.update()
        self.state_management()

        # animation/attack
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames[self.state]):
            self.image = self.frames[self.state][int(self.frame_index)]

            if self.state == 'attack' and not self.has_fired:
                self.create_shuriken(self.rect.center)
                self.has_fired = True

        else:
            self.frame_index = 0
            if self.state == 'attack':
                self.state = 'idle'
                self.has_fired = False

class Enemy4(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)
        self.frames, self.frame_index = frames, 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)

        self.direction = choice((-1, 1))
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 125
        self.health = 10

    def flicker(self):
        """Change colour of enemey for when it recieves damage"""
        if sin(pygame.time.get_ticks() * 10) >= 0:
            mask = pygame.mask.from_surface(self.image)
            tinted_surf = mask.to_surface()
            tinted_surf.set_colorkey('black')
            light_blue = (173, 216, 230)
            tinted_surf.fill(light_blue, special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted_surf

    def update(self, dt):
        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]
        if self.direction > 0:
            self.image = pygame.transform.flip(self.image, True, False)

        # move
        self.rect.x += self.direction * self.speed * dt

        # reverse direction
        floor_rect_right = pygame.FRect(self.rect.bottomright, (1,-1))
        floor_rect_left = pygame.FRect(self.rect.bottomleft, (-1,-1))

        if floor_rect_right.collidelist(self.collision_rects) > 0 and self.direction > 0 or \
            floor_rect_left.collidelist(self.collision_rects) > 0 and self.direction < 0:
            self.direction *= -1



class Shuriken(pygame.sprite.Sprite):
    """Create item thrown by enemey4"""
    def __init__(self, pos, groups, surf, speed):
        self.shuriken = True
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = pos + vector(5, -30))
        self.speed = speed

    def update(self, dt):
        self.rect.x += -1 * self.speed * dt