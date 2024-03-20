import math

import pygame as pg
from constants import *


class BTNOperation:
    def __init__(self, function=None, collection=None, *args, **kwargs):
        if not function and not collection:
            raise ValueError("No function of collection given")
        if function and not callable(function):
            raise ValueError("The given function param is not callable.")
        if collection and not isinstance(collection, Collection):
            raise ValueError("The given collection is not of instance Collection")

        self.args = args
        self.kwargs = kwargs
        self.function = function
        self.collection = collection

    def perform_operation(self):
        if self.function:
            self.function(*self.args, **self.kwargs)
        if self.collection:
            self.collection.toggle()

    def __repr__(self):
        return f"BTNOperation( {self.function.__name__ if self.function else self.collection}({self.args}, {self.kwargs}) )"


class InputOperation:
    def __init__(self, function):
        if not callable(function):
            raise ValueError("The given function param is not callable.")
        self.function = function

    def perform_operation(self, value):
        self.function(value)

    def __repr__(self):
        return f"InputOperation({self.function.__name__})"


class Collection:
    def __init__(self, pos: pg.Vector2, size: pg.Vector2, buttons=None, toggled=False):
        if buttons is None:
            buttons = []
        self.buttons = [button for button in buttons if isinstance(button, Button)]

        self.pos = pos
        self.size = size
        self.coll_screen = pg.Surface(self.size)

        self.toggled = toggled

    def add_buttons(self, new_buttons: list):
        for new_btn in new_buttons:
            if isinstance(new_btn, Button):
                new_btn.hidden = not self.toggled
                new_btn.change_mouse_offset(self.pos)
                self.buttons.append(new_btn)

    def remove_button(self, index):
        """ -1 to remove all buttons """
        if index in self.buttons:
            self.buttons.pop(index)
        if index == -1:
            self.buttons.clear()

    def toggle(self):
        self.toggled = not self.toggled
        for button in self.buttons:
            button.hidden = not self.toggled

    def mouse_down(self):
        for button in self.buttons:
            button.perform_operation()

    def render(self, screen: pg.Surface):
        self.coll_screen.fill(GameValues.BG_COL)
        if self.toggled:
            pg.draw.rect(self.coll_screen, (255, 255, 255), pg.Rect(0, 0, self.size.x, self.size.y), 2)
            for button in self.buttons:
                button.render(self.coll_screen)
        screen.blit(self.coll_screen, self.pos)

    def __repr__(self):
        return f"Collection({self.pos}, {self.size}, {self.toggled}, {len(self.buttons)})"


class Button:
    def __init__(self, text, pos: pg.Vector2, operation: BTNOperation,
                 text_size=30, colour=(255, 255, 0), text_margin=5,
                 override_size: pg.Vector2 | None = None, outline=0,
                 hidden=False, active=True):
        self.font = pg.font.SysFont(GameValues.FONT, text_size)

        self.margin = text_margin
        self.operation = operation
        self.hidden = hidden
        self.active = active

        self.text = text
        self.colour: pg.Color = pg.Color(colour)
        self.outline = outline

        display_text = self.font.render(text, True, colour)
        self.size = pg.Vector2(display_text.get_width() + self.margin, display_text.get_height() + self.margin)

        self.pos = pos
        self.bounds: pg.Rect = pg.Rect(pos.x + self.margin, pos.y + self.margin, self.size.x, self.size.y)
        if override_size:
            self.bounds.size = override_size
            self.size = pg.Vector2(self.bounds.size)
        self.mouse_offset = pg.Vector2(0, 0)

        self.text_pos = pg.Vector2(self.bounds.topleft) + pg.Vector2(self.margin * .5)

    def change_pos(self, new_pos: pg.Vector2):
        self.pos = new_pos
        self.bounds = pg.Rect(new_pos.x + self.margin, new_pos.y + self.margin, self.size.x, self.size.y)
        print(self.bounds)
        self.text_pos = pg.Vector2(self.bounds.topleft) + pg.Vector2(self.margin * .5)
        print(self.text_pos)

    def change_mouse_offset(self, new_off: pg.Vector2):
        self.mouse_offset = new_off

    def get_col(self, given_col=None):
        col = pg.Color(given_col if given_col else self.colour)
        if not self.active:
            m = 0.3
            col.update(math.ceil(col.r * m), math.ceil(col.g * m), math.ceil(col.b * m))
        return col

    def render(self, screen: pg.Surface):
        if not self.hidden:
            self.mouse_hover(screen)

            # outline
            if self.outline:
                pg.draw.rect(screen, self.get_col(), self.bounds, self.outline)

            screen.blit(self.font.render(self.text, True, self.get_col()), self.text_pos)

    def get_mouse_bounds(self):
        return pg.Rect(self.bounds.topleft + self.mouse_offset, self.bounds.size)

    def get_operation(self):
        if self.is_mouse_in_bounds():
            return self.operation

    def mouse_hover(self, screen: pg.Surface):
        if self.is_mouse_in_bounds():
            pg.draw.rect(screen, self.get_col((50, 50, 50)), self.bounds)

    def is_mouse_in_bounds(self):
        mp = pg.Vector2(pg.mouse.get_pos()) / GameValues.RES_MUL
        bounds = self.get_mouse_bounds()
        return (bounds.x < mp.x < bounds.x + bounds.width
                and bounds.y < mp.y < bounds.y + bounds.height)

    def perform_operation(self):
        if self.is_mouse_in_bounds() and not self.hidden and self.active:
            self.operation.perform_operation()


