import os
import json
import pygame
import web
from keys import HIDKeyboard
from pygame.locals import *
from ft5406 import Touchscreen, TS_PRESS, TS_RELEASE, TS_MOVE
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

def set_backlight(value):
    file_path = "/sys/class/backlight/backlight/brightness"
    with open(file_path, "w") as f:
        if value:
            f.write("1")
        else:
            f.write("0")

def initialize_touchscreen(kb, grid, grid_size, square_size):
    ts = Touchscreen()
    set_backlight(True)

    def touch_handler(event, touch):
        if event == TS_PRESS:
            try:
                x, y = touch.x, touch.y
                grid_x = x // square_size
                grid_y = y // square_size
                if grid_y < len(grid) and grid_x < len(grid[grid_y]) and 'action' in grid[grid_y][grid_x].keys() and grid[grid_y][grid_x]['action']:
                    kb.send_string(grid[grid_y][grid_x]['action'])

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
    width, height = 720, 720
    size = (width, height)
    screen = pygame.display.set_mode(size)
    pygame.mouse.set_visible(False)
    pygame.display.set_caption('hotkey')
    return screen

def load_grid(grid_size, square_size, file_path):
    grid = []
    with open(file_path, 'r') as file:
        data = json.load(file)

    for y in range(grid_size):
        row = []
        for x in range(grid_size):
            if str(y) in data.keys() and str(x) in data[str(y)].keys():
                row.append(data[str(y)][str(x)])
            else:
                row.append({'image': '', 'color': (255, 255, 255), 'name': '', 'action': ''})
        grid.append(row)
    return grid

def draw_grid(screen, grid, grid_size, square_size):
    for y in range(grid_size):
        for x in range(grid_size):
            square = grid[y][x]
            if 'image' in square:
                image_path = os.path.join('./images/', square['image'])
                if os.path.exists(image_path) and os.path.isfile(image_path):
                    image = pygame.image.load(image_path)
                    image = pygame.transform.scale(image, (square_size, square_size))
                    screen.blit(image, (x * square_size, y * square_size))
            elif 'color' in square:
                color = square['color']
                pygame.draw.rect(screen, color, (x * square_size, y * square_size, square_size, square_size))

def main():
    grid_size = 5
    square_size = 144

    grid = load_grid(grid_size, square_size, 'config.json')

    kb = HIDKeyboard()
    ts = initialize_touchscreen(kb, grid, grid_size, square_size)
    screen = initialize_pygame()
    clock = pygame.time.Clock()

    web_thread = Thread(target=web.init_web_interface)
    web_thread.setDaemon(True)
    web_thread.start()

    try:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            screen.fill((0, 0, 0))
            draw_grid(screen, grid, grid_size, square_size)
            pygame.display.flip()

            clock.tick(10)
        

    except KeyboardInterrupt:
        print('Quitting');
        pass

    finally:
        set_backlight(False)
        pygame.quit()
        ts.stop()
        kb.close()

if __name__ == '__main__':
    main()
