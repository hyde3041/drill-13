from pathlib import Path

import game_framework
import game_world
import pico2d
import title_mode
from pico2d import *

font = None
input_events = []


def init():
    global font
    input_events.clear()
    font_path = Path(pico2d.__file__).parent / 'data' / 'ConsolaMalgun.ttf'
    font = load_font(str(font_path), 24)


def finish():
    global font
    TTF_CloseFont(font.font)
    font = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.pop_mode()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.pop_mode()
            game_framework.change_mode(title_mode)
            return
        elif (event.type in (SDL_KEYDOWN, SDL_KEYUP) and
              event.key in (SDLK_LEFT, SDLK_RIGHT)):
            input_events.append(event)


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    x, y = get_canvas_width() / 2, get_canvas_height() / 2
    draw_rectangle(x - 180, y - 55, x + 180, y + 55,
                   30, 30, 30, filled=True)
    font.draw(x - 42, y + 20, 'PAUSED', (255, 255, 255))
    font.draw(x - 140, y - 20, 'P: Resume  Esc: Title', (255, 255, 255))
    update_canvas()
