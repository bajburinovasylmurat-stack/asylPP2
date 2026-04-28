"""racer.py — Core gameplay for TSIS 3 Racer"""

import pygame
import random
import math
from persistence import DIFFICULTY_PARAMS

# ─── Dimensions ──────────────────────────────────────────────────────────────
WIDTH         = 500
HEIGHT        = 650
ROAD_LEFT     = 60
ROAD_RIGHT    = 440
ROAD_W        = ROAD_RIGHT - ROAD_LEFT
NUM_LANES     = 4
LANE_W        = ROAD_W // NUM_LANES

# ─── Colours ─────────────────────────────────────────────────────────────────
C_BG          = (15,  15,  22)
C_ROAD        = (40,  40,  50)
C_LANE_LINE   = (80,  80,  90)
C_DASH        = (220, 200,  60)
C_KERB_A      = (200,  30,  30)
C_KERB_B      = (230, 230, 230)
C_COIN        = (255, 215,   0)
C_NITRO       = (80,  160, 255)
C_SHIELD      = (100, 255, 140)
C_REPAIR      = (255, 120,  80)
C_OIL         = (30,   30,  50)
C_BOOST       = (80,  200, 255)
C_BARRIER     = (220,  60,  60)
C_TRAFFIC     = [(200,  60,  60), (60, 200, 120), (200, 180,  40),
                 (180,  80, 220), (60, 160, 200)]
C_HUD_BG      = (10,  10,  18, 180)
C_WHITE       = (230, 230, 240)
C_GRAY        = (110, 110, 130)
C_ACCENT      = (0,   200, 255)
C_GREEN       = (60,  220, 100)
C_RED         = (220,  60,  60)


def lane_center(lane):
    return ROAD_LEFT + lane * LANE_W + LANE_W // 2


# ═══════════════════════════════════════════════════════════════════════════════
# Road Scroller
# ═══════════════════════════════════════════════════════════════════════════════
class Road:
    DASH_H     = 30
    DASH_GAP   = 20
    DASH_CYCLE = DASH_H + DASH_GAP
    KERB_W     = 18

    def __init__(self):
        self.offset = 0

    def update(self, speed):
        self.offset = (self.offset + speed) % self.DASH_CYCLE

    def draw(self, screen):
        # Road surface
        pygame.draw.rect(screen, C_ROAD,
                         (ROAD_LEFT, 0, ROAD_W, HEIGHT))
        # Kerbs
        for x in (ROAD_LEFT - self.KERB_W, ROAD_RIGHT):
            for y in range(-self.KERB_W,
                           HEIGHT + self.KERB_W,
                           self.KERB_W * 2):
                oy = (y + int(self.offset)) % (HEIGHT + self.KERB_W * 2) - self.KERB_W
                pygame.draw.rect(screen, C_KERB_A,
                                 (x, oy, self.KERB_W, self.KERB_W))
                pygame.draw.rect(screen, C_KERB_B,
                                 (x, oy + self.KERB_W, self.KERB_W, self.KERB_W))
        # Lane dashes
        for lane in range(1, NUM_LANES):
            lx = ROAD_LEFT + lane * LANE_W
            y  = -self.DASH_CYCLE + self.offset
            while y < HEIGHT:
                pygame.draw.rect(screen, C_LANE_LINE,
                                 (lx - 1, int(y), 2, self.DASH_H))
                y += self.DASH_CYCLE


