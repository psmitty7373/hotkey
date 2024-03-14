#!/usr/bin/env python3

import fcntl, os, json, pygame, signal, sys, syslog, time
from keys import HIDKeyboard
from pygame.locals import *
from jsonschema import validate, ValidationError
from config_schema import config_schema
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from threading import Thread

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
CONFIG_FILE_PATH = 'config.json'
os.putenv('SDL_VIDEODRIVER', 'fbcon')
os.putenv('SDL_FBDEV', '/dev/fb0')

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith(CONFIG_FILE_PATH):
            self.callback()

class Hotkey(Thread):
    size_map = {
        9: 3,
        4: 2,
        1: 1
    }

    def __init__(self):
        super().__init__()
        self.running = False
        self.g = {'config': None}
        self.image_cache = {}
        self.grid_size = 10

        if self.load_config() == False:
            raise Exception('Error loading config')

        self.kb = None
        self.screen = None
        self.clock = None
        self.observer = None

    def initialize_touchscreen(self):
        self.ts = Touchscreen()

        def touch_handler(event, touch):
            if event == TS_PRESS:
                try:
                    macro = self.find_button(touch.x, touch.y)
                    if macro and macro in self.g['config']['macros'].keys() and 'action' in self.g['config']['macros'][macro].keys():  
                        self.kb.send_string(self.g['config']['macros'][macro]['action'])

                except Exception as e:
                    syslog.syslog(syslog.LOG_INFO, f'Error handling event: {e}')

            if event == TS_RELEASE:
                pass
            if event == TS_MOVE:
                pass

        for touch in self.ts.touches:
            touch.on_press = touch_handler
            touch.on_release = touch_handler
            touch.on_move = touch_handler

        self.ts.run()

    def initialize_pygame(self):
        pygame.init()
        size = (SCREEN_WIDTH, SCREEN_HEIGHT)
        self.screen = pygame.display.set_mode(size)
        pygame.mouse.set_visible(False)
        pygame.display.set_caption('hotkey')
        

    def position_buttons(self):
        for layout in self.g['config']['layouts'].keys():
            positions = []
            for button in self.g['config']['layouts'][layout]['buttons']:
                x = 0
                y = 0

                macro = ''
                if 'macro' in button.keys():
                    macro = button['macro']

                size = self.size_map[button["size"]]
                button_width = 144 * size
                button_height = 144 * size

                while any((pos[1] <= x < pos[1] + pos[3]) and (pos[2] <= y < pos[2] + pos[4]) for pos in positions):
                    x += 144
                    if x + button_width > 720:
                        x = 0
                        y += 144
                        if y + button_height > 720:
                            raise ValueError("Not enough space for button", macro)

                positions.append((macro, x, y, button_width, button_height))

                button['x'] = x
                button['y'] = y
                button['width'] = button_width
                button['height'] = button_height

                x += 144 * size
                if x >= 720:
                    x = 0
                    y += 144 * size
            self.g['config']['layouts'][layout]['positions'] = positions

    def find_button(self, x, y):
        positions = self.g['current_layout']['positions']
        for macro, button_x, button_y, button_width, button_height in positions:
            if x >= button_x and x < button_x + button_width and y >= button_y and y < button_y + button_height:
                return macro
        return None

    def draw_buttons(self):
        layout = self.g['current_layout']

        try:
            for button in layout['buttons']:
                if 'macro' in button.keys() and button['macro'] in self.g['config']['macros']:
                    macro = self.g['config']['macros'][button['macro']]
                    size = self.size_map[button["size"]]
                    image_filename = macro['image']

                    if image_filename not in self.image_cache.keys():
                        image_path = os.path.abspath(os.path.join('./images/', os.path.basename(macro['image'])))
                        self.image_cache[image_filename] = [None]*3
                        if os.path.exists(image_path) and os.path.isfile(image_path):
                            for i in range(1,4):
                                self.image_cache[image_filename][i-1] = pygame.transform.scale(pygame.image.load(image_path), (144 * i, 144 * i)).convert_alpha()

                    if image_filename in self.image_cache.keys():
                        self.screen.blit(self.image_cache[image_filename][size - 1], (button['x'], button['y']))
        except Exception as e:
            syslog.syslog(syslog.LOG_INFO, f'Error: {e}')
            return

    def load_config(self):
        try:
            with open(CONFIG_FILE_PATH, 'r') as file:
                fcntl.flock(file.fileno(), fcntl.LOCK_EX)
                self.g['config'] = json.load(file)
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)

            validate(instance=self.g['config'], schema=config_schema)

        except Exception as e:
            syslog.syslog(syslog.LOG_INFO, f'Error opening config: {e}')
            return False

        if 'current_layout' in self.g['config'].keys():
            self.g['current_layout'] = self.g['config']['layouts'][self.g['config']['current_layout']]
        else:
            self.g['current_layout'] = self.g['config']['layouts'][self.g['config']['layouts'].keys()[0]]

        self.position_buttons()

        return True

    def run(self):
        try:
            self.running = True

            self.kb = HIDKeyboard()
            syslog.syslog(syslog.LOG_INFO, 'Keyboard Initialized')
            self.initialize_touchscreen()
            syslog.syslog(syslog.LOG_INFO, 'Touchscreen Initialized')
            self.initialize_pygame()
            syslog.syslog(syslog.LOG_INFO, 'Pygame Initialized')
            self.clock = pygame.time.Clock()

            self.observer = Observer()
            self.observer.schedule(ConfigHandler(self.load_config), os.path.dirname(os.path.abspath(CONFIG_FILE_PATH)), recursive=False)
            self.observer.start()

            while self.running:
                for event in pygame.event.get():
                    if event.type == QUIT:
                        self.running = False
                        break

                self.screen.fill((0, 0, 0))
                self.draw_buttons()
                pygame.display.flip()

                self.clock.tick(10)

        except Exception as e:
            self.running = False
            syslog.syslog(syslog.LOG_INFO, f'Exception: {e}');

        finally:
            self.running = False
            pygame.quit()
            if self.ts:
                self.ts.stop()
            if self.kb:
                self.kb.close()
            if self.observer:
                self.observer.stop()
                self.observer.join()

def sigterm_handler(signum, frame):
    syslog.syslog(syslog.LOG_INFO, 'Quitting');
    hotkey.running = False
    sys.exit(0)

def main():
    try:
        signal.signal(signal.SIGINT, sigterm_handler)
        signal.signal(signal.SIGTERM, sigterm_handler)

        hotkey = Hotkey()
        hotkey.start()

        while True:
            time.sleep(1)

    except Exception as e:
        syslog.syslog(syslog.LOG_INFO, f'Exception: {e}');
        hotkey.running = False

    finally:
        hotkey.running = False


if __name__ == '__main__':
    main()
