import pygame
from pygame.math import Vector2 as vector

class WorldSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()

        self.offset = vector()
        self.half_w = self.display_surface.get_size()[0] // 2
        self.half_h = self.display_surface.get_size()[1] // 2

    def center_target_camera(self, target):
        """Have the player in the centre of the screen"""
        if 277 < target.rect.centerx < 713:
            self.offset.x = target.rect.centerx - self.half_w

        if target.rect.centery < 760:
            self.offset.y = target.rect.centery - self.half_h

        if self.offset.x == 142 and self.offset.y == 0:  # scenario where coming out of tunnel maps don't display correctly
            self.offset.x, self.offset.y = 139, 535
        elif self.offset.x == 404 and self.offset.y == 0:
            self.offset.x, self.offset.y = 401, 534


    def draw(self, player):
        self.center_target_camera(player)

        for sprite in self:
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)



class AllSprites(pygame.sprite.Group):
    def __init__(self, level):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector(0, 0)

        self.level = level
        self.edge = 0

        # camera box setup
        self.camera_borders = {'left': 150, 'right': 150, 'top': 0, 'bottom': 0}
        l = self.camera_borders['left']
        t = self.camera_borders['top']
        w = self.display_surface.get_size()[0] - (self.camera_borders['left'] + self.camera_borders['right'])
        h = self.display_surface.get_size()[1] - (self.camera_borders['top'] + self.camera_borders['bottom'])
        self.camera_rect = pygame.Rect(l, t, w, h)

    def box_target_camera(self, target_pos):
        if self.level == 1:
            self.edge = 1864
        else:
            self.edge = 1351

        if 160 < target_pos < self.edge:  # stops camera showing map cutoff 
            if target_pos < self.camera_rect.left:
                self.camera_rect.left = target_pos
            if target_pos > self.camera_rect.right:
                self.camera_rect.right = target_pos

            self.offset.x = -(self.camera_rect.left - self.camera_borders['left'])

        if self.offset.x==0 and target_pos>1876:
            self.offset.x = -1463
        
        

    def draw(self, target_pos, past_point):
        if not past_point:
            self.box_target_camera(target_pos[0])

        for sprite in self:
            offset_pos = sprite.rect.topleft + self.offset
            self.display_surface.blit(sprite.image, offset_pos)
            




