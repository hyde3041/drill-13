from pathlib import Path

import game_framework
from pico2d import *

image = None


def init():
    global image
    image = load_image(str(Path(__file__).with_name('title.png')))


def finish():
    global image
    image = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return


def update():
    pass


def render():
    clear_canvas()
    image.draw(get_canvas_width() / 2, get_canvas_height() / 2)
    update_canvas()
