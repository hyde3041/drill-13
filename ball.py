from pathlib import Path

from pico2d import get_canvas_width, load_image

import game_world


class Ball:
    SMALL = 1
    BIG = 2
    image_files = {SMALL: 'ball21x21.png', BIG: 'ball41x41.png'}
    images = {}

    def __init__(self, x, y, velocity, ball_type=SMALL):
        if ball_type not in self.image_files:
            raise ValueError('Ball type must be SMALL (1) or BIG (2)')
        if ball_type not in Ball.images:
            Ball.images[ball_type] = load_image(
                str(Path(__file__).with_name(self.image_files[ball_type])))
        self.ball_type = ball_type
        self.image = Ball.images[ball_type]
        self.x, self.y = x, y
        self.velocity = velocity

    def update(self):
        self.x += self.velocity
        if self.x < 0 or self.x > get_canvas_width():
            game_world.remove_object(self)

    def draw(self):
        self.image.draw(self.x, self.y)
