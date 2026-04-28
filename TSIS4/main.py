import sys
import os
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, FPS,
    BLACK, WHITE, GRAY, DARK_GRAY, LIGHT_GRAY,
    RED, GREEN, BLUE, YELLOW, ORANGE, CYAN, TEAL, GOLD,
    FONT_SMALL, FONT_MEDIUM, FONT_LARGE, FONT_XLARGE,
    BUTTON_COLOR, BUTTON_HOVER, BUTTON_TEXT,
    BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_RADIUS,
)
from game import SnakeGame
from db import save_score, get_leaderboard, get_personal_best
from settings_manager import load_settings, save_settings



class Button:
    def __init__(self, x, y, w, h, text, color=BUTTON_COLOR, hover_color=BUTTON_HOVER):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.hovered = False

    def draw(self, surface):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=BUTTON_RADIUS)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=BUTTON_RADIUS)
        font = pygame.font.SysFont(None, FONT_MEDIUM)
        txt = font.render(self.text, True, BUTTON_TEXT)
        tx = self.rect.centerx - txt.get_width() // 2
        ty = self.rect.centery - txt.get_height() // 2
        surface.blit(txt, (tx, ty))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)


def draw_text_centered(surface, text, y, size=FONT_MEDIUM, color=WHITE):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    x = SCREEN_WIDTH // 2 - txt.get_width() // 2
    surface.blit(txt, (x, y))


def draw_text(surface, text, x, y, size=FONT_SMALL, color=WHITE):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))



