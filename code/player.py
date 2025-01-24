import pygame
import sys
from pygame.math import Vector2 as vector
from timer import Timer
from math import sin
import random

ANIMATION_SPEED = 5
first_call = False


class Player(pygame.sprite.Sprite):
    """A class for the player sprite in the game"""
    def __init__(self, pos, groups, collision_sprites, ladder_sprites, laddertop_sprites, frames, data, level, level_self, entrance_sprites, exit_sprites, main_self, start_pos, audio_files):
        super().__init__(groups)
        self.data = data

        # image
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = 'idle', True
        self.image = self.frames[self.state][self.frame_index]
        self.level = level
        self.level_self = level_self

        self.rect = self.image.get_frect(topleft = pos)
        self.hitbox_rect = self.rect.inflate(-100, -36)  # 50 l/r and 18 u/d -100 and -36
        self.old_rect = self.hitbox_rect.copy()

        # movement
        self.direction = vector()
        self.speed = 130
        self.gravity = 400
        self.jump = False
        self.jump_height = 310
        self.attacking = False
        self.ducking = False
        self.jumping = False  # true if jump key is currently being pressed
        self.jump2 = False  # true if doing jump2

        # collision
        self.collision_sprites = collision_sprites
        self.ladder_sprites = ladder_sprites
        self.laddertop_sprites = laddertop_sprites
        self.on_surface = {'floor': False, 'ladder': True}

        self.attack_timer = Timer(375)
        self.hit_timer = Timer(400)
        self.jump_timer = Timer(300)  # the time hold down key for jump2

        self.past_point = False

        self.entrance_sprites = entrance_sprites
        self.exit_sprites = exit_sprites

        self.main_self = main_self

        self.player_dead = False

        if start_pos == 2:
            self.on_surface['ladder'] = True
            self.state = 'climb_idle'
            self.hitbox_rect.center = (1934.389892578125, 107.1197509765625)
        elif start_pos == 4:
            self.hitbox_rect.center = (1300, 316.0)

        self.death_timer = Timer(3000)

        # audio
        self.jump_sound = audio_files['jump']
        self.death_sound = audio_files['death']
        self.attack_sound = audio_files['attack']
        self.damage_sound = audio_files['damage']
        self.boss_battle_sound = audio_files['boss_battle']
        self.level_sound = audio_files['level']
        self.level_sound.play(loops=-1)
        self.level_sound.set_volume(0.5)


    def event_loop(self):
        """Handle different key presses for player"""
        if self.data.current_level == 1 or 2:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        if not self.attack_timer.active and not self.on_surface['ladder']:
                            self.attack()
                            self.attack_timer.activate()
                            self.attack_sound.play()
                            self.attack_sound.set_volume(.1)
                    if event.key == pygame.K_x and self.on_surface['floor']:
                        self.jump = True
                        self.jumping = True
                        self.jump_timer.activate()
                    if event.key == pygame.K_DOWN and not self.on_surface['ladder']:
                        self.ducking = True
                    else:
                        self.ducking = False
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_DOWN:
                        self.ducking = False
                    if event.key == pygame.K_x:
                        self.jumping = False

        keys = pygame.key.get_pressed()
        input_vector = vector(0, 0)
        if keys[pygame.K_RIGHT]:
            if self.on_surface['ladder']:
                self.on_surface['ladder'] = False
            input_vector.x += 1
            self.facing_right = True
        if keys[pygame.K_LEFT]:
            if self.on_surface['ladder']:
                self.on_surface['ladder'] = False
            input_vector.x -= 1
            self.facing_right = False
        if keys[pygame.K_UP] and self.check_ladder():
            self.on_surface['ladder'] = True
            input_vector.y -= 1
        if keys[pygame.K_DOWN] and self.check_ladder():
            self.on_surface['ladder'] = True
            input_vector.y += 1
        if not self.check_ladder():
            self.on_surface['ladder'] = False

        self.direction.x = input_vector.normalize().x if input_vector else input_vector.x
        if self.on_surface['ladder']:
            self.direction.y = input_vector.normalize().y if input_vector else input_vector.y

    def attack(self):
        self.attacking = True
        self.frame_index = 0

    def move(self, dt):
        """Movement of player"""
        # horizontal
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collision('horizontal')

        # vertical
        if self.on_surface['ladder']: # move on ladder
            self.hitbox_rect.y += self.direction.y * self.speed * dt
        else:
            self.direction.y += self.gravity / 2 * dt
            self.hitbox_rect.y += self.direction.y * dt
            self.direction.y += self.gravity / 2 * dt
            self.collision('vertical')

        if self.jump:
            if self.on_surface['floor']:
                self.direction.y = -self.jump_height
                self.jump_sound.play()
                self.jump_sound.set_volume(0.01)
            self.jump = False

        self.rect.center = self.hitbox_rect.center

    def check_contact(self):
        """Check whether player in a collision"""
        floor_rect = pygame.Rect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 2))
        collide_rects = [sprite.rect for sprite in self.collision_sprites]

        # collisions
        self.on_surface['floor'] = True if floor_rect.collidelist(collide_rects) >= 0 else False

        # when on ladder, come of it when at bottom
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect) and self.on_surface['ladder']:
                if self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                    self.hitbox_rect.bottom = sprite.rect.top
                    self.on_surface['ladder'] = False

        for sprite in self.entrance_sprites:
            if sprite.rect.collidepoint(self.rect.center):
                self.level_sound.stop()
                if self.data.current_level == 1:
                    self.data.current_level = 0
                    self.main_self.run_overworld(0)
                else:
                    self.data.current_level = 0
                    self.main_self.run_overworld(2)

    
        for sprite in self.exit_sprites:
            if sprite.rect.collidepoint(self.rect.center):
                self.level_sound.stop()
                if self.data.current_level == 1:
                    self.data.current_level = 0
                    self.main_self.run_overworld(1)
                else:
                    self.data.current_level = 0
                    self.main_self.run_overworld(3)


    def check_ladder(self):
        """Check whether player can get onto ladder"""
        bottom_center_point1 = (self.hitbox_rect.centerx, self.hitbox_rect.bottom - 0.1)
        bottom_center_point2 = (self.hitbox_rect.centerx, self.hitbox_rect.bottom + 0.1)

        for sprite in self.ladder_sprites:
            if sprite.rect.collidepoint(bottom_center_point1) or sprite.rect.collidepoint(bottom_center_point2):
                return True


    def collision(self, axis):
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.hitbox_rect) or ((self.hitbox_rect.x < 992) and self.past_point):
                if axis == 'horizontal':
                    # left
                    if self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left >= sprite.old_rect.right:
                        self.hitbox_rect.left = sprite.rect.right

                    # right
                    if self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right <= sprite.old_rect.left:
                        self.hitbox_rect.right = sprite.rect.left
                else:  # vertical
                    # top
                    if self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.old_rect.bottom:
                        self.hitbox_rect.top = sprite.rect.bottom

                    # bottom
                    if self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                        self.hitbox_rect.bottom = sprite.rect.top
                    self.direction.y = 0

        for sprite in self.laddertop_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.old_rect.top:
                    self.hitbox_rect.bottom = sprite.rect.top



    def animate(self, dt):
        if self.on_surface['ladder']:
            self.frame_index += 10 * dt
        elif self.attacking:
            self.frame_index += 12 * dt
        elif self.jump2:
            self.frame_index += 20 * dt

        else:
            self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames[self.state]):  # only attack once
            self.state = 'idle'
            
        self.image = self.frames[self.state][int(self.frame_index % len(self.frames[self.state]))]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

        if self.state == 'death' and int(self.frame_index % len(self.frames[self.state])) == 3:
            self.state = 'death_idle'

        if self.attacking and self.frame_index > len(self.frames[self.state]):
            self.attacking = False

    def get_state(self):
        """Retrieve state of player"""
        global first_call
        if self.hit_timer.active:
            self.state = 'hit'
        elif self.on_surface['ladder']:
            self.state = 'climb_idle' if self.direction.y == 0 else 'climb'
        elif self.on_surface['floor']:
            self.jump2 = False
            first_call = False
            if self.attacking:
                self.state = 'attack'
            elif self.ducking and self.direction.x == 0:
                self.state = 'duck'
            else:
                self.state = 'idle' if self.direction.x == 0 else 'walk'
        else:
            if self.attacking:
                self.state = 'attack'
            elif self.jumping and not self.jump_timer.active:  # conditions where jump2 is true
                self.state = 'jump2'
                self.jump2 = True
                if not first_call:
                    self.direction.y = -self.jump_height
                    first_call = True
            elif self.jump2:
                self.state = 'jump2'
            else:
                self.state = 'jump1'  # includes falling as well which has same animation


    def get_damage(self, sprite, enemy3):
        """Reduce player health when hit"""
        if not self.hit_timer.active:
            if sprite in enemy3:
                self.data.health -= 2
                self.damage_sound.play()
                self.damage_sound.set_volume(0.1)
            else:
                self.data.health -= 1
                self.damage_sound.play()
                self.damage_sound.set_volume(0.1)
            self.hit_timer.activate()

    def flicker(self):
        """Animate player when sustain damage"""
        if self.hit_timer.active and sin(pygame.time.get_ticks() * 10) >= 0:
            mask = pygame.mask.from_surface(self.image)
            tinted_surf = mask.to_surface()
            tinted_surf.set_colorkey('black')
            light_blue = (173, 216, 230)
            tinted_surf.fill(light_blue, special_flags=pygame.BLEND_RGBA_MULT)
            self.image = tinted_surf

            self.hitbox_rect.x += random.choice((-0.5, 0.5))

            self.on_surface['ladder'] = False

    def check_past_point(self): 
        """When enemy4 is met, camera needs to be fixed and left hand side blocked, done using past_point"""
        if self.data.current_level == 2:
            if self.hitbox_rect.x > 1351 and not self.past_point:
                self.past_point = True
                self.level_sound.stop()
                self.level_self.create_enemy4()

    def check_health(self):
        """Check the health of player"""
        if self.data.health == 0:
            self.player_dead = True

            global ANIMATION_SPEED
            ANIMATION_SPEED = 3
            
            self.state = 'death'

            self.level_sound.stop()
            self.death_sound.play()

            self.death_timer.activate()
            


    def update(self, dt):
        if not self.player_dead:
            
            self.event_loop()

            self.attack_timer.update()
            self.hit_timer.update()
            self.jump_timer.update()

            self.old_rect = self.hitbox_rect.copy()

            self.move(dt)

            self.check_contact()
            try:
                self.check_past_point()
                
            except:
                pass

            self.get_state()
            
            self.flicker()
            self.check_health()
            

        self.animate(dt)

        self.death_timer.update()

        if not self.death_timer.active and self.player_dead:   
            pygame.quit()
            sys.exit()


