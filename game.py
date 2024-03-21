import pygame as pg
from interactable import BTNOperation, Button, ButtonToggle, Input, InputOperation, Collection
from sorter import Sorter
from constants import *


def test():
    print("test!!~~`1")


def get_render_method(pos: pg.Vector2, sorter, buttons, collection):
    font_a = pg.font.SysFont(GameValues.FONT, 20)
    font_b = pg.font.SysFont(GameValues.FONT, 30)
    font_b.underline = True

    title_text = font_a.render(Texts.SORTING_METHOD, True, (255, 255, 255))
    buttons.append(ButtonToggle(Texts.CHANGE, pg.Vector2(pos.x - 12, pos.y + 60), BTNOperation(collection=collection), text_size=15, text_margin=8))

    def render_method(screen: pg.Surface):
        method_text = font_b.render(sorter.sorting_method, True, (255, 255, 255))  # always refreshing

        screen.blit(title_text, pos)
        screen.blit(method_text, pg.Vector2(pos.x, pos.y + 30))

    return render_method


def get_buttons(game, sorter: Sorter):
    start = Button(Texts.START, pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 70),
                   BTNOperation(game.start_sorting), colour=(100, 255, 100), outline=2)
    stop = Button(Texts.STOP, pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 70),
                  BTNOperation(sorter.stop_sorting), colour=(255, 100, 100), outline=2, hidden=True)
    re_gen = Button(Texts.RE_GEN, pg.Vector2(GameValues.SCREEN_HEIGHT - 230, GameValues.SCREEN_HEIGHT - 70), BTNOperation(sorter.generate_items), text_size=20, outline=2)
    return [start, stop, re_gen]


def get_inputs(game, sorter: Sorter):
    items_num = Input(Texts.ITEMS_NUM, pg.Vector2(GameValues.SCREEN_WIDTH - 340, 20),
                      InputOperation(function=sorter.change_item_num), int_only=True, default_val='8', max_val=GameValues.MAX_ITEMS, min_val=GameValues.MIN_ITEMS)
    frames_per_op = Input(Texts.FRAMES_OP, pg.Vector2(GameValues.SCREEN_WIDTH - 200, 20),
                          InputOperation(function=sorter.change_frames_per_op), int_only=True, default_val='20', max_val=GameValues.MAX_FRAMES, min_val=GameValues.MIN_FRAMES)
    margin = Input(Texts.MARGIN, pg.Vector2(GameValues.SCREEN_WIDTH - 80, 20),
                   InputOperation(function=sorter.change_margin), int_only=True, default_val='30', max_val=GameValues.MAX_MARGIN, min_val=GameValues.MIN_MARGIN)
    return [items_num, frames_per_op, margin]


def get_collections(game, sorter: Sorter):
    method_collection = Collection(pg.Vector2(6, 110), pg.Vector2(160, 590))
    method_collection.add_buttons([
        Button(SortingMethods.BUBBLE, pg.Vector2(5, 5), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.BUBBLE), colour=(255, 255, 255), text_size=20),
        Button(SortingMethods.MERGE, pg.Vector2(5, 35), BTNOperation(function=sorter.change_sorting_method, method=SortingMethods.MERGE), colour=(255, 255, 255), text_size=20)
    ])
    return [method_collection]


class Game:
    def __init__(self):
        self.running = True
        self.fps = 120
        self.clock = pg.time.Clock()
        self.keys = pg.key.get_pressed()

        self.canvas_screen = pg.Surface(pg.Vector2(GameValues.SCREEN_WIDTH, GameValues.SCREEN_HEIGHT))
        self.final_screen = pg.display.get_surface()

        self.sorter = Sorter(self, pg.Vector2(175, 100))
        self.collections = get_collections(self, self.sorter)
        self.buttons = get_buttons(self, self.sorter)
        self.inputs = get_inputs(self, self.sorter)
        self.render_method = get_render_method(pg.Vector2(10, 10), self.sorter, self.buttons, self.collections[0])

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
                for coll in self.collections:
                    coll.mouse_down()
                for button in self.buttons:
                    if button.should_perform_op():
                        button.perform_operation()
                        return
                for inpt in self.inputs:
                    inpt.mouse_down()

    def update(self):
        self.sorter.update()

    def start_sorting(self):
        if not self.sorter.completed:
            for inpt in self.inputs:
                inpt.active = False
            for i, btn in enumerate(self.buttons):
                btn.active = False if i != 1 else True

            self.buttons[0].hidden = True
            self.buttons[1].hidden = False
            self.sorter.start_sorting()

    def stop_sorting(self):
        for inpt in self.inputs:
            inpt.active = True
        for btn in self.buttons:
            btn.active = True

        self.buttons[0].hidden = False
        self.buttons[1].hidden = True

    def render(self):
        self.final_screen.fill(GameValues.BG_COL)
        self.canvas_screen.fill(GameValues.BG_COL)

        for coll in self.collections:
            coll.render(self.canvas_screen)
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
