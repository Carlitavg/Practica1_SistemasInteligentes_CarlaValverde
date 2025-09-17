import sys, pygame
from time import perf_counter
from typing import Optional, List
from NPuzzle.tablero import Tablero, mezclar_aleatorio
from NPuzzle.heuristicas import HEURISTICAS
from NPuzzle.agente_npuzzle import AgenteNPuzzle

N = 3
M = 16
TILE = 124
TOPBAR_H = 56
PANEL_H = 170
W, H = N * TILE + 2 * M, TOPBAR_H + N * TILE + 2 * M + PANEL_H

BG = (246, 248, 250)
CARD = (255, 255, 255)
BORDER = (224, 228, 232)
TEXT = (29, 35, 42)
SUBT = (95, 110, 126)
ACCENT = (0, 122, 255)
ACCENT_H = (0, 105, 220)
EMPTY = (224, 229, 235)

pygame.init()
screen = pygame.display.set_mode((800, 1000)) # (W, H)
pygame.display.set_caption("N-Puzzle (Jugar + Agente)")
font_h1 = pygame.font.SysFont("SF Pro Display, Arial", 28)
font = pygame.font.SysFont("SF Pro Display, Arial", 22)
font_small = pygame.font.SysFont("SF Pro Display, Arial", 18)
clock = pygame.time.Clock()

def draw_text(s, pos, f=font, color=TEXT):
    t = f.render(s, True, color); screen.blit(t, pos); return t.get_rect(topleft=pos)

def rounded_rect(rect, color, radius=16, width=0, border_color=None, border_width=2):
    pygame.draw.rect(screen, color, rect, border_radius=radius)
    if width == 0 and border_color:
        pygame.draw.rect(screen, border_color, rect, border_width, border_radius=radius)

