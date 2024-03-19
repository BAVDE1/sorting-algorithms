import pygame as pg
from constants import *


class BTNOperation:
    def __init__(self, btn_type: str, function, *args, **kwargs):
        self.type = btn_type

        if not callable(function):
            raise ValueError("The given function param is not callable.")

        self.args = args
        self.kwargs = kwargs
        self.function = function

    def perform_operation(self):
        self.function(*self.args, **self.kwargs)

    def __repr__(self):
        return f"BTNOperation({self.type}, {self.function.__name__})"


class Button:
    def __init__(self, text, pos: pg.Vector2, operation: BTNOperation,
                 image=None, text_size=30, text_col=(255, 255, 0), text_margin=5,
                 override_size: pg.Vector2 | None = None, outline=0):
        self.font = pg.font.SysFont('Times New Roman', text_size)

        self.margin = text_margin
        self.operation = operation

        self.display_text = self.font.render(text, True, text_col)
        self.image = image
        self.outline = outline
        self.outline_col = text_col

        self.bounds: pg.Rect = pg.Rect(pos.x + self.margin, pos.y + self.margin, self.display_text.get_width() + self.margin, self.display_text.get_height() + self.margin)
        if override_size:
            self.bounds.size = override_size

        self.text_pos = pg.Vector2(self.bounds.topleft) + pg.Vector2(self.margin * .5)

    def render(self, screen: pg.Surface):
        self.mouse_hover(screen)

        # outline
        if self.outline:
            pg.draw.rect(screen, self.outline_col, self.bounds, self.outline)

        screen.blit(self.display_text, self.text_pos)
        if self.image:
            screen.blit(self.image, (self.bounds.x, self.bounds.y + self.display_text.get_height()))

    def get_operation(self):
        if self.is_mouse_in_bounds():
            return self.operation

    def mouse_hover(self, screen: pg.Surface):
        if self.is_mouse_in_bounds():
            pg.draw.rect(screen, (50, 50, 50), self.bounds)

    def is_mouse_in_bounds(self):
        mp = pg.Vector2(pg.mouse.get_pos()) / GameValues.RES_MUL
        return self.bounds.x < mp.x < self.bounds.width and self.bounds.y < mp.y < self.bounds.height

    def perform_operation(self):
        if self.is_mouse_in_bounds():
            self.operation.perform_operation()


class ButtonToggle(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toggle_col = (255, 255, 255)
        self.toggled = False

    def perform_operation(self):
        super().perform_operation()
        self.toggled = not self.toggled

    def render(self, screen: pg.Surface):
        super().render(screen)
        if self.toggled:
            pg.draw.rect(screen, self.toggle_col, self.bounds, 2)
