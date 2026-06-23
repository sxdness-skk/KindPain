import pygame
import sys
import os
import random
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PLAYER_SPEED, TILE_SIZE
from player import Player
from platform import Platform
from levels import level_list
from Enemy import Enemy

current_level = 1
wave = 1
wave_spawned = False


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


def load_level(level_num):
    global level_width, level_height, platforms, enemies, wave, wave_spawned
    level_data = level_list[level_num]
    platforms.empty()
    enemies.empty()

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
    global current_level, player, platforms, enemies, level_width, level_height
    global wave, wave_spawned

    player = Player(100, 400)
    platforms = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
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

        player.update(platforms, enemies)

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