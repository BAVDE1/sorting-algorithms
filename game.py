import pygame as pg
from button import BTNOperation, Button, ButtonToggle, Input, InputOperation
from sorter import Sorter
from constants import *


def test(a):
    print(a)


def get_buttons(game, sorter: Sorter):
    start = Button("> Start <", pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 70), BTNOperation(test), text_col=(100, 255, 100), outline=2)
    re_gen = Button("Re-gen", pg.Vector2(GameValues.SCREEN_HEIGHT - 230, GameValues.SCREEN_HEIGHT - 70), BTNOperation(sorter.generate_items), text_size=20, outline=2)
    change_sort = Button("change", pg.Vector2(0, 0), BTNOperation(test), text_size=15)
    return [start, re_gen, change_sort]


def get_inputs(game, sorter: Sorter):
    items_num = Input("Num of items", pg.Vector2(GameValues.SCREEN_WIDTH - 240, 20),
                      InputOperation(sorter.change_item_num), int_only=True, default_val='100', max_val=GameValues.MAX_ITEMS, min_val=GameValues.MIN_ITEMS)
    frames_per_op = Input("Frames / Op", pg.Vector2(GameValues.SCREEN_WIDTH - 100, 20),
                          InputOperation(sorter.change_frames_per_op), int_only=True, default_val='10', max_val=GameValues.MAX_FRAMES, min_val=GameValues.MIN_FRAMES)
    return [items_num, frames_per_op]


def get_sorter() -> Sorter:
    s = Sorter(pg.Vector2(175, 100))
    return s


class Game:
    def __init__(self):
        self.running = True
        self.fps = 60
        self.clock = pg.time.Clock()
        self.keys = pg.key.get_pressed()

        self.canvas_screen = pg.Surface(pg.Vector2(GameValues.SCREEN_WIDTH, GameValues.SCREEN_HEIGHT))
        self.final_screen = pg.display.get_surface()

        self.sorter = get_sorter()
        self.buttons = get_buttons(self, self.sorter)
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