# ═══════════════════════════════════════════════════════════════════════════════
# Player Car
# ═══════════════════════════════════════════════════════════════════════════════
class PlayerCar:
    W, H     = 36, 60
    SPEED    = 5
    NITRO_S  = 9

    def __init__(self, color):
        self.color      = tuple(color)
        self.x          = WIDTH // 2 - self.W // 2
        self.y          = HEIGHT - 110
        self.nitro_on   = False
        self.shield     = False
        self.invincible = 0   # frames of post-hit invincibility

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def update(self, keys, nitro_active):
        speed = self.NITRO_S if (nitro_active and self.nitro_on) else self.SPEED
        if keys[pygame.K_LEFT]  and self.x > ROAD_LEFT:
            self.x -= speed
        if keys[pygame.K_RIGHT] and self.x < ROAD_RIGHT - self.W:
            self.x += speed
        if self.invincible > 0:
            self.invincible -= 1

    def draw(self, screen):
        r = self.rect
        # Flash when invincible
        if self.invincible > 0 and (self.invincible // 4) % 2:
            return

        # Body
        pygame.draw.rect(screen, self.color, r, border_radius=6)
        # Windshield
        ww, wh = self.W - 8, 16
        pygame.draw.rect(screen, (150, 220, 255),
                         (r.x + 4, r.y + 8, ww, wh), border_radius=3)
        # Wheels
        wc = (20, 20, 20)
        for wx, wy in [(r.x - 4, r.y + 6), (r.right, r.y + 6),
                       (r.x - 4, r.bottom - 20), (r.right, r.bottom - 20)]:
            pygame.draw.rect(screen, wc, (wx, wy, 8, 14), border_radius=2)
        # Shield overlay
        if self.shield:
            s = pygame.Surface((self.W + 12, self.H + 12), pygame.SRCALPHA)
            pygame.draw.ellipse(s, (100, 255, 140, 80),
                                (0, 0, self.W + 12, self.H + 12))
            screen.blit(s, (r.x - 6, r.y - 6))


# ═══════════════════════════════════════════════════════════════════════════════
# Traffic Car
# ═══════════════════════════════════════════════════════════════════════════════
class TrafficCar:
    W, H = 34, 56

    def __init__(self, speed):
        lane      = random.randint(0, NUM_LANES - 1)
        self.x    = lane_center(lane) - self.W // 2
        self.y    = random.randint(-300, -self.H)
        self.speed = speed + random.uniform(-1, 1)
        self.color = random.choice(C_TRAFFIC)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def update(self):
        self.y += self.speed

    def draw(self, screen):
        r = self.rect
        pygame.draw.rect(screen, self.color, r, border_radius=5)
        pygame.draw.rect(screen, (150, 220, 255),
                         (r.x + 4, r.y + 6, r.w - 8, 14), border_radius=3)
        for wx, wy in [(r.x - 4, r.y + 4), (r.right, r.y + 4),
                       (r.x - 4, r.bottom - 18), (r.right, r.bottom - 18)]:
            pygame.draw.rect(screen, (20, 20, 20), (wx, wy, 8, 14), border_radius=2)


# ═══════════════════════════════════════════════════════════════════════════════
# Obstacles  (oil spill, pothole, speed-bump, barrier)
# ═══════════════════════════════════════════════════════════════════════════════
OBS_TYPES = ["oil", "pothole", "barrier", "speedbump"]

class Obstacle:
    def __init__(self, road_speed):
        self.kind  = random.choice(OBS_TYPES)
        lane       = random.randint(0, NUM_LANES - 1)
        cx         = lane_center(lane)
        if self.kind == "oil":
            self.w, self.h = 60, 40
            self.color = C_OIL
        elif self.kind == "pothole":
            self.w, self.h = 32, 32
            self.color = (15, 15, 20)
        elif self.kind == "barrier":
            self.w, self.h = LANE_W - 10, 18
            self.color = C_BARRIER
        else:  # speedbump
            self.w, self.h = LANE_W - 4, 12
            self.color = (180, 140, 40)
        self.x = cx - self.w // 2
        self.y = random.randint(-500, -self.h)
        self.speed = road_speed

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def update(self, road_speed):
        self.y += road_speed

    def draw(self, screen):
        r = self.rect
        if self.kind == "oil":
            pygame.draw.ellipse(screen, self.color, r)
            pygame.draw.ellipse(screen, (50, 50, 80), r, 2)
        elif self.kind == "pothole":
            pygame.draw.ellipse(screen, self.color, r)
        else:
            pygame.draw.rect(screen, self.color, r, border_radius=4)
            pygame.draw.rect(screen, (255, 200, 50), r, 2, border_radius=4)
            lbl = pygame.font.SysFont("Consolas", 11, bold=True).render(
                self.kind.upper(), True, (255, 255, 255))
            screen.blit(lbl, lbl.get_rect(center=r.center))


# ═══════════════════════════════════════════════════════════════════════════════
# Boost Strip  (nitro strip on road)
# ═══════════════════════════════════════════════════════════════════════════════
class BoostStrip:
    W, H = ROAD_W, 20

    def __init__(self):
        self.x = ROAD_LEFT
        self.y = random.randint(-600, -self.H)
        self.active = True

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def update(self, speed):
        self.y += speed

    def draw(self, screen):
        r = self.rect
        pygame.draw.rect(screen, C_BOOST, r)
        for i in range(0, self.W, 40):
            pygame.draw.rect(screen, (255, 255, 255), (self.x + i, r.y, 20, self.H))
        lbl = pygame.font.SysFont("Consolas", 13, bold=True).render(
            "⚡ NITRO BOOST ⚡", True, (10, 10, 10))
        screen.blit(lbl, lbl.get_rect(center=r.center))


# ═══════════════════════════════════════════════════════════════════════════════
# Coins  (weighted values)
# ═══════════════════════════════════════════════════════════════════════════════
COIN_WEIGHTS = [(1, 10), (3, 5), (5, 2), (10, 1)]   # (value, weight)

def _pick_coin_value():
    pool = []
    for val, w in COIN_WEIGHTS:
        pool.extend([val] * w)
    return random.choice(pool)


class Coin:
    def __init__(self, road_speed):
        lane       = random.randint(0, NUM_LANES - 1)
        self.x     = lane_center(lane)
        self.y     = random.randint(-600, -20)
        self.value = _pick_coin_value()
        self.r     = {1: 10, 3: 13, 5: 16, 10: 20}.get(self.value, 10)
        self.speed = road_speed

    @property
    def rect(self):
        return pygame.Rect(self.x - self.r, self.y - self.r,
                           self.r * 2, self.r * 2)

    def update(self, road_speed):
        self.y += road_speed

    def draw(self, screen):
        col = {1: C_COIN, 3: (220, 180, 50),
               5: (100, 220, 100), 10: (100, 200, 255)}.get(self.value, C_COIN)
        pygame.draw.circle(screen, col, (self.x, int(self.y)), self.r)
        pygame.draw.circle(screen, (255, 255, 255), (self.x, int(self.y)), self.r, 1)
        lbl = pygame.font.SysFont("Consolas", max(9, self.r - 3), bold=True).render(
            str(self.value), True, (20, 20, 20))
        screen.blit(lbl, lbl.get_rect(center=(self.x, int(self.y))))


# ═══════════════════════════════════════════════════════════════════════════════
# Power-ups
# ═══════════════════════════════════════════════════════════════════════════════
POWERUP_TTL   = 300   # frames before auto-disappear
POWERUP_TYPES = {
    "nitro":  {"color": C_NITRO,  "label": "⚡", "duration": 240},  # 4s
    "shield": {"color": C_SHIELD, "label": "🛡", "duration": 0},    # until hit
    "repair": {"color": C_REPAIR, "label": "♥",  "duration": 0},    # instant
}

class PowerUp:
    W, H = 32, 32

    def __init__(self, kind, road_speed):
        self.kind    = kind
        self.meta    = POWERUP_TYPES[kind]
        lane         = random.randint(0, NUM_LANES - 1)
        self.x       = lane_center(lane) - self.W // 2
        self.y       = random.randint(-600, -self.H)
        self.ttl     = POWERUP_TTL
        self.speed   = road_speed
        self._font   = pygame.font.SysFont("Segoe UI Emoji", 18)

    @property
    def rect(self):
        return pygame.Rect(self.x, self.y, self.W, self.H)

    def update(self, road_speed):
        self.y    += road_speed
        self.ttl  -= 1

    def draw(self, screen):
        r     = self.rect
        alpha = max(80, int(255 * (self.ttl / POWERUP_TTL)))
        s     = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
        col   = self.meta["color"] + (alpha,)
        pygame.draw.rect(s, col, (0, 0, self.W, self.H), border_radius=6)
        pygame.draw.rect(s, (255, 255, 255, 160), (0, 0, self.W, self.H), 2, border_radius=6)
        screen.blit(s, (r.x, r.y))
        # Label
        lbl_col = self.meta["color"]
        lbl     = self._font.render(self.meta["label"], True, lbl_col)
        screen.blit(lbl, lbl.get_rect(center=r.center))


# ═══════════════════════════════════════════════════════════════════════════════
# HUD
# ═══════════════════════════════════════════════════════════════════════════════
class HUD:
    def __init__(self):
        self.font_sm  = pygame.font.SysFont("Consolas", 16, bold=True)
        self.font_lg  = pygame.font.SysFont("Consolas", 22, bold=True)
        self.font_ico = pygame.font.SysFont("Segoe UI Emoji", 16)

    def draw(self, screen, score, distance, coins, active_pu, pu_timer,
             nitro_active, shield_active, speed, diff):
        # Top bar background
        s = pygame.Surface((WIDTH, 52), pygame.SRCALPHA)
        s.fill((10, 10, 18, 200))
        screen.blit(s, (0, 0))

        # Score & coins
        sc = self.font_lg.render(f"Score: {score}", True, C_ACCENT)
        screen.blit(sc, (8, 6))
        cn = self.font_sm.render(f"🪙 {coins}", True, C_COIN)
        screen.blit(cn, (8, 30))

        # Distance
        dm = self.font_sm.render(f"Dist: {distance}m", True, C_WHITE)
        screen.blit(dm, (WIDTH // 2 - 50, 6))

        # Speed
        sp = self.font_sm.render(f"Spd: {speed:.0f}", True, C_GREEN)
        screen.blit(sp, (WIDTH // 2 - 50, 28))

        # Active power-up
        if active_pu:
            meta = POWERUP_TYPES[active_pu]
            col  = meta["color"]
            if pu_timer > 0:
                sec = pu_timer // 60
                txt = f"{meta['label']} {active_pu.upper()} {sec}s"
            else:
                txt = f"{meta['label']} {active_pu.upper()}"
            pu_surf = self.font_sm.render(txt, True, col)
            screen.blit(pu_surf, (WIDTH - pu_surf.get_width() - 8, 6))

        # Difficulty badge
        dcol  = [C_GREEN, C_ACCENT, C_RED][["easy","normal","hard"].index(diff)]
        d_lbl = self.font_sm.render(diff.upper(), True, dcol)
        screen.blit(d_lbl, (WIDTH - d_lbl.get_width() - 8, 32))


# ═══════════════════════════════════════════════════════════════════════════════
# Main Game Session
# ═══════════════════════════════════════════════════════════════════════════════
class GameSession:
    ROAD_SPEED_BASE   = 5
    ROAD_SPEED_MAX    = 14
    SPEED_SCALE       = 0.002    # +speed per coin
    TRAFFIC_BASE      = 3        # initial traffic cars
    OBSTACLE_INTERVAL = 120      # frames between obstacles
    TRAFFIC_INTERVAL  = 180
    POWERUP_INTERVAL  = 300
    BOOST_INTERVAL    = 600

    def __init__(self, settings):
        self.settings     = settings
        self.diff         = settings.get("difficulty", "normal")
        self.dp           = DIFFICULTY_PARAMS[self.diff]
        self.car_color    = settings.get("car_color", [0, 200, 255])

        # Objects
        self.road         = Road()
        self.player       = PlayerCar(self.car_color)
        self.traffic      = []
        self.obstacles    = []
        self.coins        = []
        self.powerups     = []
        self.boosts       = []

        # State
        self.road_speed   = self.ROAD_SPEED_BASE
        self.score        = 0
        self.coin_count   = 0
        self.distance     = 0
        self.frame        = 0
        self.game_over    = False

        # Power-up state
        self.active_pu    = None   # "nitro" / "shield" / "repair"
        self.pu_timer     = 0

        # Timers
        self.obs_timer    = self.OBSTACLE_INTERVAL
        self.traf_timer   = self.TRAFFIC_INTERVAL
        self.pu_spawn_t   = self.POWERUP_INTERVAL
        self.boost_timer  = self.BOOST_INTERVAL

        self.hud = HUD()

        # Seed initial traffic
        for _ in range(self.TRAFFIC_BASE):
            self.traffic.append(TrafficCar(self.road_speed * 0.6))

        # Seed initial coins
        for _ in range(4):
            self.coins.append(Coin(self.road_speed))

    # ── Spawn helpers ─────────────────────────────────────────────────────────

    def _safe_spawn(self):
        """True if nothing is near the top of the screen (safe to spawn)."""
        py = self.player.y
        for t in self.traffic:
            if t.y > -100 and abs(t.x - self.player.x) < 60 and t.y < py - 200:
                return False
        return True

    def _spawn_traffic(self):
        density = self.dp["traffic_density"]
        count   = max(1, int(density * (1 + self.coin_count * 0.05)))
        count   = min(count, 8)
        for _ in range(count):
            self.traffic.append(
                TrafficCar(self.road_speed * random.uniform(0.5, 0.85))
            )

    def _spawn_obstacle(self):
        freq = self.dp["obstacle_freq"]
        if random.random() < freq * 0.5:
            self.obstacles.append(Obstacle(self.road_speed))

    def _spawn_powerup(self):
        # Only one power-up at a time
        if not self.powerups:
            kind = random.choice(list(POWERUP_TYPES.keys()))
            self.powerups.append(PowerUp(kind, self.road_speed))

    def _spawn_boost(self):
        if not self.boosts:
            self.boosts.append(BoostStrip())

    # ── Collision helpers ─────────────────────────────────────────────────────

    def _hit_traffic(self, t_rect):
        if self.player.invincible > 0:
            return False
        if self.active_pu == "shield":
            self.active_pu = None
            self.player.shield = False
            self.player.invincible = 90
            return False
        return True

    def _hit_obstacle(self, obs):
        if self.player.invincible > 0:
            return False
        if obs.kind == "oil":
            # Slow-down zone — no crash, just slow
            self.road_speed = max(2, self.road_speed - 1.5)
            return False
        if obs.kind == "speedbump":
            self.road_speed = max(2, self.road_speed - 0.5)
            return False
        # barrier / pothole → crash unless shielded
        if self.active_pu == "shield":
            self.active_pu = None
            self.player.shield = False
            self.player.invincible = 90
            return False
        return True

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, keys):
        if self.game_over:
            return

        self.frame    += 1
        self.distance  = self.frame * self.road_speed // 60   # approx metres

        # Speed scale
        target_speed = min(
            self.ROAD_SPEED_MAX,
            self.ROAD_SPEED_BASE + self.coin_count * self.SPEED_SCALE
        )
        if self.road_speed < target_speed:
            self.road_speed += 0.005

        # Nitro boost
        nitro_active = (self.active_pu == "nitro")
        eff_speed    = self.road_speed * (1.6 if nitro_active else 1.0)
        self.player.nitro_on = nitro_active

        # Power-up timer
        if self.active_pu == "nitro" and self.pu_timer > 0:
            self.pu_timer -= 1
            if self.pu_timer <= 0:
                self.active_pu = None
                self.player.nitro_on = False

        # Player
        self.player.update(keys, nitro_active)

        # Road
        self.road.update(eff_speed)
        self.score += int(eff_speed * 0.1)

        # Spawn timers
        self.traf_timer -= 1
        if self.traf_timer <= 0:
            self._spawn_traffic()
            self.traf_timer = max(
                40,
                int(self.TRAFFIC_INTERVAL / self.dp["traffic_density"])
            )

        self.obs_timer -= 1
        if self.obs_timer <= 0:
            self._spawn_obstacle()
            self.obs_timer = max(
                30,
                int(self.OBSTACLE_INTERVAL / self.dp["obstacle_freq"])
            )

        self.pu_spawn_t -= 1
        if self.pu_spawn_t <= 0:
            self._spawn_powerup()
            self.pu_spawn_t = self.POWERUP_INTERVAL

        self.boost_timer -= 1
        if self.boost_timer <= 0:
            self._spawn_boost()
            self.boost_timer = self.BOOST_INTERVAL

        pr = self.player.rect

        # Traffic update & collision
        for t in self.traffic[:]:
            t.update()
            if t.rect.colliderect(pr):
                if self._hit_traffic(t.rect):
                    self.game_over = True
                    return
            if t.y > HEIGHT + 20:
                self.traffic.remove(t)

        # Obstacle update & collision
        for obs in self.obstacles[:]:
            obs.update(eff_speed)
            if obs.rect.colliderect(pr):
                if self._hit_obstacle(obs):
                    self.game_over = True
                    return
                self.obstacles.remove(obs)
            elif obs.y > HEIGHT + 20:
                self.obstacles.remove(obs)

        # Coins
        for coin in self.coins[:]:
            coin.update(eff_speed)
            if coin.rect.colliderect(pr):
                mult   = self.dp["coin_value_mult"]
                gained = int(coin.value * mult * 10)
                self.score      += gained
                self.coin_count += coin.value
                self.coins.remove(coin)
                self.coins.append(Coin(self.road_speed))
            elif coin.y > HEIGHT + 20:
                self.coins.remove(coin)
                self.coins.append(Coin(self.road_speed))

        # Boost strips
        for bs in self.boosts[:]:
            bs.update(eff_speed)
            if bs.rect.colliderect(pr):
                # Trigger nitro for a short burst
                self.active_pu  = "nitro"
                self.pu_timer   = 120
                self.boosts.remove(bs)
            elif bs.y > HEIGHT + 20:
                self.boosts.remove(bs)

        # Power-ups
        for pu in self.powerups[:]:
            pu.update(eff_speed)
            if pu.rect.colliderect(pr):
                self._apply_powerup(pu.kind)
                self.powerups.remove(pu)
            elif pu.ttl <= 0 or pu.y > HEIGHT + 20:
                self.powerups.remove(pu)

    def _apply_powerup(self, kind):
        self.active_pu = kind
        if kind == "nitro":
            self.pu_timer = POWERUP_TYPES["nitro"]["duration"]
        elif kind == "shield":
            self.player.shield  = True
            self.pu_timer = 0
        elif kind == "repair":
            # Clears all current obstacles on screen
            self.obstacles.clear()
            self.active_pu = None   # instant

    # ── Draw ──────────────────────────────────────────────────────────────────

    def draw(self, screen):
        screen.fill(C_BG)
        self.road.draw(screen)

        for bs  in self.boosts:    bs.draw(screen)
        for obs in self.obstacles: obs.draw(screen)
        for coin in self.coins:    coin.draw(screen)
        for pu  in self.powerups:  pu.draw(screen)
        for t   in self.traffic:   t.draw(screen)
        self.player.draw(screen)

        self.hud.draw(
            screen,
            self.score,
            self.distance,
            self.coin_count,
            self.active_pu,
            self.pu_timer,
            self.active_pu == "nitro",
            self.active_pu == "shield",
            self.road_speed,
            self.diff,
        )