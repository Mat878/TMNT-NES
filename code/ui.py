import pygame
from sprites import Sprite

class UI:
    """Class which handles how the points and health of player are displayed"""
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.sprites = pygame.sprite.Group()
        self.font = font

        # hearts
        self.health_frames = frames['health']
        self.empty_health = frames['empty_health']
        self.sword = frames['sword']

        # points
        self.points_amount = 0

        self.overworld_view = False

    def show_points(self, amount):
        self.points_amount = amount

    def display_text(self):
        text_surf = self.font.render('Pts.' + str(self.points_amount).zfill(7), False, 'white')
        text_rect = text_surf.get_frect(topleft = (5, 395))
        self.display_surface.blit(text_surf, text_rect)

    def display_items(self):
        empty_rect = self.empty_health.get_frect(topleft=(195, 395))
        self.display_surface.blit(self.empty_health, empty_rect)

    def display_items2(self):
        sword_rect = self.sword.get_frect(topleft=(365, 395))
        self.display_surface.blit(self.sword, sword_rect)

    def create_health(self, amount):
        for sprite in self.sprites:
            sprite.kill()  # Remove sprites and add a new sprites

        sequence = [0, 8, 18, 26, 36, 44, 54, 62, 72, 80, 90, 98, 108, 116, 126, 134]
        for i in range(amount):
            x = 195 + sequence[i]
            y = 395
            Health((x,y), self.health_frames, self.sprites)

    def check_level(self, level):
        if level == 0:
            self.overworld_view = False
        else:
            self.overworld_view = True

    def update(self, dt):
        self.display_items()

        if self.overworld_view:
            self.display_items2()
            self.display_text()
        
        self.sprites.update(dt)
        self.sprites.draw(self.display_surface)
        


class Health(Sprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
