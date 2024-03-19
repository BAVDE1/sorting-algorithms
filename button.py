import pygame as pg
from constants import *


def get_middle(pos: int, width_1, width_2) -> int:
    return pos + ((width_1 / 2) - (width_2 / 2))


class BTNOperation:
    def __init__(self, function, *args, **kwargs):
        if not callable(function):
            raise ValueError("The given function param is not callable.")

        self.args = args
        self.kwargs = kwargs
        self.function = function

    def perform_operation(self):
        self.function(*self.args, **self.kwargs)

    def __repr__(self):
        return f"BTNOperation({self.function.__name__})"


class InputOperation:
    def __init__(self, function):
        if not callable(function):
            raise ValueError("The given function param is not callable.")
        self.function = function

    def perform_operation(self, value):
        self.function(value)

    def __repr__(self):
        return f"BTNOperation({self.function.__name__})"


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
        return (self.bounds.x < mp.x < self.bounds.x + self.bounds.width
                and self.bounds.y < mp.y < self.bounds.y + self.bounds.height)

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


class Input:
    def __init__(self, text, pos: pg.Vector2, operation: InputOperation,
                 text_size=20, text_col=(255, 255, 0), max_value_chars=3, int_only=False, margin=5,
                 default_val="", max_val=0, min_val=0):
        self.font = pg.font.SysFont('Times New Roman', text_size)
        self.display_text = self.font.render(text, True, text_col)

        self.text_col = text_col
        self.margin = margin
        self.operation = operation
        self.selected = True
        self.value = default_val

        self.max_value = max_val
        self.min_value = min_val
        self.max_value_chars = max_value_chars
        self.int_only = int_only

        self.box_bounds = pg.Rect(pos.x, text_size + pos.y + margin, (text_size * max_value_chars) * 0.8, text_size + margin)
        self.text_pos = pg.Vector2(get_middle(pos.x, self.box_bounds.width, self.display_text.get_width()), pos.y)

        self.de_select()

    def key_input(self, key):
        if self.selected:
            if key == pg.K_RETURN:
                self.de_select()
                return
            elif key == pg.K_BACKSPACE:
                self.value = self.value[:-1]
                return
            # add to value
            if len(self.value) < self.max_value_chars:
                char = pg.key.name(key)
                if self.int_only and not char.isdigit():
                    return
                self.value += char
                return
            self.de_select()

    def de_select(self):
        if self.selected:
            self.selected = False
            if self.int_only:
                self.value = str(min(self.max_value, max(self.min_value, int(self.value if self.value else 0))))
            self.operation.perform_operation(int(self.value) if self.int_only else self.value)

    def mouse_down(self):
        if self.is_mouse_in_bounds():
            self.selected = True
            return
        self.de_select()

    def render(self, screen: pg.Surface):
        pg.draw.rect(screen, (50, 50, 50), self.box_bounds)
        self.mouse_hover(screen)

        if self.selected:
            pg.draw.rect(screen, (255, 255, 255), self.box_bounds, 2)

        # text
        screen.blit(self.display_text, self.text_pos)
        value_text = self.font.render(self.value, True, self.text_col)
        screen.blit(value_text, pg.Vector2(get_middle(self.box_bounds.x, self.box_bounds.width, value_text.get_width()), self.box_bounds.y))

    def mouse_hover(self, screen: pg.Surface):
        if self.is_mouse_in_bounds():
            pg.draw.rect(screen, (100, 100, 100), self.box_bounds)

    def is_mouse_in_bounds(self):
        mp = pg.Vector2(pg.mouse.get_pos()) / GameValues.RES_MUL
        return (self.box_bounds.x < mp.x < self.box_bounds.x + self.box_bounds.width
                and self.box_bounds.y < mp.y < self.box_bounds.y + self.box_bounds.height)
