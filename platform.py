import pygame
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, wall_type=0):
        super().__init__()
        self.image = self.load_wall_image(wall_type, width, height)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def load_wall_image(self, wall_type, width, height):
        walls_path = os.path.join(BASE_PATH, "Environment")
        img = pygame.image.load(os.path.join(walls_path, f"walls{wall_type}.png")).convert_alpha()
        img = pygame.transform.scale(img, (width, height))
        return img