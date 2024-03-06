#!/usr/bin/env python3

import os
import json
import pygame
import web
from keys import HIDKeyboard
from pygame.locals import *
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
from threading import Thread, Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

SCREEN_WIDTH = 720
SCREEN_HEIGHT = 720
CONFIG_FILE_PATH = 'config.json'
g = {'config': None}
image_cache = {}

size_map = {
    9: 3,
    4: 2,
    1: 1
}

class ConfigHandler(FileSystemEventHandler):
    def __init__(self, callback, lock):
        super().__init__()
        self.callback = callback
        self.lock = lock

    def on_modified(self, event):
        if event.src_path.endswith(CONFIG_FILE_PATH):
            with self.lock:
                pass

        self.callback()

def initialize_touchscreen(kb, g):
    ts = Touchscreen()

    def touch_handler(event, touch):
        layout = g['current_layout']
        if event == TS_PRESS:
            try:
                macro = find_button(layout['positions'], touch.x, touch.y)
                if macro and macro in g['config']['macros'].keys() and 'action' in g['config']['macros'][macro].keys():  
                    kb.send_string(g['config']['macros'][macro]['action'])

            except Exception as e:
                print(f'Error handling event: {e}')

        if event == TS_RELEASE:
            pass
        if event == TS_MOVE:
            pass

    for touch in ts.touches:
        touch.on_press = touch_handler
        touch.on_release = touch_handler
        touch.on_move = touch_handler

    ts.run()
    return ts

def initialize_pygame():
    pygame.init()
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('hotkey')
    return screen

def position_buttons():
    for layout in g['config']['layouts'].keys():
        positions = []
        for button in g['config']['layouts'][layout]['buttons']:
            x = 0
            y = 0

            macro = ''
            if 'macro' in button.keys():
                macro = button['macro']

            size = size_map[button["size"]]
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

        g['config']['layouts'][layout]['positions'] = positions

def find_button(positions, x, y):
    for macro, button_x, button_y, button_width, button_height in positions:
        if x >= button_x and x < button_x + button_width and y >= button_y and y < button_y + button_height:
            return macro
    return None

def draw_buttons(screen, layout):
    for button in layout['buttons']:
        if 'macro' in button.keys() and button['macro'] in g['config']['macros']:
            macro = g['config']['macros'][button['macro']]
            button_id = button["id"]
            size = size_map[button["size"]]
            image_filename = macro['image']

            if image_filename not in image_cache.keys():
                image_path = os.path.abspath(os.path.join('./images/', os.path.basename(macro['image'])))
                image_cache[image_filename] = [None]*3
                if os.path.exists(image_path) and os.path.isfile(image_path):
                    for i in range(0,3):
                        image_cache[image_filename][i] = pygame.transform.scale(pygame.image.load(image_path), (144 * i, 144 * i)).convert_alpha()

            if image_filename in image_cache.keys():
                screen.blit(image_cache[image_filename][size], (button['x'], button['y']))

def load_config():
    global g
    with open(CONFIG_FILE_PATH, 'r') as file:
        g['config'] = json.load(file)

    if 'current_layout' in g['config'].keys():
        g['current_layout'] = g['config']['layouts'][g['config']['current_layout']]
    else:
        g['current_layout'] = g['config']['layouts'][g['config']['layouts'].keys()[0]]

    position_buttons()

def main():
    grid_size = 10

    config_lock = Lock()
    load_config()

    kb = HIDKeyboard()
    print('Keyboard Initialized')
    ts = initialize_touchscreen(kb, g)
    print('Touchscreen Initialized')
    screen = initialize_pygame()
    print('Pygame Initialized')
    clock = pygame.time.Clock()

    web_handler = web.WebHandler(config_lock)
    web_handler.setDaemon(True)
    web_handler.start()

    observer = Observer()
    observer.schedule(ConfigHandler(load_config, config_lock), os.path.dirname(os.path.abspath(CONFIG_FILE_PATH)), recursive=False)
    observer.start()

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            screen.fill((0, 0, 0))
            draw_buttons(screen, g['current_layout'])
            pygame.display.flip()

            clock.tick(10)
        

    except KeyboardInterrupt:
        print('Quitting');
        pass

    finally:
        pygame.quit()
        ts.stop()
        kb.close()
        observer.stop()
        observer.join()

if __name__ == '__main__':
    main()
