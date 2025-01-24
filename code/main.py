from level2 import Level2
from level import Level
from pytmx.util_pygame import load_pygame
from support import *
from data import Data
from ui import UI
from overworld import Overworld
import sys

class Game:
    def __init__(self):
        """Intialise Game class"""
        pygame.init()
        pygame.display.set_caption('TMNT')
        self.screen = pygame.display.set_mode((550, 450))

        self.clock = pygame.time.Clock()
        self.import_assets()

        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        
        self.tmx_maps = {0: load_pygame(join('graphics', 'levels', '1.tmx'))}
        self.tmx_maps2 = {0: load_pygame(join('graphics', 'levels', '2.tmx'))}
        self.tmx_overworld = load_pygame(join('graphics', 'overworld', 'overworld.tmx'))
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.level_frames, self, 0, self.audio_files)

        self.current_level = 0

    def run_overworld(self, pos):
        """Load the overworld"""
        self.current_stage = Overworld(self.tmx_overworld, self.data, self.overworld_frames, self.level_frames, self, pos, self.audio_files)

    def start_level(self, num):
        """Load level depending on where the player is"""
        if num==1:  
            self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.data, self, num, self.audio_files)
            self.data.current_level = 1
        elif num==2:
            self.current_stage = Level(self.tmx_maps[0], self.level_frames, self.data, self, num, self.audio_files)
            self.data.current_level = 1
        elif num==3:
            self.current_stage = Level2(self.tmx_maps2[0], self.level_frames, self.data, self, num, self.audio_files)
            self.data.current_level = 2
        elif num==4:
            self.current_stage = Level2(self.tmx_maps2[0], self.level_frames, self.data, self, num, self.audio_files)
            self.data.current_level = 2
        
    def import_assets(self):
        """Import the graphics and audio files used in the game"""
        self.level_frames = {
            'player': import_sub_folders('graphics', 'player'),
            'enemy1': import_folder('graphics', 'enemies', 'enemy1'),
            'enemy2': import_folder('graphics', 'enemies', 'enemy2'),
            'enemy3': import_sub_folders('graphics', 'enemies', 'enemy3'),
            'enemy4': import_folder('graphics', 'enemies', 'enemy4'),
            'shuriken': import_image('graphics', 'enemies', 'shuriken', '0'),
            'items': import_image('graphics', 'items', 'pizza'),
            'particle': import_folder('graphics', 'effects', 'particle'),
            'april': import_image('graphics', 'extras', 'april', '0'),
            'rocksteady': import_image('graphics', 'extras', 'rocksteady', '0'),
            'both': import_image('graphics', 'extras', 'both', '0')
        }

        self.font = pygame.font.Font(join('graphics', 'ui', 'PressStart2P.ttf'), 15)

        self.ui_frames = {
            'health': import_image('graphics', 'ui', 'health'),
            'empty_health': import_image('graphics', 'ui', 'empty_health'),
            'sword': import_image('graphics', 'items', 'sword')
        }

        self.overworld_frames = {
            'icon': import_sub_folders('graphics', 'overworld', 'icon'),
            'enemy1': import_sub_folders('graphics', 'overworld', 'enemy')
        }

        self.audio_files = {
            'attack': pygame.mixer.Sound(join('audio', 'attack.wav')),
            'boss_battle': pygame.mixer.Sound(join('audio', 'boss_battle.wav')),
            'boss_clear': pygame.mixer.Sound(join('audio', 'boss_clear.wav')),
            'damage': pygame.mixer.Sound(join('audio', 'damage.wav')),
            'death': pygame.mixer.Sound(join('audio', 'death.wav')),
            'health': pygame.mixer.Sound(join('audio', 'health.wav')),
            'jump': pygame.mixer.Sound(join('audio', 'jump.wav')),
            'kill': pygame.mixer.Sound(join('audio', 'kill.wav')),
            'level': pygame.mixer.Sound(join('audio', 'level.wav')),
            'overworld': pygame.mixer.Sound(join('audio', 'overworld.wav'))
        }



    def run(self):
        """Initialise pygame"""
        while True:
            dt = self.clock.tick() / 1000  # frame rate
            if self.data.current_level == 0:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

            self.current_stage.run(dt)
            self.ui.update(dt)
            self.ui.check_level(self.data.current_level)
            pygame.display.update()




if __name__ == '__main__':
    game = Game()
    game.run()
