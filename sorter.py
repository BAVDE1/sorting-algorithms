import pygame as pg
import random
from constants import *


class Sorter:
    def __init__(self, pos: pg.Vector2):
        self.pos = pos
        self.size = pg.Vector2(550, 550)
        self.margin = 50
        self.outline_rect = pg.Rect(0, 0, self.size.x, self.size.y)
        self.sorter_screen = pg.Surface(self.size)

        self.item_num = 50
        self.items = []

        self.generate_items()

    def generate_items(self):
        self.items = [i for i in range(1, self.item_num + 1)]
        random.shuffle(self.items)
        print(self.items)

    def change_item_num(self, new_num):
        self.item_num = new_num
        self.generate_items()

    def render(self, screen: pg.Surface):
        self.sorter_screen.fill(GameValues.BG_COL)

        pg.draw.rect(self.sorter_screen, (255, 255, 255), self.outline_rect, 1)

        items_width = (self.size.x - (self.margin * 2))
        bar_width = round(items_width / len(self.items), 4)
        if bar_width >= 1:
            for i, item in enumerate(self.items):
                x = self.margin + (i * bar_width)
                y = (self.size.y - self.margin) - (bar_width * item)
                pg.draw.rect(self.sorter_screen, (255, 0, 0), pg.Rect(x, y, bar_width, bar_width * item))

        # final
        screen.blit(self.sorter_screen, self.pos)