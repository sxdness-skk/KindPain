import pygame
import os
import math
import random

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Pickup(pygame.sprite.Sprite):
    def __init__(self, x, y, pickup_type):
        super().__init__()

        self.pickup_type = pickup_type
        self.load_image()

        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        self.base_y = y
        self.float_timer = random.uniform(0, math.pi * 2)
        self.float_speed = 0.03
        self.float_range = 5

        self.lifetime = 600

    def load_image(self):
        enemies_path = os.path.join(BASE_PATH, "Enemies")

        if self.pickup_type == "heal":
            img = pygame.image.load(os.path.join(enemies_path, "Heal.png")).convert_alpha()
            img = pygame.transform.scale(img, (24, 24))
        elif self.pickup_type == "shield":
            img = pygame.image.load(os.path.join(enemies_path, "Shield.png")).convert_alpha()
            img = pygame.transform.scale(img, (24, 24))

        self.image = img

    def update(self, player):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        self.float_timer += self.float_speed
        self.rect.centery = self.base_y + math.sin(self.float_timer) * self.float_range

        if player.alive and self.rect.colliderect(player.rect):
            if self.pickup_type == "heal":
                if player.hp < player.max_hp:
                    player.hp = min(player.hp + 2, player.max_hp)
                    self.kill()
            elif self.pickup_type == "shield":
                if player.armor < player.max_armor:
                    player.armor = min(player.armor + 1, player.max_armor)
                    self.kill()