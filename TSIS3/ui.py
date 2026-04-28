"""ui.py — All non-gameplay screens for TSIS 3 Racer"""

import pygame
from persistence import (
    load_settings, save_settings, load_leaderboard,
    DIFFICULTY_PARAMS,
)

# ─── Palette ─────────────────────────────────────────────────────────────────
BG       = (12,  12,  20)
PANEL    = (22,  22,  36)
ACCENT   = (0,  200, 255)
ACCENT2  = (255, 180,  0)
GREEN    = (60,  220, 100)
RED      = (220,  60,  60)
GRAY     = (110, 110, 130)
WHITE    = (230, 230, 240)
DARK     = (8,    8,  16)

CAR_COLORS = [
    ("Cyan",   (0,   200, 255)),
    ("Red",    (220,  60,  60)),
    ("Green",  (60,  220, 100)),
    ("Yellow", (255, 220,  40)),
    ("Purple", (180,  80, 220)),
    ("White",  (230, 230, 240)),
]


# ─── Reusable button ─────────────────────────────────────────────────────────
class Button:
    def __init__(self, rect, label, color=ACCENT, text_color=DARK, font=None):
        self.rect       = pygame.Rect(rect)
        self.label      = label
        self.color      = color
        self.text_color = text_color
        self.font       = font
        self._hovered   = False

    def draw(self, screen, font=None):
        f = self.font or font
        col = tuple(min(255, c + 30) for c in self.color) if self._hovered else self.color
        pygame.draw.rect(screen, col, self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=8)
        lbl = f.render(self.label, True, self.text_color)
        screen.blit(lbl, lbl.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self._hovered = self.rect.collidepoint(mouse_pos)

    def clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ─── Helper: draw starfield background ───────────────────────────────────────
def draw_bg(screen, stars):
    screen.fill(BG)
    for sx, sy, br in stars:
        pygame.draw.circle(screen, (br, br, br), (sx, sy), 1)


def make_stars(w, h, n=120):
    import random
    return [(random.randint(0, w), random.randint(0, h),
             random.randint(60, 180)) for _ in range(n)]


# ─── Title ───────────────────────────────────────────────────────────────────
def draw_title(screen, font_title, font_sub, text, sub, W):
    t = font_title.render(text, True, ACCENT)
    screen.blit(t, t.get_rect(centerx=W // 2, y=36))
    if sub:
        s = font_sub.render(sub, True, GRAY)
        screen.blit(s, s.get_rect(centerx=W // 2, y=100))


# ═══════════════════════════════════════════════════════════════════════════════
# Username Entry Screen
# ═══════════════════════════════════════════════════════════════════════════════
class UsernameScreen:
    def __init__(self, W, H, settings):
        self.W, self.H = W, H
        self.settings  = settings
        self.text      = settings.get("username", "")
        self.stars     = make_stars(W, H)
        self._init_fonts()
        self.btn_ok = Button((W // 2 - 100, H // 2 + 60, 200, 44),
                             "START", GREEN, DARK)

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont("Consolas", 52, bold=True)
        self.font_lbl   = pygame.font.SysFont("Consolas", 26, bold=True)
        self.font_input = pygame.font.SysFont("Consolas", 30)
        self.font_btn   = pygame.font.SysFont("Consolas", 20, bold=True)

    def handle(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.text.strip():
                return "done"
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 16 and event.unicode.isprintable():
                self.text += event.unicode
        if self.btn_ok.clicked(event) and self.text.strip():
            return "done"
        return None

    def draw(self, screen):
        draw_bg(screen, self.stars)
        draw_title(screen, self.font_title, self.font_lbl,
                   "TURBO RACER", "Enter your name to start", self.W)

        self.btn_ok.update(pygame.mouse.get_pos())

        # Input box
        box = pygame.Rect(self.W // 2 - 160, self.H // 2 - 20, 320, 50)
        pygame.draw.rect(screen, PANEL, box, border_radius=6)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=6)
        name_surf = self.font_input.render(self.text + "_", True, WHITE)
        screen.blit(name_surf, name_surf.get_rect(midleft=(box.x + 12, box.centery)))

        lbl = self.font_lbl.render("Your Name:", True, GRAY)
        screen.blit(lbl, (box.x, box.y - 34))

        self.btn_ok.draw(screen, self.font_btn)

    @property
    def username(self):
        return self.text.strip() or "Player"


# ═══════════════════════════════════════════════════════════════════════════════
# Main Menu
# ═══════════════════════════════════════════════════════════════════════════════
class MainMenu:
    def __init__(self, W, H, settings):
        self.W, self.H = W, H
        self.settings  = settings
        self.stars     = make_stars(W, H)
        self._init_fonts()
        cx = W // 2
        self.buttons = {
            "play":        Button((cx - 120, 200, 240, 50), "▶  PLAY",        GREEN,  DARK),
            "leaderboard": Button((cx - 120, 270, 240, 50), "🏆  LEADERBOARD", ACCENT, DARK),
            "settings":    Button((cx - 120, 340, 240, 50), "⚙  SETTINGS",    ACCENT2,DARK),
            "quit":        Button((cx - 120, 410, 240, 50), "✕  QUIT",         RED,    WHITE),
        }

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont("Consolas", 56, bold=True)
        self.font_sub   = pygame.font.SysFont("Consolas", 22)
        self.font_btn   = pygame.font.SysFont("Consolas", 20, bold=True)

    def handle(self, event):
        for name, btn in self.buttons.items():
            if btn.clicked(event):
                return name
        return None

    def draw(self, screen):
        draw_bg(screen, self.stars)
        draw_title(screen, self.font_title, self.font_sub,
                   "TURBO RACER",
                   f"Welcome, {self.settings.get('username','Player')}!", self.W)
        mouse = pygame.mouse.get_pos()
        for btn in self.buttons.values():
            btn.update(mouse)
            btn.draw(screen, self.font_btn)


# ═══════════════════════════════════════════════════════════════════════════════
# Settings Screen
# ═══════════════════════════════════════════════════════════════════════════════
class SettingsScreen:
    def __init__(self, W, H, settings):
        self.W, self.H = W, H
        self.settings  = dict(settings)   # work on a copy
        self.stars     = make_stars(W, H)
        self._car_idx  = self._find_car_idx()
        self._diff_idx = ["easy", "normal", "hard"].index(
            self.settings.get("difficulty", "normal"))
        self._init_fonts()
        cx = W // 2
        self.btn_back  = Button((cx - 110, H - 90, 220, 46), "← BACK & SAVE", ACCENT, DARK)
        self.btn_sound = Button((cx + 20,  210, 140, 38), "", GREEN, DARK)
        self.btn_car_l = Button((cx - 180, 290, 40, 38), "<", GRAY, WHITE)
        self.btn_car_r = Button((cx + 140, 290, 40, 38), ">", GRAY, WHITE)
        self.btn_dif_l = Button((cx - 180, 370, 40, 38), "<", GRAY, WHITE)
        self.btn_dif_r = Button((cx + 140, 370, 40, 38), ">", GRAY, WHITE)

    def _find_car_idx(self):
        cc = self.settings.get("car_color", [0, 200, 255])
        for i, (_, c) in enumerate(CAR_COLORS):
            if list(c) == list(cc):
                return i
        return 0

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont("Consolas", 46, bold=True)
        self.font_lbl   = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_val   = pygame.font.SysFont("Consolas", 22)
        self.font_btn   = pygame.font.SysFont("Consolas", 18, bold=True)

    def handle(self, event):
        if self.btn_back.clicked(event):
            self._apply()
            save_settings(self.settings)
            return "back"
        if self.btn_sound.clicked(event):
            self.settings["sound"] = not self.settings.get("sound", False)
        if self.btn_car_l.clicked(event):
            self._car_idx = (self._car_idx - 1) % len(CAR_COLORS)
        if self.btn_car_r.clicked(event):
            self._car_idx = (self._car_idx + 1) % len(CAR_COLORS)
        if self.btn_dif_l.clicked(event):
            self._diff_idx = (self._diff_idx - 1) % 3
        if self.btn_dif_r.clicked(event):
            self._diff_idx = (self._diff_idx + 1) % 3
        return None

    def _apply(self):
        self.settings["car_color"]  = list(CAR_COLORS[self._car_idx][1])
        self.settings["difficulty"] = ["easy", "normal", "hard"][self._diff_idx]

    def draw(self, screen):
        draw_bg(screen, self.stars)
        cx = self.W // 2
        draw_title(screen, self.font_title, self.font_val,
                   "SETTINGS", "", self.W)

        mouse = pygame.mouse.get_pos()
        for btn in (self.btn_back, self.btn_sound,
                    self.btn_car_l, self.btn_car_r,
                    self.btn_dif_l, self.btn_dif_r):
            btn.update(mouse)

        # Sound toggle
        sound_on = self.settings.get("sound", False)
        self.btn_sound.label = "ON ♪" if sound_on else "OFF ✕"
        self.btn_sound.color = GREEN if sound_on else RED
        lbl = self.font_lbl.render("Sound:", True, WHITE)
        screen.blit(lbl, (cx - 180, 218))
        self.btn_sound.draw(screen, self.font_btn)

        # Car color
        name, color = CAR_COLORS[self._car_idx]
        lbl2 = self.font_lbl.render("Car Color:", True, WHITE)
        screen.blit(lbl2, (cx - 180, 298))
        # Swatch
        swatch = pygame.Rect(cx - 60, 295, 120, 36)
        pygame.draw.rect(screen, color, swatch, border_radius=6)
        pygame.draw.rect(screen, WHITE, swatch, 1, border_radius=6)
        cn = self.font_val.render(name, True, DARK)
        screen.blit(cn, cn.get_rect(center=swatch.center))
        self.btn_car_l.draw(screen, self.font_btn)
        self.btn_car_r.draw(screen, self.font_btn)

        # Difficulty
        diff_name = ["easy", "normal", "hard"][self._diff_idx].upper()
        diff_col  = [GREEN, ACCENT2, RED][self._diff_idx]
        lbl3 = self.font_lbl.render("Difficulty:", True, WHITE)
        screen.blit(lbl3, (cx - 180, 378))
        dbox = pygame.Rect(cx - 60, 375, 120, 36)
        pygame.draw.rect(screen, PANEL, dbox, border_radius=6)
        pygame.draw.rect(screen, diff_col, dbox, 2, border_radius=6)
        dn = self.font_val.render(diff_name, True, diff_col)
        screen.blit(dn, dn.get_rect(center=dbox.center))
        self.btn_dif_l.draw(screen, self.font_btn)
        self.btn_dif_r.draw(screen, self.font_btn)

        self.btn_back.draw(screen, self.font_btn)

    @property
    def result_settings(self):
        self._apply()
        return self.settings


# ═══════════════════════════════════════════════════════════════════════════════
# Leaderboard Screen
# ═══════════════════════════════════════════════════════════════════════════════
class LeaderboardScreen:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.stars     = make_stars(W, H)
        self.entries   = load_leaderboard()
        self._init_fonts()
        self.btn_back  = Button((W // 2 - 100, H - 80, 200, 44), "← BACK", ACCENT, DARK)

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont("Consolas", 44, bold=True)
        self.font_hdr   = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_row   = pygame.font.SysFont("Consolas", 17)
        self.font_btn   = pygame.font.SysFont("Consolas", 18, bold=True)

    def handle(self, event):
        if self.btn_back.clicked(event):
            return "back"
        return None

    def draw(self, screen):
        draw_bg(screen, self.stars)
        cx = self.W // 2
        t = self.font_title.render("LEADERBOARD", True, ACCENT2)
        screen.blit(t, t.get_rect(centerx=cx, y=28))

        # Header
        cols = [50, 140, 340, 440, 540]
        hdrs = ["#", "NAME", "SCORE", "DIST", "COINS"]
        y0 = 90
        for hdr, x in zip(hdrs, cols):
            h = self.font_hdr.render(hdr, True, GRAY)
            screen.blit(h, (x, y0))
        pygame.draw.line(screen, GRAY, (40, y0 + 24), (self.W - 40, y0 + 24))

        if not self.entries:
            no = self.font_row.render("No scores yet — play the game!", True, GRAY)
            screen.blit(no, no.get_rect(centerx=cx, y=160))
        else:
            for i, e in enumerate(self.entries):
                row_y  = y0 + 36 + i * 36
                row_col = ACCENT2 if i == 0 else WHITE
                bg_col  = (30, 28, 8) if i == 0 else PANEL
                pygame.draw.rect(screen, bg_col,
                                 (40, row_y - 4, self.W - 80, 30), border_radius=4)
                vals = [str(e.get("rank", i+1)),
                        e.get("name","?")[:12],
                        str(e.get("score", 0)),
                        f"{e.get('distance', 0)}m",
                        str(e.get("coins", 0))]
                for val, x in zip(vals, cols):
                    s = self.font_row.render(val, True, row_col)
                    screen.blit(s, (x, row_y))

        self.btn_back.update(pygame.mouse.get_pos())
        self.btn_back.draw(screen, self.font_btn)


# ═══════════════════════════════════════════════════════════════════════════════
# Game Over Screen
# ═══════════════════════════════════════════════════════════════════════════════
class GameOverScreen:
    def __init__(self, W, H, score, distance, coins, username):
        self.W, self.H   = W, H
        self.score       = score
        self.distance    = distance
        self.coins       = coins
        self.username    = username
        self.stars       = make_stars(W, H)
        self._init_fonts()
        cx = W // 2
        self.btn_retry = Button((cx - 130, H - 130, 240, 50), "↺  RETRY",     GREEN,  DARK)
        self.btn_menu  = Button((cx - 130, H -  70, 240, 50), "⌂  MAIN MENU", ACCENT, DARK)

    def _init_fonts(self):
        self.font_title = pygame.font.SysFont("Consolas", 52, bold=True)
        self.font_lbl   = pygame.font.SysFont("Consolas", 24, bold=True)
        self.font_val   = pygame.font.SysFont("Consolas", 22)
        self.font_btn   = pygame.font.SysFont("Consolas", 20, bold=True)

    def handle(self, event):
        if self.btn_retry.clicked(event):
            return "retry"
        if self.btn_menu.clicked(event):
            return "menu"
        return None

    def draw(self, screen):
        draw_bg(screen, self.stars)
        cx = self.W // 2

        t = self.font_title.render("GAME OVER", True, RED)
        screen.blit(t, t.get_rect(centerx=cx, y=50))

        # Stats panel
        panel = pygame.Rect(cx - 170, 130, 340, 200)
        pygame.draw.rect(screen, PANEL, panel, border_radius=10)
        pygame.draw.rect(screen, ACCENT, panel, 2, border_radius=10)

        stats = [
            ("Player",   self.username),
            ("Score",    str(self.score)),
            ("Distance", f"{self.distance} m"),
            ("Coins",    str(self.coins)),
        ]
        for i, (key, val) in enumerate(stats):
            ky = self.font_lbl.render(key + ":", True, GRAY)
            vl = self.font_val.render(val,       True, WHITE)
            y  = panel.y + 20 + i * 44
            screen.blit(ky, (panel.x + 20, y))
            screen.blit(vl, (panel.right - vl.get_width() - 20, y))

        mouse = pygame.mouse.get_pos()
        for btn in (self.btn_retry, self.btn_menu):
            btn.update(mouse)
            btn.draw(screen, self.font_btn)