import random
import pygame
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, CELL_SIZE, GRID_W, GRID_H,
    FOOD_NORMAL, FOOD_BONUS, FOOD_POISON,
    FOOD_NORMAL_POINTS, FOOD_BONUS_POINTS, FOOD_BONUS_LIFETIME,
    POWERUP_SPEED, POWERUP_SLOW, POWERUP_SHIELD,
    POWERUP_FIELD_LIFETIME, POWERUP_EFFECT_DURATION,
    OBSTACLE_COLOR, OBSTACLE_START_LEVEL, OBSTACLES_PER_LEVEL,
    FOOD_PER_LEVEL, BASE_SPEED, SPEED_INCREMENT,
    SNAKE_HEAD_COLOR, DARK_GRAY,
)


class Food:
    def __init__(self, pos, food_type="normal", points=FOOD_NORMAL_POINTS, color=FOOD_NORMAL, lifetime=None):
        self.pos = pos
        self.food_type = food_type
        self.points = points
        self.color = color
        self.lifetime = lifetime
        self.spawn_tick = pygame.time.get_ticks()

    def is_expired(self):
        if self.lifetime is None:
            return False
        return pygame.time.get_ticks() - self.spawn_tick >= self.lifetime


class PowerUp:
    TYPES = {
        "speed": {"color": POWERUP_SPEED, "label": "S"},
        "slow": {"color": POWERUP_SLOW, "label": "W"},
        "shield": {"color": POWERUP_SHIELD, "label": "X"},
    }

    def __init__(self, pos, ptype):
        self.pos = pos
        self.ptype = ptype
        self.color = self.TYPES[ptype]["color"]
        self.label = self.TYPES[ptype]["label"]
        self.spawn_tick = pygame.time.get_ticks()

    def is_expired(self):
        return pygame.time.get_ticks() - self.spawn_tick >= POWERUP_FIELD_LIFETIME


