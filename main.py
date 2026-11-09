from pico2d import *
import game_framework
import logo_mode

open_canvas()
try:
    game_framework.run(logo_mode)
finally:
    close_canvas()
