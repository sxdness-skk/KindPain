import pygame
import os
import math
from config import SCREEN_WIDTH, SCREEN_HEIGHT, ENERGY_REGEN_RATE

ATTACK_COOLDOWN = 15

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image")


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sound_manager=None):
        super().__init__()

        self.sound_manager = sound_manager

        self.animations = {"left": [], "right": [], "up": [], "down": []}
        self.load_animations()

        self.direction = "right"
        self.last_horizontal = "right"
        self.frame_index = 0
        self.animation_timer = 0
        self.is_moving = False

        self.image = self.animations["right"][0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.vel_x = 0
        self.vel_y = 0

        self.hp = 10
        self.max_hp = 10
        self.armor = 0
        self.max_armor = 5
        self.energy = 200
        self.max_energy = 200

        self.attack_cooldown = 0
        self.bullets = pygame.sprite.Group()

        self.alive = True
        self.death_timer = 0
        self.death_duration = 120

        self.shoot_hold = False
        self.weapon_type = "gun"
        self.gun_sprites = {}
        self.bullet_sprites = {}
        self.current_gun_sprite = None
        self.current_bullet_sprite = None
        self.gun_offset = (0, 0)
        self.weapon_energy_cost = 0
        self.unlocked_weapons = ["gun"]
        self.laser_active = False
        self.laser_angle = 0
        self.load_weapons()

    def load_animations(self):
        anim_left_path = os.path.join(BASE_PATH, "Player", "Anim_left")
        for i in range(1, 5):
            img = pygame.image.load(os.path.join(anim_left_path, f"left_{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (64, 72))
            self.animations["left"].append(img)

        anim_right_path = os.path.join(BASE_PATH, "Player", "Anim_right")
        for i in range(1, 5):
            img = pygame.image.load(os.path.join(anim_right_path, f"right_{i}.png")).convert_alpha()
            img = pygame.transform.scale(img, (64, 72))
            self.animations["right"].append(img)

        self.animations["up"] = self.animations["right"].copy()
        self.animations["down"] = self.animations["right"].copy()

    def load_weapons(self):
        weapon_path = os.path.join(BASE_PATH, "Player", "Weapon", "Gun")

        self.gun_sprites["gun"] = pygame.image.load(os.path.join(weapon_path, "gun_1.png")).convert_alpha()
        self.gun_sprites["gun"] = pygame.transform.scale(self.gun_sprites["gun"], (32, 20))
        self.bullet_sprites["gun"] = pygame.image.load(os.path.join(weapon_path, "bullet.png")).convert_alpha()
        self.bullet_sprites["gun"] = pygame.transform.scale(self.bullet_sprites["gun"], (16, 16))

        self.gun_sprites["PP"] = pygame.image.load(os.path.join(weapon_path, "PP.png")).convert_alpha()
        self.gun_sprites["PP"] = pygame.transform.scale(self.gun_sprites["PP"], (32, 20))

        self.gun_sprites["AK"] = pygame.image.load(os.path.join(weapon_path, "AK.png")).convert_alpha()
        self.gun_sprites["AK"] = pygame.transform.scale(self.gun_sprites["AK"], (32, 20))
        self.bullet_sprites["AK"] = pygame.image.load(os.path.join(weapon_path, "Bullet_AK.png")).convert_alpha()
        self.bullet_sprites["AK"] = pygame.transform.scale(self.bullet_sprites["AK"], (16, 16))

        self.current_gun_sprite = self.gun_sprites["gun"]
        self.current_bullet_sprite = self.bullet_sprites["gun"]
        self.weapon_energy_cost = 0

    def set_weapon(self, weapon_type):
        if weapon_type in self.gun_sprites:
            self.weapon_type = weapon_type
            self.current_gun_sprite = self.gun_sprites[weapon_type]
            if weapon_type in self.bullet_sprites:
                self.current_bullet_sprite = self.bullet_sprites[weapon_type]
            if weapon_type == "PP":
                self.weapon_energy_cost = 30
            elif weapon_type == "AK":
                self.weapon_energy_cost = 5
            else:
                self.weapon_energy_cost = 0
            if weapon_type not in self.unlocked_weapons:
                self.unlocked_weapons.append(weapon_type)

    def switch_weapon(self, slot):
        weapons = ["gun", "PP", "AK"]
        if slot < len(weapons) and weapons[slot] in self.unlocked_weapons:
            self.set_weapon(weapons[slot])

    def stop_shooting(self):
        self.shoot_hold = False
        self.laser_active = False

    def update(self, platforms, enemies=None, pickups=None):
        if not self.alive:
            self.death_timer += 1
            self.bullets.update(platforms, enemies)
            return

        self.rect.x += self.vel_x
        self.check_collision(platforms, 'x')

        self.rect.y += self.vel_y
        self.check_collision(platforms, 'y')

        self.update_animation()

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.energy = min(self.energy + ENERGY_REGEN_RATE, self.max_energy)

        self.bullets.update(platforms, enemies)

        if pickups:
            for pickup in pickups:
                if self.rect.colliderect(pickup.rect):
                    if pickup.pickup_type == "hp":
                        self.hp = min(self.hp + pickup.heal_amount, self.max_hp)
                        if self.sound_manager:
                            self.sound_manager.play("heal")
                    elif pickup.pickup_type == "armor":
                        self.armor = min(self.armor + pickup.armor_amount, self.max_armor)
                        if self.sound_manager:
                            self.sound_manager.play("shield")
                    pickup.kill()

    def update_animation(self):
        if self.vel_x < 0:
            self.direction = "left"
            self.last_horizontal = "left"
        elif self.vel_x > 0:
            self.direction = "right"
            self.last_horizontal = "right"
        else:
            self.direction = self.last_horizontal

        self.is_moving = abs(self.vel_x) > 0.1 or abs(self.vel_y) > 0.1

        if self.is_moving:
            self.animation_timer += 1
            if self.animation_timer >= 8:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % 4
        else:
            self.frame_index = 0

        self.image = self.animations[self.direction][self.frame_index]

        if self.direction == "right":
            self.gun_offset = (35, 32)
        elif self.direction == "left":
            self.gun_offset = (-3, 32)
        elif self.direction == "up":
            self.gun_offset = (20, 12)
        elif self.direction == "down":
            self.gun_offset = (20, 50)

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

    def shoot(self, target_x, target_y, camera_x=0, camera_y=0):
        if not self.alive:
            return None

        if self.weapon_type == "PP":
            if not self.shoot_hold:
                self.laser_active = False
                return None
            if self.energy <= 0:
                self.laser_active = False
                return None

            if not self.laser_active and self.sound_manager:
                self.sound_manager.play("laser")

            self.laser_active = True
            gun_x = self.rect.x + self.gun_offset[0] + 28
            gun_y = self.rect.y + self.gun_offset[1] + 10
            dx = (target_x + camera_x) - gun_x
            dy = (target_y + camera_y) - gun_y
            self.laser_angle = math.atan2(dy, dx)
            self.energy = max(0, self.energy - self.weapon_energy_cost / 60)
            if self.energy <= 0:
                self.laser_active = False
            return None
        else:
            self.laser_active = False
            if self.attack_cooldown > 0:
                return None
            if self.energy < self.weapon_energy_cost:
                return None

            if self.sound_manager:
                self.sound_manager.play("gun")

            if self.weapon_type == "AK":
                self.attack_cooldown = ATTACK_COOLDOWN
                bullet_damage = 3
                if self.sound_manager:
                    self.sound_manager.play("ak")
            else:
                self.attack_cooldown = ATTACK_COOLDOWN
                bullet_damage = 1

            self.energy -= self.weapon_energy_cost

            gun_x = self.rect.x + self.gun_offset[0] + 16
            gun_y = self.rect.y + self.gun_offset[1] + 10
            dx = (target_x + camera_x) - gun_x
            dy = (target_y + camera_y) - gun_y
            dist = (dx ** 2 + dy ** 2) ** 0.5
            if dist == 0:
                dist = 1
            dx /= dist
            dy /= dist

            bullet = Bullet(gun_x, gun_y, dx, dy, self.current_bullet_sprite, bullet_damage)
            self.bullets.add(bullet)
            return bullet

    def draw_laser(self, screen, camera_x, camera_y, platforms, enemies):
        if not self.laser_active:
            return

        gun_x = self.rect.x + self.gun_offset[0] + 28
        gun_y = self.rect.y + self.gun_offset[1] + 10

        max_length = 1000
        end_x = gun_x + math.cos(self.laser_angle) * max_length
        end_y = gun_y + math.sin(self.laser_angle) * max_length

        hit_point = None

        for i in range(0, max_length, 4):
            check_x = gun_x + math.cos(self.laser_angle) * i
            check_y = gun_y + math.sin(self.laser_angle) * i
            check_rect = pygame.Rect(check_x - 1, check_y - 1, 2, 2)

            for platform in platforms:
                if platform.rect.colliderect(check_rect):
                    hit_point = (check_x, check_y)
                    break

            if enemies:
                for enemy in enemies:
                    if enemy.rect.collidepoint(check_x, check_y):
                        enemy.take_damage(0.01)
                        break

            if hit_point:
                break

        if hit_point:
            end_x, end_y = hit_point

        start_pos = (gun_x - camera_x, gun_y - camera_y)
        end_pos = (end_x - camera_x, end_y - camera_y)

        pygame.draw.line(screen, ("Blue"), start_pos, end_pos, 3)
        pygame.draw.line(screen, ("Blue"), start_pos, end_pos, 1)

    def draw_gun(self, screen, camera_x, camera_y):
        if self.current_gun_sprite is None:
            return

        gun_x = self.rect.x + self.gun_offset[0] - camera_x
        gun_y = self.rect.y + self.gun_offset[1] - camera_y

        if self.direction == "left":
            gun_img = pygame.transform.flip(self.current_gun_sprite, True, False)
        elif self.direction == "up":
            gun_img = pygame.transform.rotate(self.current_gun_sprite, 90)
        elif self.direction == "down":
            gun_img = pygame.transform.rotate(self.current_gun_sprite, -90)
        else:
            gun_img = self.current_gun_sprite

        screen.blit(gun_img, (gun_x, gun_y))

    def take_damage(self, damage):
        if not self.alive:
            return False

        if self.armor > 0:
            if self.armor >= damage:
                self.armor -= damage
                if self.sound_manager:
                    self.sound_manager.play("beatplayer")
                return False
            else:
                damage -= self.armor
                self.armor = 0

        self.hp -= damage
        if self.sound_manager:
            self.sound_manager.play("beatplayer")
        if self.hp <= 0:
            self.hp = 0
            self.die()
        return True

    def die(self):
        self.alive = False
        self.death_timer = 0
        self.vel_x = 0
        self.vel_y = 0
        if self.sound_manager:
            self.sound_manager.play("gameover")

    def is_death_animation_done(self):
        return self.death_timer >= self.death_duration

    def respawn(self):
        self.alive = True
        self.hp = self.max_hp
        self.armor = 0
        self.energy = self.max_energy
        self.death_timer = 0
        self.vel_x = 0
        self.vel_y = 0
        self.laser_active = False

    def draw_ui(self, screen):
        font = pygame.font.Font(None, 24)

        hp_text = font.render(f"HP: {self.hp}/{self.max_hp}", True, (255, 50, 50))
        screen.blit(hp_text, (10, 10))

        armor_text = font.render(f"Armor: {self.armor}/{self.max_armor}", True, (50, 150, 255))
        screen.blit(armor_text, (10, 35))

        energy_text = font.render(f"Energy: {int(self.energy)}/{self.max_energy}", True, (255, 200, 50))
        screen.blit(energy_text, (10, 60))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, sprite, damage=1):
        super().__init__()

        self.image = sprite.copy()
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y

        speed = 10
        self.dx = dx * speed
        self.dy = dy * speed

        self.damage = damage

    def update(self, platforms=None, enemies=None):
        self.rect.x += self.dx
        self.rect.y += self.dy

        if platforms:
            for platform in platforms:
                if self.rect.colliderect(platform.rect):
                    self.kill()
                    return

        if enemies:
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    enemy.take_damage(self.damage)
                    self.kill()
                    return