"""
TSIS 2 — Paint Application
tools.py  —  All drawing tool logic (shapes, fill, text helpers)
"""

import math
import pygame
from collections import deque


# ──────────────────────────────────────────────────────────────────────────────
# Primitive helpers
# ──────────────────────────────────────────────────────────────────────────────

def draw_thick_line(surface, start, end, width, color):
    """Draw an anti-aliased thick line as a chain of circles."""
    x1, y1 = start
    x2, y2 = end
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(x1 + t * (x2 - x1))
        y = int(y1 + t * (y2 - y1))
        pygame.draw.circle(surface, color, (x, y), width)


# ──────────────────────────────────────────────────────────────────────────────
# Pencil / Freehand
# ──────────────────────────────────────────────────────────────────────────────

def draw_pencil_stroke(surface, p1, p2, color, width):
    """Called on every MOUSEMOTION while left button held."""
    draw_thick_line(surface, p1, p2, width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Straight Line
# ──────────────────────────────────────────────────────────────────────────────

def draw_line(surface, start, end, color, width):
    draw_thick_line(surface, start, end, width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Rectangle
# ──────────────────────────────────────────────────────────────────────────────

def draw_rectangle(surface, start, end, color, width):
    x1, y1 = start
    x2, y2 = end
    pts = [(x1, y1), (x2, y1), (x2, y2), (x1, y2)]
    for i in range(4):
        draw_thick_line(surface, pts[i], pts[(i + 1) % 4], width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Square  (force equal sides)
# ──────────────────────────────────────────────────────────────────────────────

def draw_square(surface, start, end, color, width):
    x1, y1 = start
    dx = end[0] - x1
    dy = end[1] - y1
    side = min(abs(dx), abs(dy))
    sx = int(math.copysign(side, dx))
    sy = int(math.copysign(side, dy))
    draw_rectangle(surface, start, (x1 + sx, y1 + sy), color, width)


# ──────────────────────────────────────────────────────────────────────────────
# Circle
# ──────────────────────────────────────────────────────────────────────────────

def draw_circle(surface, start, end, color, width):
    cx, cy = start
    radius = int(math.hypot(end[0] - cx, end[1] - cy))
    if radius > 0:
        pygame.draw.circle(surface, color, (cx, cy), radius, width)


# ──────────────────────────────────────────────────────────────────────────────
# Right Triangle
# ──────────────────────────────────────────────────────────────────────────────

def draw_right_triangle(surface, start, end, color, width):
    x1, y1 = start
    x2, y2 = end
    pts = [(x1, y2), (x2, y2), (x1, y1)]
    for i in range(3):
        draw_thick_line(surface, pts[i], pts[(i + 1) % 3], width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Equilateral Triangle
# ──────────────────────────────────────────────────────────────────────────────

def draw_equilateral_triangle(surface, start, end, color, width):
    x1, y1 = start
    x2, y2 = end
    base = x2 - x1
    apex_x = x1 + base // 2
    apex_y = int(y2 - abs(base) * math.sqrt(3) / 2)
    pts = [(x1, y2), (x2, y2), (apex_x, apex_y)]
    for i in range(3):
        draw_thick_line(surface, pts[i], pts[(i + 1) % 3], width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Rhombus
# ──────────────────────────────────────────────────────────────────────────────

def draw_rhombus(surface, start, end, color, width):
    x1, y1 = start
    x2, y2 = end
    mx, my = (x1 + x2) // 2, (y1 + y2) // 2
    pts = [(mx, y1), (x2, my), (mx, y2), (x1, my)]
    for i in range(4):
        draw_thick_line(surface, pts[i], pts[(i + 1) % 4], width, color)


# ──────────────────────────────────────────────────────────────────────────────
# Eraser
# ──────────────────────────────────────────────────────────────────────────────

def draw_eraser(surface, pos, bg_color, size):
    half = size * 4
    pygame.draw.rect(surface, bg_color,
                     (pos[0] - half, pos[1] - half, half * 2, half * 2))


# ──────────────────────────────────────────────────────────────────────────────
# Flood Fill  (BFS, exact color match)
# ──────────────────────────────────────────────────────────────────────────────

def flood_fill(surface, pos, fill_color):
    """
    BFS flood-fill on `surface` starting at `pos` with `fill_color`.
    Stops at pixels whose color differs from the seed color.
    """
    x, y = int(pos[0]), int(pos[1])
    w, h = surface.get_size()

    if not (0 <= x < w and 0 <= y < h):
        return

    target_color = surface.get_at((x, y))[:3]   # ignore alpha
    fill_rgb = fill_color[:3]

    if target_color == fill_rgb:
        return  # already that color

    # Lock surface for pixel access
    surface.lock()

    visited = set()
    queue = deque()
    queue.append((x, y))
    visited.add((x, y))

    while queue:
        cx, cy = queue.popleft()
        if surface.get_at((cx, cy))[:3] != target_color:
            continue
        surface.set_at((cx, cy), fill_rgb)

        for nx, ny in ((cx-1, cy), (cx+1, cy), (cx, cy-1), (cx, cy+1)):
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if surface.get_at((nx, ny))[:3] == target_color:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    surface.unlock()


# ──────────────────────────────────────────────────────────────────────────────
# Dispatch helper
# ──────────────────────────────────────────────────────────────────────────────

SHAPE_TOOLS = {
    'rectangle':           draw_rectangle,
    'square':              draw_square,
    'circle':              draw_circle,
    'right_triangle':      draw_right_triangle,
    'equil_triangle':      draw_equilateral_triangle,
    'rhombus':             draw_rhombus,
    'line':                draw_line,
}


def draw_shape(surface, tool, start, end, color, width):
    """Dispatch to the correct shape drawer."""
    fn = SHAPE_TOOLS.get(tool)
    if fn:
        fn(surface, start, end, color, width)