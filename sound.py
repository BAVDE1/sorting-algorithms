import time
import threading
from pysinewave import SineWave


class SoundManager:
    def __init__(self):
        self.max_threads = 5
        self.threads = []

        self.max_sound_pitch = 20
        self.sound_on = False

    def toggle_sound(self):
        self.sound_on = not self.sound_on

    def try_play_sound(self, item_num, number):


    def thread_func(self, item_num, number):
        pitch = (number / item_num) * self.max_sound_pitch
        sine_wave = SineWave(pitch=pitch, decibels=0, decibels_per_second=500)
