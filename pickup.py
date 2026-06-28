import pygame
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, pickup_type):
        super().__init__()

        self.pickup_type = pickup_type

        if pickup_type == "hp":
            path = os.path.join(BASE_PATH, "Enemies", "Heal.png")
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (24, 24))
            self.heal_amount = 3
        elif pickup_type == "armor":
            path = os.path.join(BASE_PATH, "Enemies", "Shield.png")
            self.image = pygame.image.load(path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (24, 24))
            self.armor_amount = 2

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.lifetime = 600

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()