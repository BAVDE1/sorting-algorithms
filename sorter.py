import math

import pygame as pg
import random
from constants import *


class Sorter:
    def __init__(self, game, pos: pg.Vector2):
        self.game = game
        self.pos = pos
        self.size = pg.Vector2(600, 600)
        self.margin = 50
        self.outline_rect = pg.Rect(0, 0, self.size.x, self.size.y)
        self.sorter_screen = pg.Surface(self.size)

        self.item_num = 1
        self.items = []

        self.sorting_method = SortingMethods.BUBBLE
        self.sorter: MethodSorter = self.get_sorter()

        self.started = False
        self.completed = False
        self.frames_per_op = 0
        self.frames_since_op = 0
        self.frame_num = 0

        # init generation
        self.generate_items()

    def get_sorter(self):
        methods_dic = {
            SortingMethods.BUBBLE: BubbleSorter
        }
        return methods_dic[self.sorting_method](self)

    def generate_items(self):
        if not self.started:
            self.items = [i for i in range(1, self.item_num + 1)]
            random.shuffle(self.items)
            self.sorter = self.get_sorter()
            self.completed = False

    def change_item_num(self, new_num):
        self.item_num = new_num
        self.generate_items()

    def change_frames_per_op(self, new_val):
        self.frames_per_op = new_val

    def change_margin(self, new_val):
        self.margin = new_val

    def change_sorting_method(self, method: SortingMethods):
        if self.started:
            self.sorting_method = method
            self.sorter = self.get_sorter()

    def start_sorting(self):
        if not self.started and not self.completed:
            print('start')
            self.started = True
            self.paused = False
            self.completed = False
            self.frames_since_op = self.frames_per_op
            self.frame_num = 0

    def stop_sorting(self):
        if self.started and not self.completed:
            self.started = False
            self.game.stop_sorting()

    def complete_sorting(self):
        if self.started and not self.completed:
            self.started = False
            self.completed = True
            self.game.stop_sorting()
            print("finished!")

    def is_sorted(self):
        s = True
        for i, item in enumerate(self.items):
            if not i + 1 == len(self.items):
                s = s if item + 1 == self.items[i + 1] else False
        return s

    def update(self):
        if self.started and not self.completed and not self.paused:
            self.frame_num += 1
            self.frames_since_op += 1
            if self.frames_since_op >= self.frames_per_op:
                self.sorter.advance()
                self.frames_since_op = 0

    def render(self, screen: pg.Surface):
        self.sorter_screen.fill(GameValues.BG_COL)

        pg.draw.rect(self.sorter_screen, (255, 255, 255), self.outline_rect, 1)

        items_width = self.size.x - (self.margin * 2)
        bar_width = items_width / len(self.items)
        if bar_width >= 1:
            for i, item in enumerate(self.items):
                x = self.margin + (i * bar_width)
                y = (self.size.y - self.margin) - (bar_width * item)

                def get_col():
                    if self.completed or i in self.sorter.get_completed_items():
                        return 100, 255, 100
                    if i in self.sorter.get_looking_at_items():
                        return 255, 100, 100
                    return 255, 255, 255

                pg.draw.rect(self.sorter_screen, get_col(), pg.Rect(x, y, math.ceil(bar_width), math.ceil(bar_width * item)))

        # final
        screen.blit(self.sorter_screen, self.pos)


class MethodSorter:
    """ (theoretical) abstract class """
    def advance(self):
        pass

    def get_looking_at_items(self) -> list[int]:
        pass

    def get_completed_items(self) -> list[int]:
        pass


class BubbleSorter(MethodSorter):
    def __init__(self, sorter: Sorter):
        self.sorter = sorter

        self.looking_at_item = 0
        self.completed_items = 0

    def advance(self):
        total_items = self.sorter.item_num

        if self.looking_at_item + 1 < total_items and self.looking_at_item < (total_items - self.completed_items):
            a, b = self.looking_at_item, self.looking_at_item + 1
            item_a, item_b = self.sorter.items[a], self.sorter.items[b]
            if item_a > item_b:
                self.sorter.items[a] = item_b
                self.sorter.items[b] = item_a
            self.looking_at_item += 1
            return

        self.completed_items += 1
        self.looking_at_item = 0
        if self.completed_items == total_items or self.sorter.is_sorted():
            self.sorter.complete_sorting()

    def get_looking_at_items(self) -> list[int]:
        return [self.looking_at_item]

    def get_completed_items(self) -> list[int]:
        li = []
        for i, item in enumerate(self.sorter.items):
            if i + 1 > (self.sorter.item_num - self.completed_items):
                li.append(i)
        return li
