"""
TSIS 2 — Paint Application  (paint.py)
Extends Practice 10 & 11 with:
  • Pencil (freehand) & straight-line tool with live preview
  • Three brush sizes  (keys 1 / 2 / 3)
  • Flood-fill tool
  • Text tool  (click → type → Enter to confirm, Esc to cancel)
  • Ctrl+S  → timestamped .png save
  • All shapes from P10/P11 (rectangle, square, circle,
    right triangle, equilateral triangle, rhombus)
"""

import pygame
import datetime
from tools import (
    draw_pencil_stroke, draw_shape, draw_eraser,
    flood_fill, SHAPE_TOOLS,
)

# ──────────────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────────────

CANVAS_W, CANVAS_H = 900, 620
TOOLBAR_H = 56
WIN_W = CANVAS_W
WIN_H = CANVAS_H + TOOLBAR_H

BG_COLOR      = (255, 255, 255)
TOOLBAR_BG    = (30, 30, 38)
TOOLBAR_LINE  = (60, 60, 72)
ACCENT        = (99, 179, 237)
TEXT_COLOR    = (220, 220, 230)
HOVER_COLOR   = (55, 55, 68)
ACTIVE_COLOR  = (40, 100, 160)

BRUSH_SIZES   = {1: 2, 2: 5, 3: 10}   # key → px radius

PALETTE = [
    (0,   0,   0),    (80,  80,  80),  (160, 160, 160), (255, 255, 255),
    (220, 50,  50),   (230, 120, 40),  (230, 200, 40),  (60,  180,  60),
    (40,  160, 220),  (80,  80,  200), (160, 60,  200), (200, 60,  140),
    (120, 60,  30),   (40,  120, 100), (20,  60,  120), (200, 150, 100),
]

# Tool list:  (id, label, shortcut hint)
TOOLS = [
    ('pencil',         'Pencil',   'P'),
    ('line',           'Line',     'L'),
    ('rectangle',      'Rect',     'R'),
    ('square',         'Square',   'Q'),
    ('circle',         'Circle',   'O'),
    ('right_triangle', 'R-Tri',    'T'),
    ('equil_triangle', 'E-Tri',    'E'),
    ('rhombus',        'Rhombus',  'H'),
    ('fill',           'Fill',     'F'),
    ('text',           'Text',     'X'),
    ('eraser',         'Eraser',   'Z'),
]

KEY_SHORTCUTS = {
    pygame.K_p: 'pencil',
    pygame.K_l: 'line',
    pygame.K_r: 'rectangle',
    pygame.K_q: 'square',
    pygame.K_o: 'circle',
    pygame.K_t: 'right_triangle',
    pygame.K_e: 'equil_triangle',
    pygame.K_h: 'rhombus',
    pygame.K_f: 'fill',
    pygame.K_x: 'text',
    pygame.K_z: 'eraser',
}


# ──────────────────────────────────────────────────────────────────────────────
# Toolbar layout helpers
# ──────────────────────────────────────────────────────────────────────────────

