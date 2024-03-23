import math
import time

import pygame as pg
import random

import setuptools

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

        self.sorting_method = SortingMethods.QUICK
        self.sorter: MethodSorter = self.get_sorter()

        self.started = False
        self.completed = False
        self.frames_per_op = 0
        self.frames_since_op = 0
        self.frame_num = 0
        self.operation_num = 0

    def get_sorter(self):
        methods_dic = {
            SortingMethods.BUBBLE: BubbleSorter,
            SortingMethods.MERGE: MergeSort,
            SortingMethods.INSERTION: InsertionSort,
            SortingMethods.QUICK: QuickSort
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
        def adv():
            self.sorter.advance()
            self.frames_since_op = 0
            self.operation_num += 1

        if self.started and not self.completed:
            self.frame_num += 1
            self.frames_since_op += 1
            if self.frames_per_op == 0:
                while not self.completed:
                    adv()
            elif self.frames_since_op >= self.frames_per_op:
                adv()

    def swap_items(self, a, b):
        item_a, item_b = self.items[a], self.items[b]
        self.items[a] = item_b
        self.items[b] = item_a

    def render_text(self, screen: pg.Surface):
        col = (100, 100, 100)
        frames = self.font.render(f"{Texts.FRAMES}: {self.frame_num}", False, col)
        since_op = self.font.render(f"{Texts.SINCE_OP}: {self.frames_since_op}", False, col)
        operations = self.font.render(f"{Texts.OPERATIONS}: {self.operation_num}", False, col)
        srted = self.font.render(f"{Texts.SORTED}: {len(self.sorter.get_completed_items())}/{self.item_num}", False, col)

        screen.blit(frames, pg.Vector2(10, self.sorter_screen.get_height() - 25))
        screen.blit(operations, pg.Vector2(150, self.sorter_screen.get_height() - 25))
        screen.blit(since_op, pg.Vector2(320, self.sorter_screen.get_height() - 25))
        screen.blit(srted, pg.Vector2(450, self.sorter_screen.get_height() - 25))

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
                    if not self.completed and i in self.sorter.get_looking_at_items():
                        return 255, 100, 100
                    if self.completed or i in self.sorter.get_completed_items():
                        return 100, 255, 100
                    return 255, 255, 255

                pg.draw.rect(self.sorter_screen, get_col(), pg.Rect(x, y, math.ceil(bar_width), math.ceil(bar_width * item)))
                self.render_text(self.sorter_screen)

        # final
        screen.blit(self.sorter_screen, self.pos)


class MethodSorter:
    """ (theoretical) abstract class """
    def __init__(self, sorter: Sorter):
        self.sorter = sorter
        self.looking_at = 0

    def advance(self):
        pass

    def validator(self, value: int) -> str:
        return str(value)

    def get_looking_at_items(self) -> list[int]:
        return [self.looking_at]

    def get_completed_items(self) -> list[int]:
        completed = [i for i in range(self.sorter.item_num)]
        return [i for i in completed if i + 1 == self.sorter.items[i]]


class BubbleSorter(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)
        self.completed_items = 0

    def advance(self):
        total = self.sorter.item_num
        a, b = self.looking_at, self.looking_at + 1

        if b < total and a < (total - self.completed_items):
            if self.sorter.items[a] > self.sorter.items[b]:
                self.sorter.swap_items(a, b)
            self.looking_at += 1
            return

        self.completed_items += 1
        self.looking_at = 0
        if self.sorter.is_sorted():
            self.sorter.complete_sorting()


class MergeSort(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)
        self.groups = [[i] for i in self.sorter.items]
        self.moved_groups = self.gen_moved()
        self.on_group = 0
        self.on_moved_group = 0

    def gen_moved(self):
        # generate empty lists
        return [[] for _ in range(round(len(self.groups) / 2))]

    def advance(self):
        # if both groups aren't empty, move lowest, else move item in group that isn't empty
        g1, g2 = self.groups[self.on_group], self.groups[self.on_group + 1]
        add = g1[0] > g2[0] if len(g1) > 0 and len(g2) > 0 else not len(g1)  # either 0 or 1
        self.moved_groups[self.on_moved_group].append(self.groups[self.on_group + add].pop(0))

        # update items list
        li = [item for mg in self.moved_groups for item in mg]
        self.sorter.items = li + self.sorter.items[len(li):]
        self.looking_at = self.sorter.items.index(li[-1])

        # finish group
        if not len(g1) and not len(g2):
            self.on_group += 2
            self.on_moved_group += 1

            # finish row
            if not len(self.groups[-1]):
                self.on_group = self.on_moved_group = 0
                self.groups = self.moved_groups

                # odd no. of groups, split midd group into two
                if len(self.groups) % 2 and len(self.groups) > 1:
                    mid = int((len(self.groups) - 1) / 2)
                    mid_item = self.groups[mid]
                    self.groups[mid] = mid_item[:int(len(mid_item) / 2)]
                    self.groups.insert(mid + 1, mid_item[int(len(mid_item) / 2):])

                self.moved_groups = self.gen_moved()

        # finish sort
        if self.sorter.is_sorted(self.groups[0]):
            self.sorter.complete_sorting()
            self.sorter.items = self.groups[0]

    def validator(self, value: int) -> str:
        # even numbers only
        return str(int(value) + (value % 2))


class InsertionSort(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)
        self.up_to_column = 0
        self.looking_at = 1

    def advance(self):
        if (self.sorter.items[self.looking_at] > self.sorter.items[self.looking_at - 1]) or self.looking_at == 0:
            self.up_to_column += 1
            self.looking_at = self.up_to_column + 1
        else:
            self.sorter.swap_items(self.looking_at - 1, self.looking_at)
            self.looking_at -= 1

        if self.sorter.is_sorted():
            self.sorter.complete_sorting()


class QuickSort(MethodSorter):
    def __init__(self, *args):
        super().__init__(*args)
        if len(self.sorter.items):
            self.locked_in = set()
            self.pivot = self.get_pivot()
            self.left = self.get_left()

    def get_pivot(self):
        if len(self.locked_in):
            for i in range(max(self.locked_in), 0, -1):
                if i not in self.locked_in:
                    return i
        return len(self.sorter.items) - 1

    def get_left(self):
        for i in range(self.pivot, 0, -1):
            if i in self.locked_in:
                return i + 1
        return 0

    def is_in_place(self, index):
        is_in = self.sorter.items[index] == index + 1
        if is_in:
            self.locked_in.add(index)
        return is_in

    def advance(self):
        items = self.sorter.items

        # move items
        if items[self.left] > items[self.pivot]:
            if self.left != self.pivot - 1:
                self.sorter.swap_items(self.pivot, self.pivot - 1)
            self.sorter.swap_items(self.left, self.pivot)
            self.pivot -= 1
        else:
            self.left += 1

        # lock in pivot item
        if self.is_in_place(self.pivot):
            self.pivot -= 1
            self.left = self.get_left()

            # lock in left item
            self.is_in_place(self.left)

            # get new positions
            self.pivot = self.get_pivot()
            self.left = self.get_left()

        if self.sorter.is_sorted():
            self.sorter.complete_sorting()

    def get_looking_at_items(self) -> list[int]:
        return [self.pivot, self.left]

    def get_completed_items(self) -> list[int]:
        return list(self.locked_in)
