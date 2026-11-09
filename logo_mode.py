from pathlib import Path
import game_framework
import title_mode
from pico2d import *

image = None
logo_start_time = 0.0

def init():
    global image, logo_start_time
    image = load_image(str(Path(__file__).with_name('tuk_credit.png')))
    logo_start_time = get_time()

def finish():
    global image
    del image

def update():
    if get_time() - logo_start_time >= 2.0:
        game_framework.change_mode(title_mode)

def render():
    clear_canvas()
    image.draw(400, 300)
    update_canvas()

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return