def draw_chip(text, rect, active=False):
    color = ACCENT if active else (238, 241, 245)
    tcol = (255, 255, 255) if active else TEXT
    rounded_rect(rect, color, radius=12)
    r = font_small.render(text, True, tcol)
    screen.blit(r, (rect.x + (rect.w - r.get_width()) // 2, rect.y + (rect.h - r.get_height()) // 2))

def draw_topbar():
    rounded_rect(pygame.Rect(0, 0, W, TOPBAR_H), BG)
    draw_text("N-Puzzle (Jugar + Agente)", (M, TOPBAR_H // 2 - 12), font_h1)

def draw_board(t: Tablero):
    bx, by = M, TOPBAR_H + M
    for r in range(N):
        for c in range(N):
            v = t.fichas[r * N + c]
            x = bx + c * TILE; y = by + r * TILE
            rect = pygame.Rect(x, y, TILE - 6, TILE - 6)
            rounded_rect(rect, CARD if v != 0 else EMPTY, radius=18, border_color=BORDER)
            if v != 0:
                s = font_h1.render(str(v), True, TEXT)
                screen.blit(s, (x + (rect.w - s.get_width()) // 2, y + (rect.h - s.get_height()) // 2))

def board_rect(): 
    return pygame.Rect(M, TOPBAR_H + M, N * TILE, N * TILE)

def click_move(t: Tablero, mx, my) -> Tablero:
    rboard = board_rect()
    if not rboard.collidepoint(mx, my): return t
    c = (mx - rboard.x) // TILE; r = (my - rboard.y) // TILE
    r0, c0 = divmod(t.fichas.index(0), N)
    moves = []
    for dr, dc in ((-1,0),(1,0),(0,-1),(0,1)):
        nr, nc = r0 + dr, c0 + dc
        if 0 <= nr < N and 0 <= nc < N: moves.append((nr, nc))
    if (r, c) in moves:
        j0 = r0 * N + c0; j1 = r * N + c
        arr = list(t.fichas); arr[j0], arr[j1] = arr[j1], arr[j0]
        return Tablero(N, tuple(arr))
    return t

def draw_panel(heur, tec, solving, steps_left, stats):
    y0 = TOPBAR_H + N * TILE + M
    #rounded_rect(pygame.Rect(M, y0, W - 2 * M, PANEL_H - M), CARD, radius=18, border_color=BORDER)
    draw_text("Controles", (M + 18, y0 + 14), font, SUBT)
    chip_h = 36; pad = 10
    btns = {}

    x = M + 18; y = y0 + 46
    btns["mezclar"] = pygame.Rect(x, y, 120, chip_h); draw_chip("Mezclar (R)", btns["mezclar"])
    x += 130
    btns["heur"] = pygame.Rect(x, y, 210, chip_h); draw_chip(f"Heurística: {heur.capitalize()} (H)", btns["heur"])
    x += 220
    btns["tec"] = pygame.Rect(x, y, 210, chip_h); draw_chip(f"Técnica: {tec}", btns["tec"])
    x += 220
    btns["resolver"] = pygame.Rect(x, y, 150, chip_h); draw_chip("Resolver (Espacio)", btns["resolver"], active=True)

    y2 = y + chip_h + 18
    draw_text("Clic en fichas adyacentes al hueco para mover. Esc para salir.", (M + 18, y2), font_small, SUBT)

    y3 = y2 + 28
    draw_text("Métricas última resolución", (M + 18, y3), font, SUBT)
    y4 = y3 + 8 + 24
    if stats:
        s1 = f"Pasos: {stats.get('pasos','-')}"
        s2 = f"Nodos: {stats.get('nodos','-')}"
        s3 = f"Tiempo: {stats.get('tiempo_ms','-')} ms"
        draw_text(s1, (M + 18, y4))
        draw_text(s2, (M + 180, y4))
        draw_text(s3, (M + 340, y4))
    else:
        draw_text("— aún sin resolver —", (M + 18, y4), color=SUBT)
    return btns

def cycle(seq, cur):
    i = seq.index(cur); return seq[(i + 1) % len(seq)]

def solve(tablero, heur_name, tec):
    meta = Tablero(N, tuple([*range(1, N * N), 0]))
    ag = AgenteNPuzzle(N, HEURISTICAS[heur_name], tec)
    ag.fijar_estados(tablero, meta)
    t0 = perf_counter(); ag.programa(); dt = (perf_counter() - t0) * 1000
    ruta = ag.get_acciones() or []
    metr = ag.get_medida_rendimiento() or {}
    pasos = metr.get("pasos", max(0, len(ruta) - 1))
    nodos = metr.get("operaciones", 0)
    stats = {"pasos": pasos, "nodos": int(nodos), "tiempo_ms": round(dt, 1)}
    return ruta, stats

def main():
    heur_names = ["manhattan", "conflicto", "fuera"]
    heur = heur_names[0]
    tec = "astar"
    tablero = mezclar_aleatorio(N, pasos=40, semilla=None)
    ruta: Optional[List[Tablero]] = None
    idx = 0
    anim_ms = 140
    next_tick = 0
    solving = False
    stats = None

    while True:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            if e.type == pygame.KEYDOWN and not solving:
                if e.key == pygame.K_ESCAPE: pygame.quit(); sys.exit(0)
                if e.key == pygame.K_r:
                    tablero = mezclar_aleatorio(N, pasos=40, semilla=None)
                    ruta, idx, solving, stats = None, 0, False, None
                if e.key == pygame.K_h:
                    heur = cycle(heur_names, heur)
                if e.key == pygame.K_t:
                    tec = "codicioso" if tec == "astar" else "astar"
                if e.key == pygame.K_SPACE:
                    ruta, stats = solve(tablero, heur, tec)
                    if ruta and len(ruta) > 1:
                        idx = 0; solving = True; next_tick = now + anim_ms
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                btns = draw_panel(heur, tec, solving, 0, stats)  # layout actual
                if not solving and btns["mezclar"].collidepoint(e.pos):
                    tablero = mezclar_aleatorio(N, pasos=40, semilla=None)
                    ruta, idx, solving, stats = None, 0, False, None
                elif not solving and btns["heur"].collidepoint(e.pos):
                    heur = cycle(heur_names, heur)
                elif not solving and btns["tec"].collidepoint(e.pos):
                    tec = "codicioso" if tec == "astar" else "astar"
                elif not solving and btns["resolver"].collidepoint(e.pos):
                    ruta, stats = solve(tablero, heur, tec)
                    if ruta and len(ruta) > 1:
                        idx = 0; solving = True; next_tick = now + anim_ms
                elif not solving:
                    tablero = click_move(tablero, *e.pos)

        if solving and ruta:
            if now >= next_tick:
                idx += 1
                if idx < len(ruta):
                    tablero = ruta[idx]; next_tick = now + anim_ms
                else:
                    solving = False; ruta = None

        screen.fill(BG)
        draw_topbar()
        draw_board(tablero)
        steps_left = 0 if not ruta else max(0, len(ruta) - 1 - idx)
        btns = draw_panel(heur, tec, solving, steps_left, stats)
        pygame.display.flip()

if __name__ == "__main__":
    main()
