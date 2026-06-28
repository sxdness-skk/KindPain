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
wave_timer = 0
spawn_positions = []
door_active = False
door_position = (0, 0)
weapon_pickup_active = False
weapon_pickup_position = (0, 0)
weapon_pickup_type = ""
all_waves_complete = False



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


def start_wave_timer():
    global wave_timer, spawn_positions
    positions = get_empty_positions(current_level)
    random.shuffle(positions)

    if wave == 1:
        count = 3
        wave_timer = FPS * 5
    elif wave == 2:
        count = 4
        wave_timer = FPS * 3
    elif wave == 3:
        count = 6
        wave_timer = FPS * 3

    spawn_positions = positions[:count]


def spawn_wave():
    global wave_spawned, spawn_positions
    enemies.empty()

    for x, y in spawn_positions:
        enemy = Enemy(x, y)
        enemies.add(enemy)

    spawn_positions = []
    wave_spawned = True


def spawn_door_and_weapon():
    global door_active, door_position, weapon_pickup_active, weapon_pickup_position, weapon_pickup_type

    door_position = (level_width // 2, level_height // 2)
    door_active = True

    weapon_pickup_position = (level_width // 2, level_height // 2 - 80)
    weapon_pickup_active = True

    if current_level == 1:
        weapon_pickup_type = "PP"
    elif current_level == 2:
        weapon_pickup_type = "AK"


def load_level(level_num):
    global level_width, level_height, platforms, enemies, pickups, wave, wave_spawned, wave_timer, spawn_positions
    global door_active, door_position, weapon_pickup_active, weapon_pickup_position, weapon_pickup_type, all_waves_complete
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
    wave_timer = 0
    spawn_positions = []
    door_active = False
    door_position = (0, 0)
    weapon_pickup_active = False
    weapon_pickup_position = (0, 0)
    weapon_pickup_type = ""
    all_waves_complete = False


pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("KindPain")
clock = pygame.time.Clock()

pygame.mouse.set_visible(False)
crosshair_path = os.path.join(os.path.dirname(__file__), "Image", "Player", "Weapon", "Gun", "Crosshair.png")
crosshair_img = pygame.image.load(crosshair_path).convert_alpha()
crosshair_img = pygame.transform.scale(crosshair_img, (32, 32))


pp_gun_path = os.path.join(os.path.dirname(__file__), "Image", "Player", "Weapon", "Gun", "PP.png")
pp_gun_img = pygame.image.load(pp_gun_path).convert_alpha()
pp_gun_img = pygame.transform.scale(pp_gun_img, (48, 30))

ak_gun_path = os.path.join(os.path.dirname(__file__), "Image", "Player", "Weapon", "Gun", "AK.png")
ak_gun_img = pygame.image.load(ak_gun_path).convert_alpha()
ak_gun_img = pygame.transform.scale(ak_gun_img, (48, 30))

def main():
    global current_level, player, platforms, enemies, pickups, level_width, level_height
    global wave, wave_spawned, wave_timer, spawn_positions, door_active, door_position
    global weapon_pickup_active, weapon_pickup_position, weapon_pickup_type, all_waves_complete

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

        if not wave_spawned and not all_waves_complete and wave_timer == 0:
            start_wave_timer()

        if wave_timer > 0:
            wave_timer -= 1
            if wave_timer == 0:
                spawn_wave()

        for enemy in enemies:
            pickup = enemy.update(player, platforms)
            if pickup:
                pickups.add(pickup)

        for pickup in pickups:
            pickup.update()

        if len(enemies) == 0 and wave_spawned and not all_waves_complete:
            wave += 1
            wave_spawned = False
            if wave > 3:
                all_waves_complete = True
                spawn_door_and_weapon()

        if door_active:
            door_rect = pygame.Rect(door_position[0] - 30, door_position[1] - 30, 60, 60)
            if player.alive and player.rect.colliderect(door_rect) and not weapon_pickup_active:
                current_level += 1
                if current_level > len(level_list):
                    current_level = 1
                load_level(current_level)
                player.respawn()

        if weapon_pickup_active:
            weapon_rect = pygame.Rect(weapon_pickup_position[0] - 20, weapon_pickup_position[1] - 20, 40, 40)
            if player.alive and player.rect.colliderect(weapon_rect):
                player.set_weapon(weapon_pickup_type)
                weapon_pickup_active = False

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

        for x, y in spawn_positions:
            circle_x = x - camera_x
            circle_y = y - camera_y
            radius = 30 + int(10 * (1 - wave_timer / (FPS * 3)))
            alpha = 150
            circle_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(circle_surf, (255, 50, 50, alpha), (radius, radius), radius)
            pygame.draw.circle(circle_surf, (255, 100, 100, alpha), (radius, radius), radius - 4, 2)
            screen.blit(circle_surf, (circle_x - radius, circle_y - radius))

        for enemy in enemies:
            screen.blit(enemy.image, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

        for pickup in pickups:
            screen.blit(pickup.image, (pickup.rect.x - camera_x, pickup.rect.y - camera_y))

        if door_active:
            door_x = door_position[0] - camera_x
            door_y = door_position[1] - camera_y
            door_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.rect(door_surf, (255, 215, 0, 180), (0, 0, 60, 60))
            pygame.draw.rect(door_surf, (255, 255, 255), (0, 0, 60, 60), 3)
            font = pygame.font.Font(None, 20)
            text = font.render("NEXT", True, (255, 255, 255))
            door_surf.blit(text, (8, 20))
            screen.blit(door_surf, (door_x - 30, door_y - 30))

            if weapon_pickup_active:
                wp_x = weapon_pickup_position[0] - camera_x
                wp_y = weapon_pickup_position[1] - camera_y
                if weapon_pickup_type == "PP":
                    screen.blit(pp_gun_img, (wp_x - 24, wp_y - 15))
                elif weapon_pickup_type == "AK":
                    screen.blit(ak_gun_img, (wp_x - 24, wp_y - 15))

        if player.alive:
            screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))
            player.draw_gun(screen, camera_x, camera_y)
        else:
            if (player.death_timer // 10) % 2 == 0:
                screen.blit(player.image, (player.rect.x - camera_x, player.rect.y - camera_y))

        for bullet in player.bullets:
            screen.blit(bullet.image, (bullet.rect.x - camera_x, bullet.rect.y - camera_y))

        if wave_timer > 0 and wave == 1:
            font = pygame.font.Font(None, 36)
            timer_text = font.render(f"До начала: {wave_timer // FPS + 1}", True, (255, 255, 255))
            text_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
            screen.blit(timer_text, text_rect)

        player.draw_ui(screen)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(crosshair_img, (mouse_x - 16, mouse_y - 16))

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()