import pygame
from pygame.math import Vector2 as vector
from random import choice
import sys
from timer import Timer
ANIMATION_SPEED = 10


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf=pygame.Surface((32, 32)), groups=None):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)  # starting position of sprite
        self.old_rect = self.rect.copy()

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, data):
        super().__init__(groups)
        self.image = frames
        self.rect = self.image.get_frect(topleft = pos)
        self.data = data

    def activate(self):
        for _ in range(4):
            if self.data.health < 16:
                self.data.health += 1


class AnimatedSprite(Sprite):
    def __init__(self, pos, frames, groups, animation_speed = ANIMATION_SPEED):
        self.frames, self.frame_index = frames, 0
        super().__init__(pos, self.frames[self.frame_index], groups)
        self.animation_speed = animation_speed

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt):
        self.animate(dt)


class ParticleEffectsSprite(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.rect.center = pos

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collision_sprites, frames, node_sprites, node2_sprites, node3_sprites, node4_sprites, overworld_self, start_pos, overworld_sound):
        super().__init__(groups)
        self.icon = True
        self.direction = vector()
        self.speed = 100

        # image
        self.frames, self.frame_index = frames, 0
        self.state = 'idle'
        self.image = self.frames[self.state][self.frame_index]
        self.death = False

        # rect
        self.rect = self.image.get_frect(center = pos)

        self.collision_sprites = collision_sprites
        self.node_sprites = node_sprites
        self.node2_sprites = node2_sprites
        self.node3_sprites = node3_sprites
        self.node4_sprites = node4_sprites

        self.overworld_self = overworld_self

        if start_pos == 0:
            self.rect.x, self.rect.y = 280, 546
        elif start_pos == 1:
            self.rect.x, self.rect.y = 405, 850
        elif start_pos == 2:
            self.rect.x, self.rect.y = 667, 818
        elif start_pos == 3:
            self.rect.x, self.rect.y = 667, 600    

        self.death_timer = Timer(2500)
        
        #audio
        self.overworld_sound = overworld_sound
        self.overworld_sound.play(loops=-1)


    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]

    def get_state(self):
        if self.direction == vector(0, 0):
            if self.state == 'right': self.state = 'idle_right'
            elif self.state == 'left': self.state = 'idle_left'
            elif self.state == 'up': self.state = 'idle_up'
            elif self.state == 'down': self.state = 'idle'
        if self.direction == vector(1, 0):  self.state = 'right'
        if self.direction == vector(-1, 0): self.state = 'left'
        if self.direction == vector(0, 1):  self.state = 'down'
        if self.direction == vector(0, -1): self.state = 'up'

    def input(self):
        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)
        if keys[pygame.K_DOWN]:
            input_vector.y += 1
        elif keys[pygame.K_LEFT]:
            input_vector.x -= 1
        elif keys[pygame.K_RIGHT]:
            input_vector.x += 1
        elif keys[pygame.K_UP]:
            input_vector.y -= 1
        self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
        self.direction.y = input_vector.normalize().y if input_vector else input_vector.y

    def move(self, dt):
        self.rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')
        self.rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'horizontal':
                    # left
                    if self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.rect.left = sprite.rect.right

                    # right
                    if self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.rect.right = sprite.rect.left
                else:
                    # top
                    if self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.rect.top = sprite.rect.bottom

                    # bottom
                    if self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.rect.bottom = sprite.rect.top

        for sprite in self.node_sprites:
            if sprite.rect.collidepoint(self.rect.center):
                self.overworld_sound.stop()
                self.overworld_self.node(1)
        
        for sprite in self.node2_sprites:
            if sprite.rect.collidepoint(self.rect.center):
                self.overworld_sound.stop()
                self.overworld_self.node(2)

        for sprite in self.node3_sprites:
            if sprite.rect.collidepoint(self.rect.center):
                self.overworld_sound.stop()
                self.overworld_self.node(3)

    def update(self, dt):
        if not self.death:
            self.old_rect = self.rect.copy()
            
            self.input()
            self.move(dt)

            self.get_state()
        self.animate(dt)

        self.death_timer.update()
        
        if not self.death_timer.active and self.death:   
            pygame.quit()
            sys.exit()




class Enemy5(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites):
        super().__init__(groups)

        self.frames, self.frame_index = frames, 0
        self.state = 'down'
        self.image = self.frames[self.state][self.frame_index]

        self.rect = self.image.get_frect(topleft = pos)
        self.old_rect = self.rect.copy()

        self.collision_sprites = collision_sprites

        self.direction = vector(1,)
        self.collision_rects = [sprite.rect for sprite in collision_sprites]
        self.speed = 100

    def update(self, dt):

        # animate
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        if self.direction.y < 0:
            self.state = 'up'
        else:
            self.state = 'down'

        # move
        self.rect.y += self.direction.y * self.speed * dt
        self.collision('vertical')

        # reverse direction
        floor_rect_up = pygame.FRect(self.rect.midtop, (1, -1))
        floor_rect_down = pygame.FRect(self.rect.midbottom, (1, 1))

        if floor_rect_up.collidelist(self.collision_rects) > 0 and self.direction.y < 0 or \
            floor_rect_down.collidelist(self.collision_rects) > 0 and self.direction.y > 0:
            self.direction.y *= -1

    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if axis == 'vertical':
                    # Moving up
                    if self.direction.y < 0:
                        self.rect.top = sprite.rect.bottom
                    # Moving down
                    elif self.direction.y > 0:
                        self.rect.bottom = sprite.rect.top
                    self.direction.y = 0