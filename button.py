import pygame as pg


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
    def __init__(self, display_text, pos: pg.Vector2, operation: BTNOperation, image=None, text_size: int = 30, override_size: tuple | None = None):
        self.font = pg.font.SysFont('Times New Roman', text_size)

        self.pos = pos
        self.operation = operation

        self.display_text = self.font.render(display_text, True, (255, 255, 0))
        self.image = image

        self.bounds = []
        if not override_size:
            self.bounds = [(self.pos.x, self.pos.x + self.display_text.get_width()),
                           (self.pos.y, self.pos.y + self.display_text.get_height() + (0 if not self.image else self.image.get_height()))]
        else:
            self.bounds = [(self.pos.x, self.pos.x + override_size[0]),
                           (self.pos.y, self.pos.y + override_size[1])]

    def render(self, screen: pg.Surface):
        self.mouse_hover(screen)

        # render text and image
        screen.blit(self.display_text, self.pos)
        if self.image:
            screen.blit(self.image, (self.pos.x, self.pos.y + self.display_text.get_height()))

    def get_operation(self):
        if self.is_mouse_in_bounds():
            return self.operation

    def mouse_hover(self, screen: pg.Surface):
        if self.is_mouse_in_bounds():
            pg.draw.rect(screen, (50, 50, 50), pg.rect.Rect(self.bounds[0][0], self.bounds[1][0],
                                                                 self.bounds[0][1] - self.bounds[0][0],
                                                                 self.bounds[1][1] - self.bounds[1][0]))

    def is_mouse_in_bounds(self):
        m_x = pg.mouse.get_pos()[0]
        m_y = pg.mouse.get_pos()[1]
        return self.bounds[0][0] < m_x < self.bounds[0][1] and self.bounds[1][0] < m_y < self.bounds[1][1]

    def perform_operation(self):
        self.operation.perform_operation()


class ButtonOutlined(Button):
    def mouse_hover(self):
        if self.is_mouse_in_bounds():
            pg.draw.rect(self.screen, (50, 50, 50), pg.rect.Rect(self.bounds[0][0], self.bounds[1][0],
                                                                 self.bounds[0][1] - self.bounds[0][0],
                                                                 self.bounds[1][1] - self.bounds[1][0]), 2)
