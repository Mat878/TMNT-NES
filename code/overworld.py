import pygame
from sprites import Sprite, Icon, Enemy5
from pygame.math import Vector2 as vector
from groups import WorldSprites

class Overworld:
    """The overworld map and its interactions"""
    def __init__(self, tmx_map, data, overworld_frames, level_frames, self1, pos, audio_files):
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.level_frames = level_frames
        self.pos = pos

        self.death_sound = audio_files['death']
        self.overworld_sound = audio_files['overworld']

        #groups
        self.all_sprites = WorldSprites()
        self.collision_sprites2 = pygame.sprite.Group()
        self.node_sprites = pygame.sprite.Group()
        self.node2_sprites = pygame.sprite.Group()
        self.node3_sprites = pygame.sprite.Group()
        self.node4_sprites = pygame.sprite.Group()
        self.enemy5_sprites = pygame.sprite.Group()

        self.setup(tmx_map, overworld_frames)

        self.self1 = self1

        
        

    def setup(self, tmx_map, overworld_frames):
        # Display background for map
        for layer in ['main', 'paths', 'node1', 'node2', 'node3', 'node4']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'main':
                    groups.append(self.collision_sprites2)
                elif layer == 'node1':
                    groups.append(self.node_sprites)
                elif layer == 'node2':
                    groups.append(self.node2_sprites)
                elif layer == 'node3':
                    groups.append(self.node3_sprites)
                elif layer == 'node4':
                    groups.append(self.node4_sprites)
                Sprite((x * 16, y * 16), surf, groups)

        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'Leo':
                self.icon = Icon(
                    pos = (obj.x, obj.y),
                    groups = self.all_sprites,
                    collision_sprites=self.collision_sprites2,
                    frames = overworld_frames['icon'],
                    node_sprites=self.node_sprites,
                    node2_sprites=self.node2_sprites,
                    node3_sprites=self.node3_sprites,
                    node4_sprites=self.node4_sprites,
                    overworld_self = self,
                    start_pos = self.pos,
                    overworld_sound = self.overworld_sound)
                
       # enemies in map
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'enemy1':
                Enemy5((obj.x, obj.y), overworld_frames['enemy1'], (self.all_sprites, self.enemy5_sprites), self.collision_sprites2)

    
    def attack_collision(self):
        """Handle collisions between sprites"""
        enemy_sprites =  self.enemy5_sprites.sprites()
        for target in enemy_sprites:
            if target.rect.colliderect(self.icon.rect):
                if self.icon.direction == vector(0, 0):
                    if self.icon.state == 'idle_right': self.icon.state = 'flat_right'
                    elif self.icon.state == 'idle_left': self.icon.state = 'flat_left'
                    elif self.icon.state == 'idle_up': self.icon.state = 'flat_up'
                    elif self.icon.state == 'idle': self.icon.state = 'flat_down'

                if self.icon.direction == vector(1, 0):  self.icon.state = 'flat_right'
                if self.icon.direction == vector(-1, 0): self.icon.state = 'flat_left'
                if self.icon.direction == vector(0, 1):  self.icon.state = 'flat_down'
                if self.icon.direction == vector(0, -1): self.icon.state = 'flat_up'

                self.icon.death = True
                self.data.health = 0

                self.overworld_sound.stop()
                self.death_sound.play()
                self.icon.death_timer.activate()
                    
            

    def node(self, num):
        self.self1.start_level(num)


    def run(self, dt):
        self.all_sprites.update(dt)
        self.all_sprites.draw(self.icon)
        self.attack_collision()

        

