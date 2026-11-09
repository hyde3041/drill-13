from pico2d import *
import game_framework
import game_world
import item_mode
import pause_mode
import title_mode
from boy import Boy
from grass import Grass

pause_started_at = 0.0
suspended_input_events = []


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.push_mode(pause_mode)
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_i:
            game_framework.push_mode(item_mode)
            return
        else:
            boy.handle_event(event)

def init():
    global boy

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)

def update():
    game_world.update()

def render():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    game_world.clear()


def pause():
    global pause_started_at
    pause_started_at = get_time()
    suspended_input_events.clear()


def resume():
    # 정지한 시간은 잠들기까지의 대기 시간에서 제외한다.
    boy.idle_started_at += get_time() - pause_started_at
    # 정지 중 방향키를 놓은 경우에도 입력 상태를 갱신한다.
    for event in suspended_input_events:
        boy.handle_event(event)
    suspended_input_events.clear()


def remember_suspended_input(event):
    if (event.type in (SDL_KEYDOWN, SDL_KEYUP) and
            event.key in (SDLK_LEFT, SDLK_RIGHT)):
        suspended_input_events.append(event)

