import pygame
import sys
import os

BASE_PATH = os.path.join(os.path.dirname(__file__), "Image", "Menu")

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

game_started = False


class Button:
    def __init__(self, text, color, hover_color, action=None):
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.is_hovered = False
        self.rel_x = 0.35
        self.rel_y = 0.42
        self.rel_width = 0.30
        self.rel_height = 0.12
        self.rect = pygame.Rect(0, 0, 0, 0)

    def update_rect(self, window_width, window_height):
        x = int(window_width * self.rel_x)
        y = int(window_height * self.rel_y)
        width = int(window_width * self.rel_width)
        height = int(window_height * self.rel_height)
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        current_color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, current_color, self.rect, border_radius=int(self.rect.height * 0.15))
        pygame.draw.rect(surface, BLACK, self.rect, max(2, int(self.rect.height * 0.03)),
                         border_radius=int(self.rect.height * 0.15))
        font_size = int(self.rect.height * 0.5)
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(self.text, True, WHITE)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


class SpriteSheetAnimation:
    def __init__(self, sprite_sheet_path, frame_width, frame_height, total_frames,
                 cols=None, rows=None, fps=10, loop=True):
        self.sprite_sheet = pygame.image.load(sprite_sheet_path).convert_alpha()
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.total_frames = total_frames
        self.current_frame = 0
        self.fps = fps
        self.loop = loop
        self.is_playing = False
        self.is_finished = False
        self.animation_time = 0
        self.cols = cols
        self.rows = rows
        self.frames = []
        frame_count = 0
        for row in range(self.rows):
            for col in range(self.cols):
                if frame_count >= total_frames:
                    break
                x = col * frame_width
                y = row * frame_height
                frame = self.sprite_sheet.subsurface((x, y, frame_width, frame_height))
                self.frames.append(frame)
                frame_count += 1
            if frame_count >= total_frames:
                break
        while len(self.frames) < total_frames:
            self.frames.append(self.frames[-1])
        self.rect = self.frames[0].get_rect()
        self.x = 0
        self.y = 0
        self.scaled_frames = None
        self.base_width = 960
        self.base_height = 540
        self.current_scale = 1.0
        self.scale_ratio = 2.0

    def update(self, dt):
        if not self.is_playing:
            return
        self.animation_time += dt
        frame_duration = 1000 / self.fps
        frames_to_advance = 0
        while self.animation_time >= frame_duration:
            self.animation_time -= frame_duration
            frames_to_advance += 1
        if frames_to_advance > 0:
            self.current_frame += frames_to_advance
            if self.current_frame >= self.total_frames:
                if self.loop:
                    self.current_frame = self.current_frame % self.total_frames
                else:
                    self.current_frame = self.total_frames - 1
                    self.is_playing = False
                    self.is_finished = True

    def get_current_frame(self):
        if self.scaled_frames:
            return self.scaled_frames[self.current_frame]
        return self.frames[self.current_frame]

    def draw(self, surface, x=None, y=None):
        if x is not None:
            self.x = x
        if y is not None:
            self.y = y
        frame = self.get_current_frame()
        self.rect = frame.get_rect(center=(self.x, self.y))
        surface.blit(frame, self.rect)

    def update_scale(self, window_width, window_height):
        scale_x = window_width / self.base_width
        scale_y = window_height / self.base_height
        base_scale = min(scale_x, scale_y)
        new_scale = base_scale * self.scale_ratio
        if abs(new_scale - self.current_scale) < 0.01:
            return
        self.current_scale = new_scale
        if self.current_scale == 0:
            self.scaled_frames = None
        else:
            self.scaled_frames = []
            for frame in self.frames:
                new_width = max(1, int(frame.get_width() * self.current_scale))
                new_height = max(1, int(frame.get_height() * self.current_scale))
                scaled = pygame.transform.scale(frame, (new_width, new_height))
                self.scaled_frames.append(scaled)

    def play(self):
        self.is_playing = True
        self.is_finished = False

    def stop(self):
        self.is_playing = False

    def reset(self):
        self.current_frame = 0
        self.animation_time = 0
        self.is_playing = False
        self.is_finished = False


