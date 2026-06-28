import pygame
import sys
import os
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED, TILE_SIZE
from player import Player
from platform import Platform
from levels import level_list
from Enemy import Enemy
from pickup import Pickup

current_level = 1
wave = 1
wave_spawned = False
door = None
weapon_pickup = None


def get_empty_positions(level_num):
    level_data = level_list[level_num]
    empty_positions = []
    for row in range(2, len(level_data) - 2):
        for col in range(2, len(level_data[row]) - 2):
            if level_data[row][col] == 0:
                if (level_data[row-1][col] == 0 and level_data[row+1][col] == 0 and
                    level_data[row][col-1] == 0 and level_data[row][col+1] == 0):
                    x = col * TILE_SIZE + TILE_SIZE // 2
                    y = row * TILE_SIZE + TILE_SIZE // 2
                    empty_positions.append((x, y))
    return empty_positions


def spawn_wave():
    global wave_spawned
    enemies.empty()

    positions = get_empty_positions(current_level)
    random.shuffle(positions)

    count = 0
    if wave == 1:
        count = 3
    elif wave == 2:
        count = 4
    elif wave == 3:
        count = 6

    spawned = 0
    for x, y in positions:
        if spawned >= count:
            break
        enemy = Enemy(x, y)
        enemies.add(enemy)
        spawned += 1

    wave_spawned = True


def spawn_door():
    global door, weapon_pickup
    door = pygame.sprite.Sprite()
    door.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
    door.image.fill((139, 90, 43))
    door.rect = door.image.get_rect()
    door.rect.centerx = level_width // 2
    door.rect.centery = level_height // 2

    if current_level == 1:
        weapon_pickup = WeaponPickup(level_width // 2, level_height // 2 - TILE_SIZE, "PP")
    elif current_level == 2:
        weapon_pickup = WeaponPickup(level_width // 2, level_height // 2 - TILE_SIZE, "AK")
    else:
        weapon_pickup = None


class WeaponPickup(pygame.sprite.Sprite):
    def __init__(self, x, y, weapon_type):
        super().__init__()
        self.weapon_type = weapon_type
        weapon_path = os.path.join(os.path.dirname(__file__), "Image", "Player", "Weapon", "Gun")
        self.image = pygame.image.load(os.path.join(weapon_path, f"{weapon_type}.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (48, 30))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y


def load_level(level_num):
    global level_width, level_height, platforms, enemies, pickups, wave, wave_spawned, door, weapon_pickup
    level_data = level_list[level_num]
    platforms.empty()
    enemies.empty()
    pickups.empty()

    for row in range(len(level_data)):
        for col in range(len(level_data[row])):
            type = level_data[row][col]
            if type != 0:
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                platforms.add(Platform(x, y, TILE_SIZE, TILE_SIZE, type))

    level_width = len(level_data[0]) * TILE_SIZE
    level_height = len(level_data) * TILE_SIZE

    player.rect.x = level_width // 2
    player.rect.y = level_height // 2

    wave = 1
    wave_spawned = False
    door = None
    weapon_pickup = None


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("KindPain")
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
crosshair_path = os.path.join(os.path.dirname(__file__), "Image", "Player", "Weapon", "Gun", "Crosshair.png")
crosshair_img = pygame.image.load(crosshair_path).convert_alpha()
crosshair_img = pygame.transform.scale(crosshair_img, (32, 32))


def main():
    global current_level, player, platforms, enemies, pickups, level_width, level_height
    global wave, wave_spawned, door, weapon_pickup

    player = Player(100, 400)
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    pickups = pygame.sprite.Group()
    level_width = 0
    level_height = 0

    load_level(current_level)

    running = True
    while running:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    load_level(current_level)
                    player.respawn()
                if event.key == pygame.K_n:
                    current_level += 1
                    if current_level > len(level_list):
                        current_level = 1
                    load_level(current_level)
                    player.respawn()
                if event.key == pygame.K_1:
                    player.switch_weapon(0)
                if event.key == pygame.K_2:
                    player.switch_weapon(1)
                if event.key == pygame.K_3:
                    player.switch_weapon(2)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player.shoot(mouse_x, mouse_y, camera_x, camera_y)

        keys = pygame.key.get_pressed()
        player.vel_x = 0
        player.vel_y = 0

        if player.alive:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                player.vel_x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                player.vel_x = PLAYER_SPEED
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                player.vel_y = -PLAYER_SPEED
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                player.vel_y = PLAYER_SPEED

        if not wave_spawned:
            spawn_wave()

        for enemy in enemies:
            pickup = enemy.update(player, platforms)
            if pickup is not None:
                pickups.add(pickup)

        for pickup in pickups:
            pickup.update()

        if len(enemies) == 0 and wave_spawned:
            wave += 1
            wave_spawned = False
            if wave > 3:
                spawn_door()

        if weapon_pickup and player.alive and player.rect.colliderect(weapon_pickup.rect):
            player.set_weapon(weapon_pickup.weapon_type)
            weapon_pickup = None

        if door and player.alive and player.rect.colliderect(door.rect):
            current_level += 1
            if current_level > len(level_list):
                current_level = 1
            load_level(current_level)
            player.respawn()

        player.update(platforms, enemies, pickups)

        if not player.alive and player.is_death_animation_done():
            load_level(current_level)
            player.respawn()

        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_y = player.rect.centery - SCREEN_HEIGHT // 2

        camera_x = max(0, min(camera_x, level_width - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, level_height - SCREEN_HEIGHT))

        screen.fill((30, 30, 40))

        for platform in platforms:
            screen.blit(platform.image, (platform.rect.x - camera_x, platform.rect.y - camera_y))

        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

        for pickup in pickups:
            screen.blit(pickup.image, (pickup.rect.x - camera_x, pickup.rect.y - camera_y))

        if player.alive:
            screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
            player.draw_gun(screen, camera_x, camera_y)
        else:
            if (player.death_timer // 10) % 2 == 0:
                screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

        for bullet in player.bullets:
            screen.blit(bullet.image, (bullet.rect.x - camera_x, bullet.rect.y - camera_y))

        if weapon_pickup:
            screen.blit(weapon_pickup.image, (weapon_pickup.rect.x - camera_x, weapon_pickup.rect.y - camera_y))

        if door:
            screen.blit(door.image, (door.rect.x - camera_x, door.rect.y - camera_y))

        player.draw_ui(screen)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(crosshair_img, (mouse_x - 16, mouse_y - 16))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()