import pygame
import os
import math
import random

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type="normal", sound_manager=None):
        super().__init__()

        self.sound_manager = sound_manager
        self.enemy_type = enemy_type
        self.idle_frame = None
        self.walk_frames = []
        self.attack_frames = []
        self.load_animations()

        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0

        self.image = self.idle_frame
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        if enemy_type == "normal":
            self.speed = 1.5
            self.hp = 3
            self.damage = 1
        elif enemy_type == "heavy":
            self.speed = 1.0
            self.hp = 8
            self.damage = 3

        self.vel_x = 0
        self.vel_y = 0

        self.direction = "right"
        self.attack_cooldown = 0
        self.attack_lock = False
        self.target = None
        self.aggro_range = 500
        self.attack_range = 50
        self.stuck_timer = 0
        self.avoid_timer = 0
        self.avoid_dx = 0
        self.avoid_dy = 0

    def load_animations(self):
        enemies_path = os.path.join(BASE_PATH, "Enemies")

        if self.enemy_type == "normal":
            self.idle_frame = pygame.image.load(os.path.join(enemies_path, "Enemy11.png")).convert_alpha()
            self.idle_frame = pygame.transform.scale(self.idle_frame, (64, 64))

            for i in range(1, 5):
                img = pygame.image.load(os.path.join(enemies_path, f"Enemy1{i}.png")).convert_alpha()
                img = pygame.transform.scale(img, (64, 64))
                self.walk_frames.append(img)

            for i in range(1, 6):
                img = pygame.image.load(os.path.join(enemies_path, f"Atack_{i}.png")).convert_alpha()
                img = pygame.transform.scale(img, (64, 64))
                self.attack_frames.append(img)


        elif self.enemy_type == "heavy":
            self.idle_frame = pygame.image.load(os.path.join(enemies_path, "Enemy21.png")).convert_alpha()
            self.idle_frame = pygame.transform.scale(self.idle_frame, (96, 96))
            for i in range(1, 7):
                img = pygame.image.load(os.path.join(enemies_path, f"Enemy2{i}.png")).convert_alpha()
                img = pygame.transform.scale(img, (96, 96))
                self.walk_frames.append(img)
            for i in range(7, 14):
                img = pygame.image.load(os.path.join(enemies_path, f"Enemy2{i}.png")).convert_alpha()
                img = pygame.transform.scale(img, (96, 96))
                self.attack_frames.append(img)

    def can_move_to(self, x, y, platforms):
        test_rect = self.rect.copy()
        test_rect.x = x
        test_rect.y = y
        for platform in platforms:
            if test_rect.colliderect(platform.rect):
                return False
        return True

    def update(self, player, platforms):
        if self.hp <= 0:
            pickup = self.drop_pickup()
            self.kill()
            return pickup

        if not player.alive:
            self.target = None
            self.state = "idle"
            self.vel_x = 0
            self.vel_y = 0
            self.update_animation()
            return None

        dist_to_player = math.hypot(player.rect.centerx - self.rect.centerx,
                                    player.rect.centery - self.rect.centery)

        if dist_to_player < self.aggro_range:
            self.target = player
        else:
            self.target = None
            self.state = "idle"
            self.vel_x = 0
            self.vel_y = 0

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        if self.target and not self.attack_lock:
            if dist_to_player <= self.attack_range:
                self.vel_x = 0
                self.vel_y = 0
                if self.attack_cooldown <= 0:
                    self.state = "attack"
                    self.frame_index = 0
                    self.animation_timer = 0
                    self.attack_lock = True
                    self.target.take_damage(self.damage)
                    self.attack_cooldown = 60
                    if self.enemy_type == "heavy" and self.sound_manager:
                        self.sound_manager.play("ogrbeat")
            else:
                self.state = "walk"
                dx = self.target.rect.centerx - self.rect.centerx
                dy = self.target.rect.centery - self.rect.centery
                dist = math.hypot(dx, dy)
                if dist > 0:
                    self.vel_x = (dx / dist) * self.speed
                    self.vel_y = (dy / dist) * self.speed

                if self.enemy_type == "heavy" and self.sound_manager:
                    self.sound_manager.play_random_ogr()

        if self.avoid_timer > 0:
            self.avoid_timer -= 1
            self.vel_x = self.avoid_dx
            self.vel_y = self.avoid_dy
        elif self.target:
            new_x = self.rect.x + self.vel_x
            new_y = self.rect.y + self.vel_y
            if not self.can_move_to(new_x, self.rect.y, platforms):
                if self.can_move_to(self.rect.x, self.rect.y - self.speed * 3, platforms):
                    self.avoid_dx = 0
                    self.avoid_dy = -self.speed
                    self.avoid_timer = 30
                elif self.can_move_to(self.rect.x, self.rect.y + self.speed * 3, platforms):
                    self.avoid_dx = 0
                    self.avoid_dy = self.speed
                    self.avoid_timer = 30
                else:
                    self.vel_x = 0
            if not self.can_move_to(self.rect.x, new_y, platforms):
                if self.can_move_to(self.rect.x - self.speed * 3, self.rect.y, platforms):
                    self.avoid_dx = -self.speed
                    self.avoid_dy = 0
                    self.avoid_timer = 30
                elif self.can_move_to(self.rect.x + self.speed * 3, self.rect.y, platforms):
                    self.avoid_dx = self.speed
                    self.avoid_dy = 0
                    self.avoid_timer = 30
                else:
                    self.vel_y = 0

        if self.vel_x < 0:
            self.direction = "left"
        elif self.vel_x > 0:
            self.direction = "right"

        self.rect.x += self.vel_x
        self.check_collision(platforms, 'x')

        self.rect.y += self.vel_y
        self.check_collision(platforms, 'y')

        self.update_animation()
        return None

    def update_animation(self):
        if self.state == "walk":
            self.animation_timer += 1
            if self.animation_timer >= 10:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.walk_frames)
            self.image = self.walk_frames[self.frame_index]
        elif self.state == "attack":
            self.animation_timer += 1
            if self.animation_timer >= 12:
                self.animation_timer = 0
                self.frame_index += 1
                if self.frame_index >= len(self.attack_frames):
                    self.frame_index = 0
                    self.state = "idle"
                    self.attack_lock = False
            self.image = self.attack_frames[self.frame_index]
        else:
            self.image = self.idle_frame

        if self.direction == "right" and self.enemy_type == "normal":
            self.image = pygame.transform.flip(self.image, True, False)
        elif self.direction == "left" and self.enemy_type == "heavy":
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

    def drop_pickup(self):
        from pickup import Pickup
        roll = random.random()
        if self.enemy_type == "heavy":
            if roll < 0.6:
                pickup = Pickup(self.rect.centerx, self.rect.centery, "hp")
                return pickup
            elif roll < 0.9:
                pickup = Pickup(self.rect.centerx, self.rect.centery, "armor")
                return pickup
        else:
            if roll < 0.4:
                pickup = Pickup(self.rect.centerx, self.rect.centery, "hp")
                return pickup
            elif roll < 0.7:
                pickup = Pickup(self.rect.centerx, self.rect.centery, "armor")
                return pickup
        return None