import pygame as pg
from button import BTNOperation, Button, ButtonToggle
from sorter import Sorter
from constants import *


def test():
    print("clicked")


def get_buttons(game, sorter: Sorter):
    start_btn = Button("> Start <", pg.Vector2(GameValues.SCREEN_WIDTH - 140, GameValues.SCREEN_HEIGHT - 70), BTNOperation("a", test), text_col=(100, 255, 100), outline=2)
    return [start_btn]


def get_sorter() -> Sorter:
    s = Sorter(pg.Vector2(225, 150))
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

    def events(self):
        for event in pg.event.get():
            # keydown input
            if event.type in (pg.KEYDOWN, pg.KEYUP):
                self.keys = pg.key.get_pressed()

            # close game
            if event.type == pg.QUIT or self.keys[pg.K_ESCAPE]:
                self.running = False

            # mouse
            if event.type == pg.MOUSEBUTTONDOWN and pg.mouse.get_pressed()[0]:
                for button in self.buttons:
                    if button.is_mouse_in_bounds():
                        button.perform_operation()

    def render(self):
        self.final_screen.fill(GameValues.BG_COL)
        self.canvas_screen.fill(GameValues.BG_COL)

        for button in self.buttons:
            button.render(self.canvas_screen)

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
