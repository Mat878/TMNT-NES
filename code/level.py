import pygame
from sprites import Sprite, Item, ParticleEffectsSprite
from player import Player
from groups import AllSprites
from enemies import Enemy1, Enemy2, Enemy3, Shuriken
from timer import Timer
from data import Data

class Level:
    def __init__(self, tmx_map, level_frames, data, main_self, start_pos, audio_files):
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.main_self = main_self
        self.start_pos = start_pos

        #audio
        self.audio_files = audio_files
        self.health_sound = audio_files['health']
        self.kill_sound = audio_files['kill']

        # groups
        self.all_sprites = AllSprites(1)
        self.collision_sprites = pygame.sprite.Group()
        self.ladder_sprites = pygame.sprite.Group()
        self.laddertop_sprites = pygame.sprite.Group()
        self.enemy1_sprites = pygame.sprite.Group()
        self.enemy2_sprites = pygame.sprite.Group()
        self.enemy3_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.shuriken_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()
        
        self.entrance_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()

        self.setup(tmx_map, level_frames)

        self.shuriken_surf = level_frames['shuriken']
        self.particle_frames = level_frames['particle']

        self.attacked_timer = Timer(750)

        self.current_level = 1
 
        

        

    def setup(self, tmx_map, level_frames):
        # Display background for map
        for layer in ['Background', 'Walls', 'Ladders', 'LadderTop', 'Entrance', 'Exit']:
            for x, y, surf in tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if layer == 'Walls':
                    groups.append(self.collision_sprites)
                elif layer == 'Ladders':
                    groups.append(self.ladder_sprites)
                elif layer == 'LadderTop':
                    groups.append(self.laddertop_sprites)
                elif layer == 'Entrance':
                    groups.append(self.entrance_sprites)
                elif layer == 'Exit':
                    groups.append(self.exit_sprites)
                Sprite((x * 32, y * 32), surf, groups)

        # Object in map
        for obj in tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'Leonardo':
                self.player = Player(
                pos = (obj.x, obj.y),
                groups = self.all_sprites,
                collision_sprites = self.collision_sprites,
                ladder_sprites = self.ladder_sprites,
                laddertop_sprites = self.laddertop_sprites,
                frames = level_frames['player'],
                data = self.data,
                level = 1,
                level_self = self,
                entrance_sprites = self.entrance_sprites,
                exit_sprites = self.exit_sprites,
                main_self = self.main_self,
                start_pos = self.start_pos,
                audio_files = self.audio_files)

        # enemies in map
        for obj in tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'enemy1':
                self.enemy1 = Enemy1((obj.x, obj.y), level_frames['enemy1'], (self.all_sprites, self.damage_sprites, self.enemy1_sprites), self.collision_sprites)
            elif obj.name == 'enemy2':
                self.enemy2 = Enemy2((obj.x, obj.y), level_frames['enemy2'], (self.all_sprites, self.damage_sprites, self.enemy2_sprites), self.collision_sprites)
            elif obj.name == 'enemy3':
                Enemy3(
                    pos = (obj.x, obj.y),
                    frames = level_frames['enemy3'],
                    groups = (self.all_sprites, self.damage_sprites, self.enemy3_sprites),
                    collision_sprites = self.collision_sprites,
                    player = self.player,
                    create_shuriken = self.create_shuriken)

        for obj in tmx_map.get_layer_by_name('Items'):
            Item((obj.x, obj.y), level_frames['items'], (self.all_sprites, self.item_sprites), self.collision_sprites, self.data)

    def item_collision(self):
        """When player hits health object"""
        if self.item_sprites:
            item_sprites = pygame.sprite.spritecollide(self.player, self.item_sprites, True)
            if item_sprites:
                self.health_sound.play()
                item_sprites[0].activate()

    def attack_collision(self):
        """Handle collisions between sprites"""
        enemy_sprites = self.shuriken_sprites.sprites() + self.enemy1_sprites.sprites() + self.enemy2_sprites.sprites() + self.enemy3_sprites.sprites()
        for target in enemy_sprites:
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                ParticleEffectsSprite(target.rect.center, self.particle_frames, self.all_sprites)
                if target in self.shuriken_sprites.sprites() or self.enemy1_sprites.sprites():
                    self.data.points += 100
                elif target in self.enemy2_sprites.sprites():
                    self.data.points += 200
                elif target in self.enemy3_sprites.sprites():
                    self.data.points += 800
                target.kill()
                self.kill_sound.play()
                self.kill_sound.set_volume(0.01)



    def create_shuriken(self, pos):
        Shuriken(pos, (self.all_sprites, self.damage_sprites, self.shuriken_sprites), self.shuriken_surf, 150)

    def shuriken_collision(self):
        for sprite in self.collision_sprites:
            pygame.sprite.spritecollide(sprite, self.shuriken_sprites, True)

    def hit_collision(self):
        for sprite in self.damage_sprites:
            if sprite.rect.colliderect(self.player.hitbox_rect) and not self.attacked_timer.active:
                self.attacked_timer.activate()
                self.player.get_damage(sprite, self.enemy3_sprites)
                if hasattr(sprite, 'shuriken'):
                    sprite.kill()

    def run(self, dt):
        self.all_sprites.update(dt)
        self.shuriken_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        self.attacked_timer.update()

        self.all_sprites.draw(self.player.hitbox_rect.center, False)

