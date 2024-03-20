import pygame as pg
from interactable import BTNOperation, Button, ButtonToggle, Input, InputOperation
from sorter import Sorter
from constants import *


def test():
    print("test!!~~`1")


def get_render_method(pos: pg.Vector2, sorter, buttons):
    font_a = pg.font.SysFont(GameValues.FONT, 20)
    font_b = pg.font.SysFont(GameValues.FONT, 30)
    font_b.underline = True

    title_text = font_a.render(Texts.SORTING_METHOD, True, (255, 255, 255))
    buttons.append(ButtonToggle(Texts.CHANGE, pg.Vector2(pos.x - 12, pos.y + 55), BTNOperation(test), text_size=15, text_margin=10))

    def render_method(screen: pg.Surface):
        method_text = font_b.render(sorter.sorting_method, True, (255, 255, 255))  # always refreshing

        screen.blit(title_text, pos)
        screen.blit(method_text, pg.Vector2(pos.x, pos.y + 30))

    return render_method


def get_buttons(game, sorter: Sorter):
    start = Button(Texts.START, pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 70), BTNOperation(test), colour=(100, 255, 100), outline=2)
    re_gen = Button(Texts.RE_GEN, pg.Vector2(GameValues.SCREEN_HEIGHT - 230, GameValues.SCREEN_HEIGHT - 70), BTNOperation(sorter.generate_items), text_size=20, outline=2, active=False)
    return [start, re_gen]


def get_inputs(game, sorter: Sorter):
    items_num = Input(Texts.ITEMS_NUM, pg.Vector2(GameValues.SCREEN_WIDTH - 340, 20),
                      InputOperation(sorter.change_item_num), int_only=True, default_val='100', max_val=GameValues.MAX_ITEMS, min_val=GameValues.MIN_ITEMS)
    frames_per_op = Input(Texts.FRAMES_OP, pg.Vector2(GameValues.SCREEN_WIDTH - 200, 20),
                          InputOperation(sorter.change_frames_per_op), int_only=True, default_val='10', max_val=GameValues.MAX_FRAMES, min_val=GameValues.MIN_FRAMES)
    margin = Input(Texts.MARGIN, pg.Vector2(GameValues.SCREEN_WIDTH - 80, 20), InputOperation(sorter.change_margin), int_only=True, default_val='30', max_val=GameValues.MAX_MARGIN, min_val=GameValues.MIN_MARGIN, active=False)
    return [items_num, frames_per_op, margin]


class Game:
    def __init__(self):
        self.running = True
        self.fps = 60
        self.clock = pg.time.Clock()
        self.keys = pg.key.get_pressed()

        self.canvas_screen = pg.Surface(pg.Vector2(GameValues.SCREEN_WIDTH, GameValues.SCREEN_HEIGHT))
        self.final_screen = pg.display.get_surface()

        self.sorter = Sorter(pg.Vector2(175, 100))
        self.buttons = get_buttons(self, self.sorter)
        self.render_method = get_render_method(pg.Vector2(10, 10), self.sorter, self.buttons)
        self.inputs = get_inputs(self, self.sorter)

    def events(self):
        for event in pg.event.get():
            # keydown input
            if event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                for inpt in self.inputs:
                    inpt.key_input(event.key)

            if event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()

            # close game
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.running = False

            # mouse
            if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
                for button in self.buttons:
                    if button.is_mouse_in_bounds():
                        button.perform_operation()
                for inpt in self.inputs:
                    inpt.mouse_down()

    def render(self):
        self.final_screen.fill(GameValues.BG_COL)
        self.canvas_screen.fill(GameValues.BG_COL)

        for button in self.buttons:
            button.render(self.canvas_screen)
        for inpt in self.inputs:
            inpt.render(self.canvas_screen)

        self.sorter.render(self.canvas_screen)
        self.render_method(self.canvas_screen)

        # final
        scaled = pg.transform.scale(self.canvas_screen, pg.Vector2(GameValues.SCREEN_WIDTH * GameValues.RES_MUL, GameValues.SCREEN_HEIGHT * GameValues.RES_MUL))
        self.final_screen.blit(scaled, pg.Vector2(0, 0))

        pg.display.flip()

    def main_loop(self):
        while self.running:
            self.events()
            self.render()

            self.clock.tick(self.fps)

            pg.display.set_caption("{} - fps: {:.2f}".format("sort stuff idk", self.clock.get_fps()))
