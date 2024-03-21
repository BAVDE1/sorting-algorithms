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
        self.font = pg.font.SysFont(GameValues.FONT, 20)

        self.item_num = 1
        self.items = []

        self.sorting_method = SortingMethods.MERGE
        self.sorter: MethodSorter = self.get_sorter()

        self.started = False
        self.completed = False
        self.frames_per_op = 0
        self.frames_since_op = 0
        self.frame_num = 0
        self.operation_num = 0

        # init generation
        self.generate_items()

    def get_sorter(self):
        methods_dic = {
            SortingMethods.BUBBLE: BubbleSorter,
            SortingMethods.MERGE: MergeSort
        }
        if self.sorting_method not in methods_dic:
            raise ValueError(f"method {self.sorting_method} is not registered. look at Sorter.get_sorter()")
        return methods_dic[self.sorting_method](self)

    def generate_items(self):
        if not self.started:
            self.items = [i for i in range(1, self.item_num + 1)]
            random.shuffle(self.items)
            self.sorter = self.get_sorter()
            self.completed = False
            self.started = False
            self.frame_num = 0
            self.operation_num = 0

    def validator(self, value) -> str:
        return self.sorter.validator(value)

    def change_item_num(self, new_num):
        self.item_num = new_num
        self.generate_items()

    def change_frames_per_op(self, new_val):
        self.frames_per_op = new_val

    def change_margin(self, new_val):
        self.margin = new_val

    def change_sorting_method(self, method: SortingMethods):
        if not self.started:
            self.sorting_method = method
            self.sorter = self.get_sorter()

            self.item_num = int(self.validator(self.item_num))
            self.generate_items()
            self.game.change_item_num_input(self.item_num)

    def start_sorting(self):
        if not self.completed:
            self.started = True
            self.completed = False
            if (not self.started and self.frame_num != 0) or self.completed:
                self.frames_since_op = self.frames_per_op
                self.frame_num = 0
                self.operation_num = 0

    def stop_sorting(self):
        if self.started and not self.completed:
            self.started = False
            self.game.stop_sorting()

    def complete_sorting(self):
        if self.started and not self.completed:
            self.started = False
            self.completed = True
            self.game.stop_sorting()

    def is_sorted(self, li=None):
        li = li if li is not None else self.items

        if len(li) != self.item_num:
            return False

        s = True
        for i, item in enumerate(li):
            if not i + 1 == len(li):
                s = s if item + 1 == li[i + 1] else False
        return s

    def update(self):
        if self.started and not self.completed:
            self.frame_num += 1
            self.frames_since_op += 1
            if self.frames_since_op >= self.frames_per_op:
                self.sorter.advance()
                self.frames_since_op = 0
                self.operation_num += 1

    def swap_items(self, a, b):
        item_a, item_b = self.items[a], self.items[b]
        self.items[a] = item_b
        self.items[b] = item_a

    def render_text(self, screen: pg.Surface):
        col = (100, 100, 100)
        frames = self.font.render(f"frames: {self.frame_num}", False, col)
        since_op = self.font.render(f"since last op: {self.frames_since_op}", False, col)
        operations = self.font.render(f"operations: {self.operation_num}", False, col)
        srted = self.font.render(f"sorted {len(self.sorter.get_completed_items())}/{self.item_num}", False, col)

        screen.blit(frames, pg.Vector2(10, self.sorter_screen.get_height() - 25))
        screen.blit(operations, pg.Vector2(150, self.sorter_screen.get_height() - 25))
        screen.blit(since_op, pg.Vector2(320, self.sorter_screen.get_height() - 25))
        screen.blit(srted, pg.Vector2(480, self.sorter_screen.get_height() - 25))

    def render(self, screen: pg.Surface):
        self.sorter_screen.fill(GameValues.BG_COL)

        pg.draw.rect(self.sorter_screen, (255, 255, 255), self.outline_rect, 1)

        items_width = self.size.x - (self.margin * 2)
        bar_width = items_width / self.item_num
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
                self.render_text(self.sorter_screen)

        # final
        screen.blit(self.sorter_screen, self.pos)


class MethodSorter:
    """ (theoretical) abstract class """
    def __init__(self, sorter: Sorter):
        self.sorter = sorter

    def advance(self):
        pass

    def validator(self, value: int) -> str:
        return str(value)

    def get_looking_at_items(self) -> list[int]:
        return []

    def get_completed_items(self) -> list[int]:
        return []


class BubbleSorter(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)

        self.looking_at_item = 0
        self.completed_items = 0

    def advance(self):
        total = self.sorter.item_num

        if self.looking_at_item + 1 < total and self.looking_at_item < (total - self.completed_items):
            a, b = self.looking_at_item, self.looking_at_item + 1
            if self.sorter.items[a] > self.sorter.items[b]:
                self.sorter.swap_items(a, b)
            self.looking_at_item += 1
            return

        self.completed_items += 1
        self.looking_at_item = 0
        if self.completed_items == total or self.sorter.is_sorted():
            self.sorter.complete_sorting()

    def get_looking_at_items(self) -> list[int]:
        return [self.looking_at_item]

    def get_completed_items(self) -> list[int]:
        li = []
        for i, item in enumerate(self.sorter.items):
            if i + 1 > (self.sorter.item_num - self.completed_items):
                li.append(i)
        return li


class MergeSort(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)

        self.groups = [[i] for i in self.sorter.items]
        self.moved_groups = [[] for _ in range(round(len(self.groups) / 2))]
        self.groups_of = 1
        self.on_group = 0
        self.on_moved_group = 0

        self.even = self.sorter.item_num % 2 == 0

    def advance(self):
        print("before:")
        print("group:       ", self.on_group, len(self.groups), self.groups)
        print("moved group: ", self.on_moved_group, len(self.moved_groups), self.moved_groups)

        # move stuff
        if len(self.groups[self.on_group]) == 0:
            self.moved_groups[self.on_moved_group].append(self.groups[self.on_group + 1].pop(0))
        elif len(self.groups[self.on_group + 1]) == 0:
            self.moved_groups[self.on_moved_group].append(self.groups[self.on_group].pop(0))
        else:
            add = int(self.groups[self.on_group][0] > self.groups[self.on_group + 1][0])  # 0 or 1
            self.moved_groups[self.on_moved_group].append(self.groups[self.on_group + add].pop(0))

        # update items list
        li = []
        for i in self.moved_groups:
            for ii in i:
                li.append(ii)
        self.sorter.items = li + self.sorter.items[len(li):]

        # finish group
        if len(self.groups[self.on_group]) == 0 and len(self.groups[self.on_group + 1]) == 0:
            self.on_group += 2
            self.on_moved_group += 1

            # finish row
            if len(self.groups[-1]) == 0:
                self.on_group = 0
                self.on_moved_group = 0
                self.groups_of += self.groups_of
                self.groups = self.moved_groups
                self.moved_groups = [[] for _ in range(round(len(self.groups) / 2))]

        # finish sort
        if self.sorter.is_sorted(self.groups[0]):
            self.sorter.complete_sorting()
            self.sorter.items = self.groups[0]

        print("after:")
        print("group:       ", self.on_group, len(self.groups), self.groups)
        print("moved group: ", self.on_moved_group, len(self.moved_groups), self.moved_groups)
        print("             ", self.sorter.items)

    def validator(self, value: int) -> str:
        return str(int(value) + (value % 2))
