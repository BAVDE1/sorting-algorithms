from pysinewave import SineWave


class SoundManager:
    def __init__(self):
        self.sound_on = False

        self.pitch_upper_limit = 20
        self.decibels_default = 20
        self.decibels_lower_limit = -200

        self.sine_wave = SineWave(pitch=0, decibels=self.decibels_lower_limit, decibels_per_second=1000, pitch_per_second=1000)

        # init
        self.toggle_sound(False)
        self.sine_wave.play()

    def toggle_sound(self, toggle=None):
        self.sound_on = toggle if toggle is not None else not self.sound_on
        self.change_volume()

    def change_volume(self, volume=None):
        if self.sound_on:
            volume = volume if volume is not None else self.decibels_lower_limit
            self.sine_wave.set_volume(volume)

    def change_pitch(self, pitch):
        self.sine_wave.set_pitch(pitch)
