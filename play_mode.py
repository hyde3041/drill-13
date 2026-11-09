from pico2d import *
import game_framework
import game_world
import pause_mode
import title_mode
from boy import Boy
from grass import Grass

pause_started_at = 0.0


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


def resume():
    # 정지한 시간은 잠들기까지의 대기 시간에서 제외한다.
    boy.idle_started_at += get_time() - pause_started_at
    # 정지 중 방향키를 놓은 경우에도 입력 상태를 갱신한다.
    for event in pause_mode.input_events:
        boy.handle_event(event)
    pause_mode.input_events.clear()