class ButtonToggle(Button):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toggle_col = (255, 255, 255)
        self.toggled = False

    def perform_operation(self):
        super().perform_operation()
        if self.is_mouse_in_bounds():
            self.toggled = not self.toggled

    def render(self, screen: pg.Surface):
        super().render(screen)
        if self.toggled:
            pg.draw.rect(screen, self.toggle_col, self.bounds, 1)


class Input:
    def __init__(self, text, pos: pg.Vector2, operation: InputOperation,
                 text_size=20, text_col=(255, 255, 0), max_value_chars=3, int_only=False, margin=5,
                 default_val="", max_val=0, min_val=0, hidden=False, active=True):
        self.font = pg.font.SysFont(GameValues.FONT, text_size)

        self.text = text
        self.colour: pg.Color = pg.Color(text_col)
        self.margin = margin
        self.operation = operation
        self.hidden = hidden
        self.active = active

        self.selected = True
        self.value = default_val

        self.max_value = max_val
        self.min_value = min_val
        self.max_value_chars = max_value_chars
        self.int_only = int_only

        self.box_bounds = pg.Rect(pos.x, text_size + pos.y + margin, (text_size * max_value_chars) * 0.8, text_size + margin)
        display_text = self.font.render(text, True, text_col)
        self.text_pos = pg.Vector2(get_middle(pos.x, self.box_bounds.width, display_text.get_width()), pos.y)

        self.de_select()  # load defaults

    def key_input(self, key):
        if self.selected and not self.hidden and self.active:
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

    def get_col(self, given_col=None):
        col = pg.Color(given_col if given_col else self.colour)
        if not self.active:
            m = 0.3
            col.update(math.ceil(col.r * m), math.ceil(col.g * m), math.ceil(col.b * m))
        return col

    def de_select(self):
        if self.selected:
            self.selected = False
            if self.int_only:
                self.value = str(min(self.max_value, max(self.min_value, int(self.value if self.value else 0))))
            self.operation.perform_operation(int(self.value) if self.int_only else self.value)

    def mouse_down(self):
        if self.is_mouse_in_bounds() and not self.hidden and self.active:
            self.selected = True
            return
        self.de_select()

    def render(self, screen: pg.Surface):
        if not self.hidden:
            pg.draw.rect(screen, self.get_col((50, 50, 50)), self.box_bounds)
            self.mouse_hover(screen)

            if self.selected:
                pg.draw.rect(screen, (255, 255, 255), self.box_bounds, 2)

            # text
            screen.blit(self.font.render(self.text, True, self.get_col()), self.text_pos)
            value_text = self.font.render(self.value, True, self.get_col())
            screen.blit(value_text, pg.Vector2(get_middle(self.box_bounds.x, self.box_bounds.width, value_text.get_width()), self.box_bounds.y))

    def mouse_hover(self, screen: pg.Surface):
        if self.is_mouse_in_bounds():
            pg.draw.rect(screen, self.get_col((100, 100, 100)), self.box_bounds)

    def is_mouse_in_bounds(self):
        mp = pg.Vector2(pg.mouse.get_pos()) / GameValues.RES_MUL
        return (self.box_bounds.x < mp.x < self.box_bounds.x + self.box_bounds.width
                and self.box_bounds.y < mp.y < self.box_bounds.y + self.box_bounds.height)