class MainMenu:
    def __init__(self):
        cx = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        self.buttons = [
            Button(cx, 280, BUTTON_WIDTH, BUTTON_HEIGHT, "Play"),
            Button(cx, 350, BUTTON_WIDTH, BUTTON_HEIGHT, "Leaderboard"),
            Button(cx, 420, BUTTON_WIDTH, BUTTON_HEIGHT, "Settings"),
            Button(cx, 490, BUTTON_WIDTH, BUTTON_HEIGHT, "Quit", RED, (255, 80, 80)),
        ]
        self.username = ""
        self.active_field = True
        self.cursor_blink = 0
        self.personal_best = None

    def enter(self, username=""):
        self.username = username
        self.personal_best = get_personal_best(username) if username else None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active_field:
            if event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.key == pygame.K_RETURN:
                if self.username.strip():
                    return "play"
            elif len(self.username) < 15 and event.unicode.isprintable() and event.unicode != " ":
                self.username += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.buttons[0].clicked(pos) and self.username.strip():
                return "play"
            elif self.buttons[1].clicked(pos):
                return "leaderboard"
            elif self.buttons[2].clicked(pos):
                return "settings"
            elif self.buttons[3].clicked(pos):
                return "quit"
        return None

    def update(self):
        mouse = pygame.mouse.get_pos()
        for b in self.buttons:
            b.update(mouse)
        self.cursor_blink = (self.cursor_blink + 1) % 60

    def draw(self, surface):
        surface.fill(DARK_GRAY)

       
        draw_text_centered(surface, "SNAKE", 60, FONT_XLARGE, GREEN)
        draw_text_centered(surface, "GAME", 120, FONT_XLARGE, TEAL)

       
        pygame.draw.line(surface, TEAL, (SCREEN_WIDTH // 2 - 120, 190), (SCREEN_WIDTH // 2 + 120, 190), 2)

        
        draw_text_centered(surface, "Enter Username", 210, FONT_SMALL, LIGHT_GRAY)
        input_rect = pygame.Rect(SCREEN_WIDTH // 2 - 120, 235, 240, 36)
        pygame.draw.rect(surface, GRAY, input_rect, border_radius=6)
        pygame.draw.rect(surface, TEAL if self.active_field else LIGHT_GRAY, input_rect, 2, border_radius=6)

        display_name = self.username
        if self.active_field and self.cursor_blink < 30:
            display_name += "|"
        font = pygame.font.SysFont(None, FONT_MEDIUM)
        txt = font.render(display_name, True, WHITE)
        surface.blit(txt, (input_rect.x + 10, input_rect.y + 6))

      
        if self.personal_best is not None:
            draw_text_centered(surface, f"Personal Best: {self.personal_best}", 540, FONT_SMALL, GOLD)

        for b in self.buttons:
            b.draw(surface)


class GameOverScreen:
    def __init__(self):
        cx = SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2
        self.buttons = [
            Button(cx, 380, BUTTON_WIDTH, BUTTON_HEIGHT, "Retry"),
            Button(cx, 450, BUTTON_WIDTH, BUTTON_HEIGHT, "Main Menu", LIGHT_GRAY, (130, 130, 130)),
        ]
        self.score = 0
        self.level = 0
        self.personal_best = 0
        self.username = ""
        self.saved = False

    def enter(self, score, level, username):
        self.score = score
        self.level = level
        self.username = username
        self.saved = False
        self.personal_best = get_personal_best(username) or 0
        if score > self.personal_best:
            self.personal_best = score
        save_score(username, score, level)
        self.saved = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            if self.buttons[0].clicked(pos):
                return "retry"
            elif self.buttons[1].clicked(pos):
                return "menu"
        return None

    def update(self):
        mouse = pygame.mouse.get_pos()
        for b in self.buttons:
            b.update(mouse)

    def draw(self, surface):
        surface.fill(DARK_GRAY)

        draw_text_centered(surface, "GAME OVER", 80, FONT_XLARGE, RED)

       
        box = pygame.Rect(SCREEN_WIDTH // 2 - 160, 170, 320, 180)
        pygame.draw.rect(surface, GRAY, box, border_radius=10)
        pygame.draw.rect(surface, LIGHT_GRAY, box, 2, border_radius=10)

        draw_text_centered(surface, f"Score: {self.score}", 190, FONT_LARGE, WHITE)
        draw_text_centered(surface, f"Level: {self.level}", 240, FONT_MEDIUM, TEAL)
        draw_text_centered(surface, f"Personal Best: {self.personal_best}", 290, FONT_MEDIUM, GOLD)

        if self.saved:
            draw_text_centered(surface, "Score saved!", 330, FONT_SMALL, GREEN)

        for b in self.buttons:
            b.draw(surface)


class LeaderboardScreen:
    def __init__(self):
        self.back_btn = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 520, BUTTON_WIDTH, BUTTON_HEIGHT, "Back")
        self.entries = []
        self.loaded = False

    def enter(self):
        self.entries = get_leaderboard()
        self.loaded = True

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.back_btn.clicked(pygame.mouse.get_pos()):
                return "back"
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "back"
        return None

    def update(self):
        self.back_btn.update(pygame.mouse.get_pos())

    def draw(self, surface):
        surface.fill(DARK_GRAY)

        draw_text_centered(surface, "LEADERBOARD", 30, FONT_LARGE, GOLD)


        y = 80
        header_font = pygame.font.SysFont(None, FONT_SMALL)
        cols = [("#", 60), ("Username", 160), ("Score", 380), ("Level", 500), ("Date", 600)]
        for label, x in cols:
            txt = header_font.render(label, True, TEAL)
            surface.blit(txt, (x, y))

        pygame.draw.line(surface, LIGHT_GRAY, (40, y + 25), (SCREEN_WIDTH - 40, y + 25), 1)

      
        row_font = pygame.font.SysFont(None, FONT_SMALL)
        for i, entry in enumerate(self.entries[:10]):
            ry = y + 35 + i * 36
            color = GOLD if i == 0 else WHITE
            username = entry.get("username", "???")[:12]
            score = str(entry.get("score", 0))
            level = str(entry.get("level_reached", 0))
            played = entry.get("played_at", "")[:10]

            txt_rank = row_font.render(str(i + 1), True, color)
            txt_name = row_font.render(username, True, color)
            txt_score = row_font.render(score, True, color)
            txt_level = row_font.render(level, True, color)
            txt_date = row_font.render(played, True, LIGHT_GRAY)

            surface.blit(txt_rank, (70, ry))
            surface.blit(txt_name, (160, ry))
            surface.blit(txt_score, (390, ry))
            surface.blit(txt_level, (510, ry))
            surface.blit(txt_date, (590, ry))

            if i < 9:
                pygame.draw.line(surface, (40, 40, 40), (40, ry + 30), (SCREEN_WIDTH - 40, ry + 30), 1)

        if not self.entries:
            draw_text_centered(surface, "No scores yet!", 250, FONT_MEDIUM, LIGHT_GRAY)

        self.back_btn.draw(surface)


class SettingsScreen:
    def __init__(self):
        self.settings = load_settings()
        self.back_btn = Button(SCREEN_WIDTH // 2 - BUTTON_WIDTH // 2, 480, BUTTON_WIDTH, BUTTON_HEIGHT, "Save & Back")
        self.color_options = [
            ((0, 200, 0), "Green"),
            ((0, 150, 255), "Blue"),
            ((255, 100, 0), "Orange"),
            ((200, 0, 200), "Pink"),
            ((255, 255, 0), "Yellow"),
            ((0, 220, 220), "Cyan"),
        ]
        self.selected_color_idx = 0
        for i, (c, _) in enumerate(self.color_options):
            if list(c) == self.settings["snake_color"]:
                self.selected_color_idx = i
                break

    def enter(self):
        self.settings = load_settings()
        for i, (c, _) in enumerate(self.color_options):
            if list(c) == self.settings["snake_color"]:
                self.selected_color_idx = i
                break

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()

           
            grid_rect = pygame.Rect(300, 180, 60, 30)
            if grid_rect.collidepoint(pos):
                self.settings["grid_overlay"] = not self.settings["grid_overlay"]

      
            sound_rect = pygame.Rect(300, 240, 60, 30)
            if sound_rect.collidepoint(pos):
                self.settings["sound"] = not self.settings["sound"]

            for i, (color, name) in enumerate(self.color_options):
                cx = 160 + i * 80
                cy = 340
                if pygame.Rect(cx - 20, cy - 20, 40, 40).collidepoint(pos):
                    self.selected_color_idx = i
                    self.settings["snake_color"] = list(color)

            if self.back_btn.clicked(pos):
                save_settings(self.settings)
                return "back"

        return None

    def update(self):
        self.back_btn.update(pygame.mouse.get_pos())

    def draw(self, surface):
        surface.fill(DARK_GRAY)

        draw_text_centered(surface, "SETTINGS", 40, FONT_LARGE, TEAL)

        draw_text(surface, "Grid Overlay:", 160, 185, FONT_MEDIUM, WHITE)
        grid_val = self.settings.get("grid_overlay", True)
        toggle_rect = pygame.Rect(300, 180, 60, 30)
        pygame.draw.rect(surface, GREEN if grid_val else RED, toggle_rect, border_radius=15)
        knob_x = 330 if grid_val else 300
        pygame.draw.circle(surface, WHITE, (knob_x + 15, 195), 12)
        draw_text(surface, "ON" if grid_val else "OFF", 375, 185, FONT_SMALL, GREEN if grid_val else RED)

        draw_text(surface, "Sound:", 160, 245, FONT_MEDIUM, WHITE)
        sound_val = self.settings.get("sound", True)
        sound_rect = pygame.Rect(300, 240, 60, 30)
        pygame.draw.rect(surface, GREEN if sound_val else RED, sound_rect, border_radius=15)
        knob_x = 330 if sound_val else 300
        pygame.draw.circle(surface, WHITE, (knob_x + 15, 255), 12)
        draw_text(surface, "ON" if sound_val else "OFF", 375, 245, FONT_SMALL, GREEN if sound_val else RED)

        # Snake color
        draw_text(surface, "Snake Color:", 160, 305, FONT_MEDIUM, WHITE)
        for i, (color, name) in enumerate(self.color_options):
            cx = 160 + i * 80
            cy = 340
            rect = pygame.Rect(cx - 20, cy - 20, 40, 40)
            pygame.draw.rect(surface, color, rect, border_radius=6)
            if i == self.selected_color_idx:
                pygame.draw.rect(surface, WHITE, rect, 3, border_radius=6)
            draw_text(surface, name, cx - 20, cy + 28, 18, LIGHT_GRAY)

        # Preview
        draw_text_centered(surface, "Preview", 420, FONT_SMALL, LIGHT_GRAY)
        preview_y = 445
        for i in range(5):
            x = SCREEN_WIDTH // 2 - 50 + i * CELL_SIZE
            c = self.color_options[self.selected_color_idx][0] if i > 0 else (0, 255, 0)
            pygame.draw.rect(surface, c, (x, preview_y, CELL_SIZE, CELL_SIZE))

        self.back_btn.draw(surface)



def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Snake Game")
    clock = pygame.time.Clock()

    settings = load_settings()

    menu = MainMenu()
    game_over_screen = GameOverScreen()
    leaderboard_screen = LeaderboardScreen()
    settings_screen = SettingsScreen()

    state = "menu"
    game = None
    username = ""
    last_move_tick = 0

    menu.enter("")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            if state == "menu":
                result = menu.handle_event(event)
                if result == "play":
                    username = menu.username.strip()
                    game = SnakeGame(tuple(settings["snake_color"]))
                    last_move_tick = pygame.time.get_ticks()
                    state = "playing"
                elif result == "leaderboard":
                    leaderboard_screen.enter()
                    state = "leaderboard"
                elif result == "settings":
                    settings_screen.enter()
                    state = "settings"
                elif result == "quit":
                    running = False

            elif state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        state = "menu"
                        menu.enter(username)
                    else:
                        game.handle_input(event.key)

            elif state == "game_over":
                result = game_over_screen.handle_event(event)
                if result == "retry":
                    game = SnakeGame(tuple(settings["snake_color"]))
                    last_move_tick = pygame.time.get_ticks()
                    state = "playing"
                elif result == "menu":
                    state = "menu"
                    menu.enter(username)

            elif state == "leaderboard":
                result = leaderboard_screen.handle_event(event)
                if result == "back":
                    state = "menu"
                    menu.enter(username)

            elif state == "settings":
                result = settings_screen.handle_event(event)
                if result == "back":
                    settings = load_settings()
                    state = "menu"
                    menu.enter(username)

        if not running:
            break

        if state == "menu":
            menu.update()
        elif state == "playing":
            now = pygame.time.get_ticks()
            move_interval = 1000 // game.get_current_speed()
            if now - last_move_tick >= move_interval:
                game.update()
                last_move_tick = now
                if game.game_over:
                    game_over_screen.enter(game.score, game.level, username)
                    state = "game_over"
        elif state == "game_over":
            game_over_screen.update()
        elif state == "leaderboard":
            leaderboard_screen.update()
        elif state == "settings":
            settings_screen.update()

        if state == "menu":
            menu.draw(screen)
        elif state == "playing":
            game.draw(screen, grid_overlay=settings.get("grid_overlay", True))
            font = pygame.font.SysFont(None, FONT_MEDIUM)
            hud = font.render(f"Score: {game.score}  Level: {game.level}", True, WHITE)
            screen.blit(hud, (10, 10))
            if username:
                name_font = pygame.font.SysFont(None, FONT_SMALL)
                name_txt = name_font.render(f"Player: {username}", True, LIGHT_GRAY)
                screen.blit(name_txt, (SCREEN_WIDTH - name_txt.get_width() - 10, 10))
            pb = get_personal_best(username) if username else None
            if pb is not None:
                pb_font = pygame.font.SysFont(None, FONT_SMALL)
                pb_txt = pb_font.render(f"Best: {pb}", True, GOLD)
                screen.blit(pb_txt, (SCREEN_WIDTH - pb_txt.get_width() - 10, 32))
        elif state == "game_over":
            game_over_screen.draw(screen)
        elif state == "leaderboard":
            leaderboard_screen.draw(screen)
        elif state == "settings":
            settings_screen.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