class SnakeGame:
    def __init__(self, snake_color=(0, 200, 0)):
        self.snake_color = snake_color
        self.reset()

    def reset(self):
        start_x = (GRID_W // 2) * CELL_SIZE
        start_y = (GRID_H // 2) * CELL_SIZE
        self.snake = [
            (start_x, start_y),
            (start_x - CELL_SIZE, start_y),
            (start_x - 2 * CELL_SIZE, start_y),
        ]
        self.dx = CELL_SIZE
        self.dy = 0
        self.score = 0
        self.level = 1
        self.food_eaten = 0
        self.speed = BASE_SPEED
        self.game_over = False
        self.death_reason = ""

        self.foods = []
        self.powerup = None
        self.obstacles = []

        self.active_effects = {}
        self.shield_active = False

        self._spawn_food()
        self._maybe_spawn_bonus_food()

    def _occupied_cells(self):
        cells = set(self.snake)
        for f in self.foods:
            cells.add(f.pos)
        for o in self.obstacles:
            cells.add(o)
        if self.powerup:
            cells.add(self.powerup.pos)
        return cells

    def _random_free_cell(self, occupied=None):
        if occupied is None:
            occupied = self._occupied_cells()
        attempts = 0
        while attempts < 1000:
            x = random.randrange(0, SCREEN_WIDTH, CELL_SIZE)
            y = random.randrange(0, SCREEN_HEIGHT, CELL_SIZE)
            if (x, y) not in occupied:
                return (x, y)
            attempts += 1
        return None

    def _spawn_food(self):
        pos = self._random_free_cell()
        if pos:
            self.foods.append(Food(pos, "normal", FOOD_NORMAL_POINTS, FOOD_NORMAL))

    def _maybe_spawn_bonus_food(self):
        if random.random() < 0.3:
            pos = self._random_free_cell()
            if pos:
                self.foods.append(Food(pos, "bonus", FOOD_BONUS_POINTS, FOOD_BONUS, FOOD_BONUS_LIFETIME))

    def _maybe_spawn_poison_food(self):
        if random.random() < 0.2:
            pos = self._random_free_cell()
            if pos:
                self.foods.append(Food(pos, "poison", 0, FOOD_POISON))

    def _maybe_spawn_powerup(self):
        if self.powerup is not None:
            return
        if random.random() < 0.15:
            pos = self._random_free_cell()
            if pos:
                ptype = random.choice(["speed", "slow", "shield"])
                self.powerup = PowerUp(pos, ptype)

    def _generate_obstacles(self):
        self.obstacles.clear()
        if self.level < OBSTACLE_START_LEVEL:
            return
        count = (self.level - OBSTACLE_START_LEVEL + 1) * OBSTACLES_PER_LEVEL
        occupied = self._occupied_cells()

        safe_zone = set()
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                sx = self.snake[0][0] + dx * CELL_SIZE
                sy = self.snake[0][1] + dy * CELL_SIZE
                safe_zone.add((sx, sy))
        for seg in self.snake:
            safe_zone.add(seg)

        for _ in range(count):
            pos = self._random_free_cell(occupied | safe_zone)
            if pos:
                self.obstacles.append(pos)
                occupied.add(pos)

    def _check_path_exists(self, start, obstacles_set):
        visited = set()
        queue = [start]
        visited.add(start)
        while queue:
            cx, cy = queue.pop(0)
            for ddx, ddy in [(CELL_SIZE, 0), (-CELL_SIZE, 0), (0, CELL_SIZE), (0, -CELL_SIZE)]:
                nx, ny = cx + ddx, cy + ddy
                if 0 <= nx < SCREEN_WIDTH and 0 <= ny < SCREEN_HEIGHT:
                    if (nx, ny) not in visited and (nx, ny) not in obstacles_set:
                        visited.add((nx, ny))
                        queue.append((nx, ny))
        return len(visited)

    def handle_input(self, key):
        if self.game_over:
            return
        if key == pygame.K_UP and self.dy == 0:
            self.dx = 0
            self.dy = -CELL_SIZE
        elif key == pygame.K_DOWN and self.dy == 0:
            self.dx = 0
            self.dy = CELL_SIZE
        elif key == pygame.K_LEFT and self.dx == 0:
            self.dx = -CELL_SIZE
            self.dy = 0
        elif key == pygame.K_RIGHT and self.dx == 0:
            self.dx = CELL_SIZE
            self.dy = 0

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()

        # Expire timed effects
        expired = []
        for effect, end_time in self.active_effects.items():
            if now >= end_time:
                expired.append(effect)
        for effect in expired:
            del self.active_effects[effect]
            if effect == "shield":
                self.shield_active = False

        # Expire bonus/poison foods
        self.foods = [f for f in self.foods if not f.is_expired()]

        # Expire powerup on field
        if self.powerup and self.powerup.is_expired():
            self.powerup = None

        # Move snake
        head_x, head_y = self.snake[0]
        new_head = (head_x + self.dx, head_y + self.dy)

        # Wall collision
        if new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
            if self.shield_active:
                self.shield_active = False
                self.active_effects.pop("shield", None)
                if self.dx != 0:
                    self.dx = -self.dx
                else:
                    self.dy = -self.dy
                new_head = (head_x + self.dx, head_y + self.dy)
                if new_head[0] < 0 or new_head[0] >= SCREEN_WIDTH or new_head[1] < 0 or new_head[1] >= SCREEN_HEIGHT:
                    self.game_over = True
                    self.death_reason = "wall"
                    return
            else:
                self.game_over = True
                self.death_reason = "wall"
                return

        # Self collision
        if new_head in self.snake:
            if self.shield_active:
                self.shield_active = False
                self.active_effects.pop("shield", None)
            else:
                self.game_over = True
                self.death_reason = "self"
                return

        # Obstacle collision
        if new_head in self.obstacles:
            if self.shield_active:
                self.shield_active = False
                self.active_effects.pop("shield", None)
            else:
                self.game_over = True
                self.death_reason = "obstacle"
                return

        self.snake.insert(0, new_head)

        # Check food
        ate = False
        for food in self.foods[:]:
            if new_head == food.pos:
                if food.food_type == "poison":
                    for _ in range(min(2, len(self.snake) - 1)):
                        if len(self.snake) > 1:
                            self.snake.pop()
                    if len(self.snake) <= 1:
                        self.game_over = True
                        self.death_reason = "poison"
                        return
                else:
                    self.score += food.points
                    self.food_eaten += 1
                    ate = True

                    if self.food_eaten % FOOD_PER_LEVEL == 0:
                        self.level += 1
                        self.speed += SPEED_INCREMENT
                        self._generate_obstacles()

                self.foods.remove(food)
                break

        if not ate:
            self.snake.pop()

        # Ensure at least one normal food exists
        has_normal = any(f.food_type == "normal" for f in self.foods)
        if not has_normal:
            self._spawn_food()

        # Maybe spawn bonus/poison
        self._maybe_spawn_bonus_food()
        self._maybe_spawn_poison_food()

        # Maybe spawn powerup
        self._maybe_spawn_powerup()

        # Check powerup collection
        if self.powerup and new_head == self.powerup.pos:
            ptype = self.powerup.ptype
            self.active_effects[ptype] = now + POWERUP_EFFECT_DURATION
            if ptype == "shield":
                self.shield_active = True
            self.powerup = None

    def get_current_speed(self):
        if "speed" in self.active_effects:
            return self.speed + 4
        if "slow" in self.active_effects:
            return max(3, self.speed - 3)
        return self.speed

    def draw(self, surface, grid_overlay=False):
        surface.fill(DARK_GRAY)

        if grid_overlay:
            for x in range(0, SCREEN_WIDTH, CELL_SIZE):
                pygame.draw.line(surface, (40, 40, 40), (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
                pygame.draw.line(surface, (40, 40, 40), (0, y), (SCREEN_WIDTH, y))

        for obs in self.obstacles:
            pygame.draw.rect(surface, OBSTACLE_COLOR, (*obs, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, (80, 80, 80), (*obs, CELL_SIZE, CELL_SIZE), 1)

        for food in self.foods:
            pygame.draw.rect(surface, food.color, (*food.pos, CELL_SIZE, CELL_SIZE))
            if food.food_type == "bonus":
                remaining = max(0, food.lifetime - (pygame.time.get_ticks() - food.spawn_tick))
                ratio = remaining / food.lifetime if food.lifetime else 1
                bar_w = int(CELL_SIZE * ratio)
                pygame.draw.rect(surface, (255, 255, 255), (food.pos[0], food.pos[1] - 4, bar_w, 3))
            elif food.food_type == "poison":
                cx = food.pos[0] + CELL_SIZE // 2
                cy = food.pos[1] + CELL_SIZE // 2
                pygame.draw.line(surface, (255, 255, 255), (cx - 4, cy - 4), (cx + 4, cy + 4), 2)
                pygame.draw.line(surface, (255, 255, 255), (cx + 4, cy - 4), (cx - 4, cy + 4), 2)

        if self.powerup:
            pu = self.powerup
            pygame.draw.rect(surface, pu.color, (*pu.pos, CELL_SIZE, CELL_SIZE))
            font = pygame.font.SysFont(None, 18)
            label = font.render(pu.label, True, (0, 0, 0))
            surface.blit(label, (pu.pos[0] + 4, pu.pos[1] + 2))
            remaining = max(0, POWERUP_FIELD_LIFETIME - (pygame.time.get_ticks() - pu.spawn_tick))
            ratio = remaining / POWERUP_FIELD_LIFETIME
            bar_w = int(CELL_SIZE * ratio)
            pygame.draw.rect(surface, (255, 255, 255), (pu.pos[0], pu.pos[1] - 4, bar_w, 3))

        for i, seg in enumerate(self.snake):
            color = SNAKE_HEAD_COLOR if i == 0 else self.snake_color
            pygame.draw.rect(surface, color, (*seg, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(surface, (0, 0, 0), (*seg, CELL_SIZE, CELL_SIZE), 1)

        if self.shield_active:
            head = self.snake[0]
            pygame.draw.rect(surface, (100, 180, 255), (*head, CELL_SIZE, CELL_SIZE), 2)

        y_offset = 40
        for effect, end_time in self.active_effects.items():
            remaining = max(0, end_time - pygame.time.get_ticks())
            secs = remaining / 1000
            if effect == "speed":
                txt = f"Speed Boost: {secs:.1f}s"
                col = POWERUP_SPEED
            elif effect == "slow":
                txt = f"Slow Motion: {secs:.1f}s"
                col = POWERUP_SLOW
            elif effect == "shield":
                txt = f"Shield: Active"
                col = POWERUP_SHIELD
            else:
                continue
            font = pygame.font.SysFont(None, 22)
            surf = font.render(txt, True, col)
            surface.blit(surf, (10, y_offset))
            y_offset += 22
