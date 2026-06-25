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


def get_spawn_positions(level_num, wave_num):
    if level_num == 1:
        if wave_num == 1:
            return [(400, 200), (700, 200), (550, 300)]
        elif wave_num == 2:
            return [(350, 200), (650, 250), (750, 350), (500, 400)]
        elif wave_num == 3:
            return [(300, 200), (600, 200), (800, 300), (450, 350), (700, 400), (550, 250)]
    elif level_num == 2:
        if wave_num == 1:
            return [(300, 300), (500, 300), (400, 400)]
        elif wave_num == 2:
            return [(300, 250), (500, 250), (400, 350), (600, 400)]
        elif wave_num == 3:
            return [(250, 200), (450, 200), (650, 250), (350, 350), (550, 350), (400, 450)]
    elif level_num == 3:
        if wave_num == 1:
            return [(400, 250), (600, 250), (500, 350)]
        elif wave_num == 2:
            return [(350, 200), (550, 200), (450, 300), (650, 350)]
        elif wave_num == 3:
            return [(300, 200), (500, 200), (700, 200), (400, 350), (600, 350), (500, 450)]
    return [(400, 300)]


def spawn_wave():
    global wave_spawned
    enemies.empty()

    positions = get_spawn_positions(current_level, wave)

    for x, y in positions:
        enemy = Enemy(x, y)
        enemies.add(enemy)

    wave_spawned = True


def load_level(level_num):
    global level_width, level_height, platforms, enemies, pickups, wave, wave_spawned
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
    global wave, wave_spawned

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
            enemy.update(player, platforms)

        for pickup in pickups:
            pickup.update(player)

        if len(enemies) == 0 and wave_spawned:
            wave += 1
            wave_spawned = False
            if wave > 3:
                wave = 1
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

        for pickup in pickups:
            screen.blit(pickup.image, (pickup.rect.x - camera_x, pickup.rect.y - camera_y))

        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

        if player.alive:
            screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
            player.draw_gun(screen, camera_x, camera_y)
        else:
            if (player.death_timer // 10) % 2 == 0:
                screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

        for bullet in player.bullets:
            screen.blit(bullet.image, (bullet.rect.x - camera_x, bullet.rect.y - camera_y))

        player.draw_ui(screen)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(crosshair_img, (mouse_x - 16, mouse_y - 16))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()