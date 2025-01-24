import pygame
from sprites import Sprite, ParticleEffectsSprite, Item
from player import Player
from groups import AllSprites
from enemies import Enemy1, Enemy2, Enemy3, Enemy4, Shuriken
from timer import Timer

class Level2:
    def __init__(self, tmx_map, level_frames, data, main_self, start_pos, audio_files):
        self.display_surface = pygame.display.get_surface()
        self.data = data
        self.tmx_map = tmx_map
        self.level_frames = level_frames
        self.main_self = main_self
        self.start_pos = start_pos

        #audio
        self.audio_files = audio_files

        self.kill_sound = audio_files['kill']
        self.boss_battle_sound = audio_files['boss_battle']
        self.boss_clear_sound = audio_files['boss_clear']     

        # groups
        self.all_sprites = AllSprites(2)
        self.collision_sprites = pygame.sprite.Group()
        self.ladder_sprites = pygame.sprite.Group()
        self.laddertop_sprites = pygame.sprite.Group()
        self.enemy1_sprites = pygame.sprite.Group()
        self.enemy2_sprites = pygame.sprite.Group()
        self.enemy3_sprites = pygame.sprite.Group()
        self.enemy4_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.shuriken_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

        self.entrance_sprites = pygame.sprite.Group()
        self.exit_sprites = pygame.sprite.Group()

        self.setup(tmx_map, level_frames)

        self.shuriken_surf = level_frames['shuriken']
        self.particle_frames = level_frames['particle']

        self.attacked_timer = Timer(750)
        self.enemy4_timer = Timer(500)
        self.player_timer = Timer(2000)

        self.first_timer = True
        self.animation_called = False

        self.current_level = 2

        

    def setup(self, tmx_map, level_frames):
        # Display background for map
        for layer in ['Background', 'Walls', 'Ladders', 'Entrance', 'Exit']:
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
                level = 2,
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

    def create_enemy4(self):
        """Create the different enemy for the map"""
        for obj in self.tmx_map.get_layer_by_name('Enemies'):
            if obj.name == 'enemy4':
                self.enemy4 = Enemy4((obj.x, obj.y), self.level_frames['enemy4'], (self.all_sprites, self.damage_sprites, self.enemy4_sprites), self.collision_sprites)

        for obj in self.tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'April':
                self.sprite1 = Item((obj.x, obj.y), self.level_frames['april'], (self.all_sprites, self.item_sprites),
                     self.collision_sprites, self.data)
            elif obj.name == 'Rocksteady':
                self.sprite2 = Item((obj.x, obj.y), self.level_frames['rocksteady'], (self.all_sprites, self.item_sprites),
                     self.collision_sprites, self.data)

        self.boss_battle_sound.play(loops=-1)
        self.player.jump_height = 300 #  prevent player jumping on ledge

    def attack_collision(self):
        """Handle collisions between sprites"""
        enemy_sprites = self.shuriken_sprites.sprites() + self.enemy1_sprites.sprites() + self.enemy2_sprites.sprites() + self.enemy3_sprites.sprites() + self.enemy4_sprites.sprites()
        for target in enemy_sprites:
            facing_target = self.player.rect.centerx < target.rect.centerx and self.player.facing_right or \
                            self.player.rect.centerx > target.rect.centerx and not self.player.facing_right
            if target.rect.colliderect(self.player.rect) and self.player.attacking and facing_target:
                if target in self.enemy4_sprites.sprites():
                    if self.enemy4.health != 1 and not self.enemy4_timer.active:
                        self.enemy4.health -= 1
                        self.enemy4_timer.activate()
                    elif self.enemy4.health == 1:
                        self.boss_battle_sound.stop()
                        self.boss_clear_sound.play()

                        self.data.points += 4000
                        ParticleEffectsSprite(target.rect.center, self.particle_frames, self.all_sprites)
                        target.kill()
                        self.kill_sound.play()
                        self.kill_sound.set_volume(0.01)
                        self.player_timer.activate()

                        self.player.jump_height = 0
                        self.player.speed = 0
                        self.first_timer = False
                    break

                ParticleEffectsSprite(target.rect.center, self.particle_frames, self.all_sprites)
                target.kill()
                self.kill_sound.play()
                self.kill_sound.set_volume(0.01)

                if target in self.shuriken_sprites.sprites() or self.enemy1_sprites.sprites():
                    self.data.points += 100
                elif target in self.enemy2_sprites.sprites():
                    self.data.points += 200
                elif target in self.enemy3_sprites.sprites():
                    self.data.points += 800

    def animation(self):
        for obj in self.tmx_map.get_layer_by_name('Objects'):
            if obj.name == 'Both':
                self.sprite3 = Item((obj.x, obj.y), self.level_frames['both'], (self.all_sprites, self.item_sprites),
                     self.collision_sprites, self.data)
        self.animation_called = True

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
        self.attack_collision()

        self.attacked_timer.update()
        self.enemy4_timer.update()
        self.player_timer.update()

        self.all_sprites.draw(self.player.hitbox_rect.center, self.player.past_point)

        if not self.player_timer.active and not self.first_timer:
            self.player.jump_height = 310
            self.player.speed = 130
            self.sprite3.kill()
                
        try:
            if (self.sprite2.rect.x > 1350) and self.player.jump_height<300:
                self.sprite2.rect.x += -1 * .05
            elif self.sprite2.rect.x < 1350:
                self.sprite1.kill()
                self.sprite2.kill()

                if not self.animation_called:
                    self.animation()
        except:
            pass


        



