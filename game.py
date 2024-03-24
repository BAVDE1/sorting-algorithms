from pydub.generators import Sine
from pydub.playback import play
import pygame as pg
from interactable import BTNOperation, Button, ButtonToggle, Input, InputOperation, Collection
from sorter import Sorter
from constants import *


def get_render_method(pos: pg.Vector2, sorter, buttons, collection):
    font_a = pg.font.SysFont(GameValues.FONT, 20)
    font_b = pg.font.SysFont(GameValues.FONT, 30)
    font_b.underline = True

    title_text = font_a.render(Texts.SORTING_METHOD, True, (255, 255, 255))
    buttons.append(ButtonToggle(Texts.CHANGE, pg.Vector2(pos.x - 12, pos.y + 60), BTNOperation(collection=collection), text_size=15, text_margin=8))

    def render_method(screen: pg.Surface):
        method_text = font_b.render(sorter.sorting_method + " " + Texts.SORT, True, (255, 255, 255))  # always refreshing

        screen.blit(title_text, pos)
        screen.blit(method_text, pg.Vector2(pos.x, pos.y + 30))

    return render_method


def get_buttons(game, sorter: Sorter):
    start = Button(Texts.START, pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 80),
                   BTNOperation(game.start_sorting), colour=(100, 255, 100), outline=2)
    stop = Button(Texts.STOP, pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 80),
                  BTNOperation(sorter.stop_sorting), colour=(255, 100, 100), outline=2, hidden=True)
    re_gen = Button(Texts.RE_GEN, pg.Vector2(GameValues.SCREEN_HEIGHT - 230, GameValues.SCREEN_HEIGHT - 80), BTNOperation(sorter.generate_items), text_size=20, outline=2)
    return [start, stop, re_gen]


def get_inputs(game, sorter: Sorter):
    items_num = Input(Texts.ITEMS_NUM, pg.Vector2(GameValues.SCREEN_WIDTH - 340, 20),
                      InputOperation(function=sorter.change_item_num), int_only=True, default_val='20', max_val=GameValues.MAX_ITEMS, min_val=GameValues.MIN_ITEMS, validator=sorter.validator)
    frames_per_op = Input(Texts.FRAMES_OP, pg.Vector2(GameValues.SCREEN_WIDTH - 200, 20),
                          InputOperation(function=sorter.change_frames_per_op), int_only=True, default_val='10', max_val=GameValues.MAX_FRAMES, min_val=GameValues.MIN_FRAMES)
    margin = Input(Texts.MARGIN, pg.Vector2(GameValues.SCREEN_WIDTH - 80, 20),
                   InputOperation(function=sorter.change_margin), int_only=True, default_val='30', max_val=GameValues.MAX_MARGIN, min_val=GameValues.MIN_MARGIN)
    return [items_num, frames_per_op, margin]


def get_collection(game, sorter: Sorter) -> Collection:
    size = 20
    col = (255, 255, 255)
    method_collection = Collection(pg.Vector2(6, 110), pg.Vector2(160, 590))
    method_collection.add_buttons([
        Button(SortingMethods.BUBBLE, pg.Vector2(5, 5), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.BUBBLE), colour=col, text_size=size),
        Button(SortingMethods.COMB, pg.Vector2(5, 35), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.COMB), colour=col, text_size=size),
        Button(SortingMethods.INSERTION, pg.Vector2(5, 65), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.INSERTION), colour=col, text_size=size),
        Button(SortingMethods.SHELL, pg.Vector2(5, 95), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.SHELL), colour=col, text_size=size),
        Button(SortingMethods.COCKTAIL, pg.Vector2(5, 125), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.COCKTAIL), colour=col, text_size=size),
        Button(SortingMethods.MERGE, pg.Vector2(5, 155), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.MERGE), colour=col, text_size=size),
        Button(SortingMethods.SIMPLE_QUICK, pg.Vector2(5, 185), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.SIMPLE_QUICK), colour=col, text_size=size),
        Button(SortingMethods.HEAP, pg.Vector2(5, 215), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.HEAP), colour=col, text_size=size),
        Button(SortingMethods.RADIX, pg.Vector2(5, 275), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.RADIX), colour=col, text_size=size)
    ])
    return method_collection


class Game:
    def __init__(self):
        self.running = True
        self.fps = 120
        self.clock = pg.time.Clock()
        self.keys = pg.key.get_pressed()

        self.canvas_screen = pg.Surface(pg.Vector2(GameValues.SCREEN_WIDTH, GameValues.SCREEN_HEIGHT))
        self.final_screen = pg.display.get_surface()

        self.sorter = Sorter(self, pg.Vector2(175, 100))
        self.collection = get_collection(self, self.sorter)
        self.buttons = get_buttons(self, self.sorter)
        self.inputs = get_inputs(self, self.sorter)
        self.render_method = get_render_method(pg.Vector2(10, 10), self.sorter, self.buttons, self.collection)

    def events(self):
        for event in pg.event.get():
            # keydown input
            if event.type == pg.KEYDOWN:
                self.keys = pg.key.get_pressed()
                should_start = True
                for inpt in self.inputs:
                    should_start = should_start if not inpt.selected else False
                    inpt.key_input(event.key)

                # start sorting
                if should_start and not self.sorter.started and event.key == pg.K_RETURN:
                    if self.sorter.completed:
                        self.sorter.generate_items()
                    self.start_sorting()
                elif should_start and self.sorter.started:
                    self.sorter.stop_sorting()

            if event.type == pg.KEYUP:
                self.keys = pg.key.get_pressed()

            # close game
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.running = False

            # mouse
            if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
                self.collection.mouse_down()
                for inpt in self.inputs:
                    inpt.mouse_down()
                for button in self.buttons:
                    if button.should_perform_op():
                        button.perform_operation()
                        return

    def update(self):
        self.sorter.update()

    def start_sorting(self):
        if not self.sorter.completed:
            self.collection.toggle_active(False)
            for inpt in self.inputs:
                inpt.set_active(False)
            for i, btn in enumerate(self.buttons):
                btn.set_active(i == 1)

            self.buttons[0].set_hidden(True)
            self.buttons[1].set_hidden(False)
            self.sorter.start_sorting()

    def stop_sorting(self):
        self.collection.toggle_active(True)
        for inpt in self.inputs:
            inpt.set_active(True)
        for btn in self.buttons:
            btn.set_active(True)

        self.buttons[0].set_hidden(False)
        self.buttons[1].set_hidden(True)

    def change_item_num_input(self, value):
        self.inputs[0].change_value(value)

    def render(self):
        self.final_screen.fill(GameValues.BG_COL)
        self.canvas_screen.fill(GameValues.BG_COL)

        self.collection.render(self.canvas_screen)
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
            self.update()
            self.render()

            self.clock.tick(self.fps)

            pg.display.set_caption("{} - fps: {:.2f}".format("sort stuff idk", self.clock.get_fps()))
