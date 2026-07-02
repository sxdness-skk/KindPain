import pygame
import os
import random

BASE_PATH = os.path.join(os.path.dirname(__file__), "Sound")


class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.load_sounds()

    def load_sounds(self):
        self.sounds["beatplayer"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "beatplayer.mp3"))
        self.sounds["gameover"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "gameover.mp3"))
        self.sounds["gun"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "gun.mp3"))
        self.sounds["heal"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "heal.mp3"))
        self.sounds["laser"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "laser.mp3"))
        self.sounds["newgun"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "newgun.mp3"))
        self.sounds["nextlvl"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "nextlvl.mp3"))
        self.sounds["ogr"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "ogr.mp3"))
        self.sounds["ogrbeat"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "ogrbeat.mp3"))
        self.sounds["shield"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "shield.mp3"))
        self.sounds["toboss"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "toboss.mp3"))
        self.sounds["win"] = pygame.mixer.Sound(os.path.join(BASE_PATH, "win.mp3"))

        for sound in self.sounds.values():
            sound.set_volume(0.3)

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

    def play_random_ogr(self):
        if random.random() < 0.005:
            self.play("ogr")