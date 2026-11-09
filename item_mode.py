from pathlib import Path

import game_framework
import game_world
import pico2d
import play_mode
from pico2d import *

image = None
font = None
selections = {SDLK_0: 0, SDLK_1: 1, SDLK_2: 2}
item_names = {0: 'None', 1: 'Small ball', 2: 'Big ball'}


def init():
    global image, font
    image = load_image(str(Path(__file__).with_name('item_select.png')))
    font_path = Path(pico2d.__file__).parent / 'data' / 'ConsolaMalgun.ttf'
    font = load_font(str(font_path), 24)


def finish():
    global image, font
    if font is not None:
        TTF_CloseFont(font.font)
    font = None
    image = None


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN:
            if event.key in selections:
                play_mode.boy.select_ball(selections[event.key])
                game_framework.pop_mode()
                return
            elif event.key in (SDLK_i, SDLK_ESCAPE):
                game_framework.pop_mode()
                return
            else:
                play_mode.remember_suspended_input(event)
        else:
            play_mode.remember_suspended_input(event)


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    x, y = get_canvas_width() / 2, get_canvas_height() / 2
    draw_rectangle(x - 180, y - 180, x + 180, y + 180,
                   30, 30, 30, filled=True)
    font.draw(x - 80, y + 150, 'ITEM SELECT', (255, 255, 255))
    image.draw(x, y + 10)
    font.draw(x - 150, y - 125,
              'Current: ' + item_names[play_mode.boy.ball_type], (255, 255, 255))
    font.draw(x - 150, y - 155, 'I / Esc: Cancel', (255, 255, 255))
    update_canvas()
