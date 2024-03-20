

def get_middle(pos_x, width_1, width_2) -> int:
    return pos_x + ((width_1 / 2) - (width_2 / 2))


class SortingMethods:
    BUBBLE = "Bubble Sort"
    OTHER = "Other Sort"


class Texts:
    START = "> Start <"
    RE_GEN = "Re-gen"
    CHANGE = "change"
    ITEMS_NUM = "Num of items"
    FRAMES_OP = "Frames / Op"
    MARGIN = "Margin"
    SORTING_METHOD = "Sorting Method:"


class GameValues:
    FONT = "Times New Roman"

    MIN_ITEMS = 3
    MIN_FRAMES = 1
    MIN_MARGIN = 30

    MAX_ITEMS = 500
    MAX_FRAMES = 100
    MAX_MARGIN = 100

    BG_COL = (0, 5, 5)

    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    RES_MUL = 1