class ImageButton:
    def __init__(self, image_path, hover_image_path=None, action=None,
                 rel_x=0.35, rel_y=0.42, rel_width=0.30, rel_height=0.12):
        self.image = pygame.image.load(image_path).convert_alpha()
        if hover_image_path and os.path.exists(hover_image_path):
            self.hover_image = pygame.image.load(hover_image_path).convert_alpha()
        else:
            self.hover_image = self.image.copy()
            self.hover_image.fill((50, 50, 50, 0), special_flags=pygame.BLEND_RGB_ADD)
        self.action = action
        self.is_hovered = False
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.rel_width = rel_width
        self.rel_height = rel_height
        self.rect = pygame.Rect(0, 0, 0, 0)
        self.update_rect(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.scaled_image = None
        self.scaled_hover_image = None
        self.scale_images()

    def update_rect(self, window_width, window_height):
        x = int(window_width * self.rel_x)
        y = int(window_height * self.rel_y)
        width = int(window_width * self.rel_width)
        height = int(window_height * self.rel_height)
        self.rect = pygame.Rect(x, y, width, height)
        self.scale_images()

    def scale_images(self):
        if self.rect.width > 0 and self.rect.height > 0:
            self.scaled_image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height))
            self.scaled_hover_image = pygame.transform.scale(self.hover_image, (self.rect.width, self.rect.height))

    def draw(self, surface):
        if self.is_hovered and self.scaled_hover_image:
            surface.blit(self.scaled_hover_image, self.rect)
        elif self.scaled_image:
            surface.blit(self.scaled_image, self.rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
            if self.is_hovered:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            else:
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                self.action()


def start_game():
    global game_started
    game_started = True


def quit_game():
    pygame.quit()
    sys.exit()


def scale_background(image, window_width, window_height):
    if image is None:
        return None
    return pygame.transform.scale(image, (window_width, window_height))


def scale_name(image, window_width, window_height, width_ratio=0.3, max_width=540):
    if image is None:
        return None
    target_width = min(int(window_width * width_ratio), max_width)
    target_height = int(target_width * (image.get_height() / image.get_width()))
    return pygame.transform.scale(image, (target_width * 1.83, target_height * 1.83))


def scale_image_to_window(image, window_width, window_height, width_ratio=0.3, max_width=540):
    if image is None:
        return None
    target_width = min(int(window_width * width_ratio), max_width)
    target_height = int(target_width * (image.get_height() / image.get_width()))
    return pygame.transform.scale(image, (target_width * 1.2, target_height * 1.2))


def splash_screen(screen, clock):
    global game_started
    game_started = False

    pygame.mouse.set_visible(True)

    M_MENU_PATH = os.path.join(BASE_PATH, "M_menu_ob.png")
    IMAGE_PATH = os.path.join(BASE_PATH, "press_to_play.png")
    BACKGROUND_PATH = os.path.join(BASE_PATH, "main_back.png")
    GAME_NAME_PATH = os.path.join(BASE_PATH, "kind_pain.png")
    ANIM_SHEET_PATH = os.path.join(BASE_PATH, "Anim_Sheet.png")

    FRAME_WIDTH = 480
    FRAME_HEIGHT = 270
    TOTAL_FRAMES = 13
    COLS = 13
    ROWS = 1
    FPS = 24

    try:
        if os.path.exists(ANIM_SHEET_PATH):
            animation = SpriteSheetAnimation(
                sprite_sheet_path=ANIM_SHEET_PATH,
                frame_width=FRAME_WIDTH,
                frame_height=FRAME_HEIGHT,
                total_frames=TOTAL_FRAMES,
                cols=COLS,
                rows=ROWS,
                fps=FPS,
                loop=False
            )
            animation.base_width = WINDOW_WIDTH
            animation.base_height = WINDOW_HEIGHT
            animation.update_scale(WINDOW_WIDTH, WINDOW_HEIGHT)
        else:
            animation = None
    except Exception as e:
        print(f"ошибка загрузки анимации: {e}")
        animation = None

    WAITING = 0
    ANIMATING = 1
    DONE = 2

    state = WAITING

    try:
        or_m_menu = pygame.image.load(M_MENU_PATH) if os.path.exists(M_MENU_PATH) else None
    except:
        or_m_menu = None

    try:
        or_name = pygame.image.load(GAME_NAME_PATH) if os.path.exists(GAME_NAME_PATH) else None
    except:
        or_name = None

    try:
        or_image = pygame.image.load(IMAGE_PATH) if os.path.exists(IMAGE_PATH) else None
    except:
        or_image = None

    try:
        or_background = pygame.image.load(BACKGROUND_PATH) if os.path.exists(BACKGROUND_PATH) else None
    except:
        or_background = None

    background = scale_background(or_background, WINDOW_WIDTH, WINDOW_HEIGHT)
    image = scale_image_to_window(or_image, WINDOW_WIDTH, WINDOW_HEIGHT)
    name = scale_name(or_name, WINDOW_WIDTH, WINDOW_HEIGHT)
    m_menu = scale_background(or_m_menu, WINDOW_WIDTH, WINDOW_HEIGHT)

    alpha = 0
    alpha_direction = 1
    blink_speed = 4
    window_width = WINDOW_WIDTH
    window_height = WINDOW_HEIGHT

    while not game_started and state != DONE:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                window_width = event.w
                window_height = event.h
                screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
                background = scale_background(or_background, window_width, window_height)
                image = scale_image_to_window(or_image, window_width, window_height)
                name = scale_name(or_name, window_width, window_height)
                m_menu = scale_background(or_m_menu, window_width, window_height)
                if animation:
                    animation.base_width = WINDOW_WIDTH
                    animation.base_height = WINDOW_HEIGHT
                    animation.update_scale(window_width, window_height)

            if (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN) and state == WAITING:
                state = ANIMATING
                if animation:
                    animation.reset()
                    animation.play()

        if animation and state == ANIMATING:
            animation.update(dt)
            if not animation.loop and animation.is_finished:
                state = DONE

        alpha += blink_speed * alpha_direction
        if alpha >= 255:
            alpha = 255
            alpha_direction = -1
        elif alpha <= 50:
            alpha = 50
            alpha_direction = 1

        if state == WAITING:
            if background:
                screen.blit(background, (0, 0))
            else:
                screen.fill(BLACK)
            if name:
                name_rect = name.get_rect(center=(window_width // 2, int(window_height * 0.44)))
                screen.blit(name, name_rect)
            if image:
                image_rect = image.get_rect(center=(window_width // 1.87, int(window_height * 0.78)))
                image.set_alpha(alpha)
                screen.blit(image, image_rect)

        elif state == ANIMATING:
            if animation:
                anim_x = window_width // 2
                anim_y = window_height // 2
                if animation.current_frame < 6:
                    if background:
                        screen.blit(background, (0, 0))
                    else:
                        screen.fill(BLACK)
                    if name:
                        name_rect = name.get_rect(center=(window_width // 2, int(window_height * 0.44)))
                        screen.blit(name, name_rect)
                    if image:
                        image_rect = image.get_rect(center=(window_width // 1.87, int(window_height * 0.78)))
                        image.set_alpha(alpha)
                        screen.blit(image, image_rect)
                else:
                    if m_menu:
                        screen.blit(m_menu, (0, 0))
                    else:
                        screen.fill(BLACK)
                animation.draw(screen, anim_x, anim_y)

        elif state == DONE:
            if m_menu:
                screen.blit(m_menu, (0, 0))
            else:
                screen.fill(BLACK)
            main_menu(screen, clock)
            return

        pygame.display.flip()


def main_menu(screen, clock):
    global game_started
    game_started = False

    pygame.mouse.set_visible(True)

    SETTING_PATH = os.path.join(BASE_PATH, "M_menu_knopka_Nas.png")
    NEW_GAME_IMAGE = os.path.join(BASE_PATH, "M_menu_knopka.png")
    QUIT_IMAGE = os.path.join(BASE_PATH, "M_menu_knopka_vih.png")
    M_BACKGROUND_PATH = os.path.join(BASE_PATH, "M_menu_Fon.png")

    try:
        or_m_background = pygame.image.load(M_BACKGROUND_PATH) if os.path.exists(M_BACKGROUND_PATH) else None
    except:
        or_m_background = None

    width, height = screen.get_width(), screen.get_height()
    background = scale_background(or_m_background, width, height)

    new_game_button = ImageButton(
        image_path=NEW_GAME_IMAGE,
        action=start_game,
        rel_x=0.02,
        rel_y=0.155,
        rel_width=0.425,
        rel_height=0.445
    )

    settings_button = ImageButton(
        image_path=SETTING_PATH,
        rel_x=0.173,
        rel_y=0.563,
        rel_width=0.24,
        rel_height=0.24
    )

    quit_button = ImageButton(
        image_path=QUIT_IMAGE,
        action=quit_game,
        rel_x=0.036,
        rel_y=0.612,
        rel_width=0.125,
        rel_height=0.192
    )

    buttons = [new_game_button, settings_button, quit_button]

    while not game_started:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                background = scale_background(or_m_background, width, height)
                for button in buttons:
                    button.update_rect(width, height)

            for button in buttons:
                button.handle_event(event)

        if background:
            screen.blit(background, (0, 0))
        else:
            screen.fill(BLACK)

        for button in buttons:
            button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


def show_menu(screen, clock):
    splash_screen(screen, clock)