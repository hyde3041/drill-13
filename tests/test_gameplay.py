"""Real SDL input and rendering checks for the item and pause modes.

Run from the project root: python -m unittest discover -s tests -v
"""

import ctypes
import unittest

import pico2d
import sdl2

import game_framework as framework
import game_world
import item_mode
import pause_mode
import play_mode
import title_mode
from ball import Ball


class GameplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pico2d.open_canvas()

    @classmethod
    def tearDownClass(cls):
        Ball.images.clear()
        pico2d.close_canvas()

    def setUp(self):
        pico2d.get_events()
        game_world.clear()
        framework.stack = []
        framework.running = True
        framework.change_mode(play_mode)

    def tearDown(self):
        while framework.stack:
            framework.stack.pop().finish()
        framework.running = False

    def key(self, code, kind=sdl2.SDL_KEYDOWN, repeat=0):
        event = sdl2.SDL_Event()
        event.type = kind
        event.key.keysym.sym = code
        event.key.repeat = repeat
        self.assertEqual(sdl2.SDL_PushEvent(ctypes.byref(event)), 1)
        framework.stack[-1].handle_events()

    def frames(self, count=1):
        for _ in range(count):
            framework.stack[-1].update()
            framework.stack[-1].render()

    def snapshot(self):
        return tuple((id(obj), getattr(obj, 'x', None), getattr(obj, 'y', None),
                      getattr(obj, 'frame', None), getattr(obj, 'state', None))
                     for layer in game_world.world for obj in layer)

    def test_three_selections_change_only_new_shots(self):
        boy = play_mode.boy
        shots = []
        for code, selection, width in ((sdl2.SDLK_0, 0, None),
                                        (sdl2.SDLK_1, 1, 23),
                                        (sdl2.SDLK_2, 2, 43)):
            self.key(sdl2.SDLK_i)
            self.assertEqual(framework.stack, [play_mode, item_mode])
            self.frames()
            self.key(code)
            self.assertEqual(framework.stack, [play_mode])
            self.assertIs(play_mode.boy, boy)
            self.assertEqual(boy.ball_type, selection)
            before = len(game_world.world[1])
            self.key(sdl2.SDLK_SPACE)
            self.assertEqual(len(game_world.world[1]), before + (selection != 0))
            if selection:
                shot = game_world.world[1][-1]
                self.assertEqual(shot.image.w, width)
                self.assertEqual(shot.ball_type, selection)
                shots.append(shot)
        self.assertEqual([shot.ball_type for shot in shots], [1, 2])
        self.assertEqual([shot.image.w for shot in shots], [23, 43])

    def test_cancel_keeps_selected_item(self):
        self.key(sdl2.SDLK_i)
        self.key(sdl2.SDLK_2)
        for cancel in (sdl2.SDLK_ESCAPE, sdl2.SDLK_i):
            self.key(sdl2.SDLK_i)
            self.frames()
            self.key(cancel)
            self.assertEqual(framework.stack, [play_mode])
            self.assertEqual(play_mode.boy.ball_type, Ball.BIG)

    def test_menu_freezes_world_and_excludes_suspended_time(self):
        boy = play_mode.boy
        self.key(sdl2.SDLK_SPACE)
        self.frames(2)
        shot = game_world.world[1][-1]
        boy.idle_started_at = pico2d.get_time() - 4.5
        self.key(sdl2.SDLK_i)
        frozen = self.snapshot()
        # Represent six seconds spent in the menu without a slow wall-clock wait.
        boy.idle_started_at -= 6.0
        play_mode.pause_started_at -= 6.0
        self.frames(8)
        self.assertEqual(self.snapshot(), frozen)
        self.key(sdl2.SDLK_1)
        self.assertIs(play_mode.boy, boy)
        self.assertIn(shot, game_world.world[1])
        shot_x = shot.x
        self.frames()
        self.assertEqual(boy.state, 'IDLE')
        self.assertLess(pico2d.get_time() - boy.idle_started_at, 5.0)
        self.assertGreater(shot.x, shot_x)

    def test_released_direction_is_applied_after_both_overlays(self):
        for enter, leave in ((sdl2.SDLK_i, sdl2.SDLK_1),
                              (sdl2.SDLK_p, sdl2.SDLK_p)):
            self.key(sdl2.SDLK_RIGHT)
            self.frames()
            boy = play_mode.boy
            self.assertEqual(boy.state, 'RUN')
            self.key(enter)
            frozen = self.snapshot()
            self.key(sdl2.SDLK_RIGHT, sdl2.SDL_KEYUP)
            self.frames(3)
            self.assertEqual(self.snapshot(), frozen)
            self.key(leave)
            self.assertEqual(framework.stack, [play_mode])
            self.assertEqual(boy.state, 'IDLE')
            self.assertFalse(boy.pressed_keys)
            x = boy.x
            self.frames(3)
            self.assertEqual(boy.x, x)

    def test_repeated_overlay_use_does_not_duplicate_world_objects(self):
        boy = play_mode.boy
        for _ in range(3):
            self.key(sdl2.SDLK_i)
            self.frames()
            self.key(sdl2.SDLK_2)
            self.key(sdl2.SDLK_p)
            self.frames()
            self.key(sdl2.SDLK_p)
            self.assertIs(play_mode.boy, boy)
            self.assertEqual(framework.stack, [play_mode])
            self.assertEqual([len(layer) for layer in game_world.world], [1, 1, 0])
            self.assertIsNone(item_mode.font)
            self.assertIsNone(pause_mode.font)

    def test_holding_p_does_not_toggle_repeatedly(self):
        self.key(sdl2.SDLK_p)
        self.assertEqual(framework.stack, [play_mode, pause_mode])
        self.key(sdl2.SDLK_p, repeat=1)
        self.assertEqual(framework.stack, [play_mode, pause_mode])
        self.key(sdl2.SDLK_p, sdl2.SDL_KEYUP)
        self.key(sdl2.SDLK_p)
        self.assertEqual(framework.stack, [play_mode])

    def test_sleep_and_facing_direction_survive_item_selection(self):
        boy = play_mode.boy
        boy.face_dir = -1
        boy.fall_asleep()
        self.key(sdl2.SDLK_i)
        self.frames(3)
        self.key(sdl2.SDLK_2)
        self.assertEqual(boy.state, 'SLEEP')
        self.key(sdl2.SDLK_SPACE)
        self.assertEqual(boy.state, 'IDLE')
        self.assertEqual(len(game_world.world[1]), 1)
        self.key(sdl2.SDLK_SPACE)
        shot = game_world.world[1][-1]
        self.assertEqual(shot.ball_type, Ball.BIG)
        self.assertLess(shot.velocity, 0)

    def test_new_game_clears_projectiles_and_resets_selection(self):
        original_boy = play_mode.boy
        self.key(sdl2.SDLK_i)
        self.key(sdl2.SDLK_2)
        self.key(sdl2.SDLK_SPACE)
        self.key(sdl2.SDLK_ESCAPE)
        self.assertEqual(framework.stack, [title_mode])
        self.assertTrue(all(not layer for layer in game_world.world))
        self.key(sdl2.SDLK_SPACE)
        self.assertIsNot(play_mode.boy, original_boy)
        self.assertEqual(play_mode.boy.ball_type, Ball.SMALL)
        self.assertEqual([len(layer) for layer in game_world.world], [1, 1, 0])

    def test_window_close_from_item_menu_stops_framework(self):
        self.key(sdl2.SDLK_i)
        event = sdl2.SDL_Event()
        event.type = sdl2.SDL_QUIT
        self.assertEqual(sdl2.SDL_PushEvent(ctypes.byref(event)), 1)
        item_mode.handle_events()
        self.assertFalse(framework.running)


if __name__ == '__main__':
    unittest.main()
