import pygame
import os
import math

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()

        self.idle_frame = None
        self.walk_frames = []
        self.bite_frames = []
        self.load_animations()

        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0

        self.image = self.idle_frame
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.speed = 1.5
        self.vel_x = 0
        self.vel_y = 0

        self.hp = 3
        self.damage = 1

        self.direction = "right"
        self.attack_cooldown = 0
        self.bite_lock = False
        self.target = None
        self.aggro_range = 250
        self.attack_range = 40

    def load_animations(self):
        enemies_path = os.path.join(BASE_PATH, "Enemies")

        self.idle_frame = pygame.image.load(os.path.join(enemies_path, "Enemy11.png")).convert_alpha()
        self.idle_frame = pygame.transform.scale(self.idle_frame, (48, 48))

        for i in range(1, 5):
            img = pygame.image.load(os.path.join(enemies_path, f"Enemy1{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (48, 48))
            self.walk_frames.append(img)

        bite14 = pygame.image.load(os.path.join(enemies_path, "Enemy14.png")).convert_alpha()
        bite14 = pygame.transform.scale(bite14, (48, 48))
        self.bite_frames.append(bite14)

        bite15 = pygame.image.load(os.path.join(enemies_path, "Enemy15.png")).convert_alpha()
        bite15 = pygame.transform.scale(bite15, (48, 48))
        self.bite_frames.append(bite15)

    def update(self, player, platforms):
        if self.hp <= 0:
            self.kill()
            return

        dist_to_player = math.hypot(player.rect.centerx - self.rect.centerx,
                                    player.rect.centery - self.rect.centery)

        if dist_to_player < self.aggro_range:
            self.target = player
        else:
            self.target = None
            if not self.bite_lock:
                self.state = "idle"
            self.vel_x = 0
            self.vel_y = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.target and not self.bite_lock:
            if dist_to_player <= self.attack_range:
                self.vel_x = 0
                self.vel_y = 0
                if self.attack_cooldown <= 0:
                    self.state = "bite"
                    self.frame_index = 0
                    self.animation_timer = 0
                    self.bite_lock = True
                    self.target.take_damage(self.damage)
                    self.attack_cooldown = 40
            else:
                self.state = "walk"
                dx = self.target.rect.centerx - self.rect.centerx
                dy = self.target.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.vel_x = (dx / dist) * self.speed
                    self.vel_y = (dy / dist) * self.speed

        if self.vel_x < 0:
            self.direction = "left"
        elif self.vel_x > 0:
            self.direction = "right"

        self.rect.x += self.vel_x
        self.check_collision(platforms, 'x')

        self.rect.y += self.vel_y
        self.check_collision(platforms, 'y')

        self.update_animation()

    def update_animation(self):
        if self.state == "walk":
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 4
            self.image = self.walk_frames[self.frame_index]
        elif self.state == "bite":
            self.animation_timer += 1
            if self.animation_timer >= 30:
                self.animation_timer = 0
                self.frame_index += 1
                if self.frame_index >= 2:
                    self.frame_index = 0
                    self.state = "idle"
                    self.bite_lock = False
            self.image = self.bite_frames[self.frame_index]
        else:
            self.image = self.idle_frame

        if self.direction == "left":
            self.image = pygame.transform.flip(self.image, True, False)

    def check_collision(self, platforms, direction):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if direction == 'x':
                    if self.vel_x > 0:
                        self.rect.right = platform.rect.left
                    elif self.vel_x < 0:
                        self.rect.left = platform.rect.right
                    self.vel_x = 0

                elif direction == 'y':
                    if self.vel_y > 0:
                        self.rect.bottom = platform.rect.top
                    elif self.vel_y < 0:
                        self.rect.top = platform.rect.bottom
                    self.vel_y = 0

    def take_damage(self, damage):
        self.hp -= damage
        if self.hp <= 0:
            self.kill()