class Toolbar:
    """Renders the top toolbar: tools | sizes | palette"""

    BTN_W, BTN_H = 68, 36
    PAD           = 6
    SWATCH        = 22

    def __init__(self, font_sm, font_xs):
        self.font_sm = font_sm
        self.font_xs = font_xs
        self._build_rects()

    def _build_rects(self):
        x = self.PAD
        y = (TOOLBAR_H - self.BTN_H) // 2

        # Tool buttons
        self.tool_rects = {}
        for tid, label, hint in TOOLS:
            rect = pygame.Rect(x, y, self.BTN_W, self.BTN_H)
            self.tool_rects[tid] = rect
            x += self.BTN_W + 2

        x += self.PAD * 2

        # Size buttons  (1 / 2 / 3)
        self.size_rects = {}
        for k, px in BRUSH_SIZES.items():
            r = pygame.Rect(x, y, 36, self.BTN_H)
            self.size_rects[k] = r
            x += 38

        x += self.PAD * 2

        # Color swatches
        sw = self.SWATCH
        cols_per_row = 8
        self.swatch_rects = []
        for i, color in enumerate(PALETTE):
            col = i % cols_per_row
            row = i // cols_per_row
            sx = x + col * (sw + 2)
            sy = (TOOLBAR_H // 2 - sw) + row * (sw + 2)
            self.swatch_rects.append((pygame.Rect(sx, sy, sw, sw), color))

    def draw(self, screen, active_tool, brush_key, draw_color):
        # Background
        pygame.draw.rect(screen, TOOLBAR_BG, (0, 0, WIN_W, TOOLBAR_H))
        pygame.draw.line(screen, TOOLBAR_LINE, (0, TOOLBAR_H - 1), (WIN_W, TOOLBAR_H - 1))

        # Tool buttons
        for tid, label, hint in TOOLS:
            rect = self.tool_rects[tid]
            is_active = (tid == active_tool)
            bg = ACTIVE_COLOR if is_active else TOOLBAR_BG
            border = ACCENT if is_active else TOOLBAR_LINE

            pygame.draw.rect(screen, bg, rect, border_radius=5)
            pygame.draw.rect(screen, border, rect, 1, border_radius=5)

            txt = self.font_xs.render(f"{label}({hint})", True,
                                      (255, 255, 255) if is_active else TEXT_COLOR)
            screen.blit(txt, txt.get_rect(center=rect.center))

        # Size buttons
        for k, r in self.size_rects.items():
            is_active = (k == brush_key)
            bg = ACTIVE_COLOR if is_active else TOOLBAR_BG
            pygame.draw.rect(screen, bg, r, border_radius=4)
            pygame.draw.rect(screen, ACCENT if is_active else TOOLBAR_LINE, r, 1, border_radius=4)
            lbl = self.font_sm.render(str(k), True,
                                      (255, 255, 255) if is_active else TEXT_COLOR)
            screen.blit(lbl, lbl.get_rect(center=r.center))
            # show dot size
            dot_r = BRUSH_SIZES[k]
            pygame.draw.circle(screen, draw_color,
                                (r.right + 6, r.centery), min(dot_r, 7))

        # Palette swatches
        for rect, color in self.swatch_rects:
            pygame.draw.rect(screen, color, rect)
            if color == draw_color:
                pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            else:
                pygame.draw.rect(screen, (80, 80, 80), rect, 1)

    def hit_tool(self, pos):
        for tid, _, _ in TOOLS:
            if self.tool_rects[tid].collidepoint(pos):
                return tid
        return None

    def hit_size(self, pos):
        for k, r in self.size_rects.items():
            if r.collidepoint(pos):
                return k
        return None

    def hit_swatch(self, pos):
        for rect, color in self.swatch_rects:
            if rect.collidepoint(pos):
                return color
        return None


# ──────────────────────────────────────────────────────────────────────────────
# Text tool state
# ──────────────────────────────────────────────────────────────────────────────

class TextEntry:
    def __init__(self, pos, font, color):
        self.pos   = pos
        self.font  = font
        self.color = color
        self.text  = ""
        self.active = True

    def handle_key(self, event):
        """Returns True if still active, False if committed/cancelled."""
        if event.key == pygame.K_RETURN:
            return False        # commit
        elif event.key == pygame.K_ESCAPE:
            self.text = ""
            return False        # cancel
        elif event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
        else:
            ch = event.unicode
            if ch and ch.isprintable():
                self.text += ch
        return True

    def render_preview(self, surface):
        if not self.text and not self.active:
            return
        surf = self.font.render(self.text + ("_" if self.active else ""),
                                True, self.color)
        surface.blit(surf, self.pos)

    def commit(self, surface):
        if self.text:
            surf = self.font.render(self.text, True, self.color)
            surface.blit(surf, self.pos)


# ──────────────────────────────────────────────────────────────────────────────
# Main application
# ──────────────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen  = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Paint — TSIS 2")
    clock   = pygame.time.Clock()

    # Fonts
    font_sm  = pygame.font.SysFont("Consolas", 14, bold=True)
    font_xs  = pygame.font.SysFont("Consolas", 11, bold=True)
    font_txt = pygame.font.SysFont("Arial",    22)

    toolbar = Toolbar(font_sm, font_xs)

    # Canvas (separate surface so toolbar never gets painted on)
    canvas  = pygame.Surface((CANVAS_W, CANVAS_H))
    canvas.fill(BG_COLOR)

    # State
    active_tool  = 'pencil'
    brush_key    = 2              # default medium
    draw_color   = (0, 0, 0)

    is_drawing   = False
    shape_start  = None
    prev_pos     = None           # for pencil

    text_entry: TextEntry | None = None

    # Overlay surface for live shape preview (transparent)
    overlay = pygame.Surface((CANVAS_W, CANVAS_H), pygame.SRCALPHA)

    def canvas_pos(screen_pos):
        """Convert screen coords → canvas coords."""
        return (screen_pos[0], screen_pos[1] - TOOLBAR_H)

    running = True
    while running:
        clock.tick(60)
        mouse_scr = pygame.mouse.get_pos()
        mouse_cvs = canvas_pos(mouse_scr)
        pressed   = pygame.key.get_pressed()
        ctrl_held = pressed[pygame.K_LCTRL] or pressed[pygame.K_RCTRL]

        for event in pygame.event.get():

            # ── Quit ──────────────────────────────────────────────────────────
            if event.type == pygame.QUIT:
                running = False

            # ── Keyboard ──────────────────────────────────────────────────────
            elif event.type == pygame.KEYDOWN:

                # Text entry gets priority
                if text_entry and text_entry.active:
                    still_active = text_entry.handle_key(event)
                    if not still_active:
                        text_entry.commit(canvas)
                        text_entry = None

                else:
                    # Ctrl+S  → save
                    if event.key == pygame.K_s and ctrl_held:
                        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        name = f"canvas_{ts}.png"
                        pygame.image.save(canvas, name)
                        pygame.display.set_caption(f"Saved → {name}")

                    # Brush sizes 1 / 2 / 3
                    elif event.key == pygame.K_1:
                        brush_key = 1
                    elif event.key == pygame.K_2:
                        brush_key = 2
                    elif event.key == pygame.K_3:
                        brush_key = 3

                    # Clear canvas
                    elif event.key == pygame.K_a:
                        canvas.fill(BG_COLOR)

                    # Tool shortcuts
                    elif event.key in KEY_SHORTCUTS:
                        active_tool = KEY_SHORTCUTS[event.key]

            # ── Mouse button DOWN ─────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    scr_pos = event.pos

                    # Click on toolbar
                    if scr_pos[1] < TOOLBAR_H:
                        hit_tool = toolbar.hit_tool(scr_pos)
                        if hit_tool:
                            active_tool = hit_tool
                            # Cancel text entry if switching tool
                            if text_entry:
                                text_entry = None
                        hit_sz = toolbar.hit_size(scr_pos)
                        if hit_sz:
                            brush_key = hit_sz
                        hit_col = toolbar.hit_swatch(scr_pos)
                        if hit_col:
                            draw_color = hit_col

                    # Click on canvas
                    else:
                        cv_pos = canvas_pos(scr_pos)

                        if active_tool == 'fill':
                            flood_fill(canvas, cv_pos, draw_color)

                        elif active_tool == 'text':
                            # Cancel previous entry if any
                            if text_entry:
                                text_entry.commit(canvas)
                            text_entry = TextEntry(cv_pos, font_txt, draw_color)

                        elif active_tool == 'pencil':
                            is_drawing = True
                            prev_pos   = cv_pos

                        elif active_tool == 'eraser':
                            is_drawing = True
                            draw_eraser(canvas, cv_pos, BG_COLOR, BRUSH_SIZES[brush_key])

                        else:
                            # Shape / line tools
                            is_drawing  = True
                            shape_start = cv_pos

            # ── Mouse button UP ───────────────────────────────────────────────
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and is_drawing:
                    cv_pos = canvas_pos(event.pos)

                    if active_tool not in ('pencil', 'eraser', 'fill', 'text'):
                        if shape_start:
                            draw_shape(canvas, active_tool,
                                       shape_start, cv_pos,
                                       draw_color, BRUSH_SIZES[brush_key])
                        shape_start = None

                    is_drawing = False
                    prev_pos   = None

            # ── Mouse MOTION ──────────────────────────────────────────────────
            elif event.type == pygame.MOUSEMOTION:
                cv_pos = canvas_pos(event.pos)

                if is_drawing:
                    if active_tool == 'pencil' and prev_pos:
                        draw_pencil_stroke(canvas, prev_pos, cv_pos,
                                           draw_color, BRUSH_SIZES[brush_key])
                        prev_pos = cv_pos

                    elif active_tool == 'eraser':
                        draw_eraser(canvas, cv_pos, BG_COLOR, BRUSH_SIZES[brush_key])

        # ── Render ────────────────────────────────────────────────────────────
        # 1. Canvas
        screen.blit(canvas, (0, TOOLBAR_H))

        # 2. Live shape preview
        if is_drawing and shape_start and active_tool not in ('pencil', 'eraser'):
            overlay.fill((0, 0, 0, 0))
            draw_shape(overlay, active_tool,
                       shape_start, mouse_cvs,
                       draw_color, BRUSH_SIZES[brush_key])
            screen.blit(overlay, (0, TOOLBAR_H))

        # 3. Text preview
        if text_entry and text_entry.active:
            preview = canvas.copy()
            text_entry.render_preview(preview)
            screen.blit(preview, (0, TOOLBAR_H))

        # 4. Eraser cursor outline
        if active_tool == 'eraser':
            half = BRUSH_SIZES[brush_key] * 4
            pygame.draw.rect(screen, (120, 120, 120),
                             (mouse_scr[0] - half, mouse_scr[1] - half,
                              half * 2, half * 2), 1)

        # 5. Toolbar (drawn last — always on top)
        toolbar.draw(screen, active_tool, brush_key, draw_color)

        # 6. Status bar hint
        hint = (f"Tool: {active_tool}  |  Size: {BRUSH_SIZES[brush_key]}px  |  "
                f"Ctrl+S=Save  Del=Clear  1/2/3=Size")
        hint_surf = font_xs.render(hint, True, (140, 140, 160))
        screen.blit(hint_surf, (6, TOOLBAR_H - 14))

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()