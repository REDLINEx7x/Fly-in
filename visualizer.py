"""Pygame-based visual replay of the Fly-in drone simulation.

Renders directly at window resolution — no upscaling blur.
All coordinates and sizes scale dynamically when the window is resized.
"""

import pygame
import math
import random
from objects import Graph, Zone
from validation import ZoneType

# ── Base layout (at scale=1.0) ────────────────────────────────────────
B_CELL: int = 120
B_MARGIN: int = 90
B_ZONE_R: int = 28
B_DRONE_R: int = 10
B_PANEL_W: int = 250
B_PROG_H: int = 44
ANIM_FRAMES: int = 30
TRAIL_LEN: int = 12

# ── Colors ────────────────────────────────────────────────────────────
PYGAME_COLORS: dict[str, tuple[int, int, int]] = {
    "red": (255, 90, 90), "green": (90, 230, 120),
    "blue": (80, 140, 255), "yellow": (255, 230, 70),
    "magenta": (240, 90, 240), "cyan": (0, 230, 240),
    "white": (220, 220, 230), "gray": (120, 120, 130),
    "grey": (120, 120, 130), "orange": (255, 160, 40),
    "purple": (155, 55, 215), "black": (45, 45, 50),
    "brown": (155, 115, 55), "maroon": (130, 20, 30),
    "gold": (255, 210, 30), "darkred": (110, 25, 25),
    "violet": (175, 115, 255), "crimson": (215, 25, 65),
    "rainbow": (255, 55, 195), "lime": (55, 245, 55),
    "neon": (215, 250, 10), "pink": (255, 145, 195),
    "turquoise": (60, 220, 205),
}
DRONE_PAL: list[tuple[int, int, int]] = [
    (255, 255, 255), (255, 200, 50), (50, 200, 255),
    (255, 100, 150), (130, 255, 110), (255, 140, 40),
    (180, 100, 255), (100, 255, 200), (255, 80, 80),
    (200, 200, 60), (60, 180, 180), (220, 140, 220),
]
BG = (10, 10, 16)
PANEL_BG = (16, 18, 26)
LINE_CLR = (35, 40, 55)
TXT = (215, 220, 232)
TXT_DIM = (105, 112, 128)
TXT_MUTED = (55, 60, 72)
ACCENT = (65, 140, 255)
PROG_BG = (20, 22, 32)
PROG_FG = (65, 140, 255)
SUCCESS_CLR = (50, 210, 100)
WARNING_CLR = (255, 170, 40)
GRID_DOT = (20, 22, 30)
ZTYPE_CLR: dict = {
    ZoneType.NORMAL: (160, 165, 180),
    ZoneType.BLOCKED: (80, 30, 30),
    ZoneType.RESTRICTED: (255, 140, 40),
    ZoneType.PRIORITY: (50, 210, 100),
}
ZTYPE_LBL: dict = {
    ZoneType.NORMAL: "Normal",
    ZoneType.BLOCKED: "Blocked",
    ZoneType.RESTRICTED: "Restricted",
    ZoneType.PRIORITY: "Priority",
}


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def lerp_pos(p1: tuple[int, int], p2: tuple[int, int],
             t: float) -> tuple[int, int]:
    return (int(lerp(p1[0], p2[0], t)), int(lerp(p1[1], p2[1], t)))


def dim(c: tuple[int, int, int], f: float) -> tuple[int, int, int]:
    return (max(0, min(255, int(c[0]*f))),
            max(0, min(255, int(c[1]*f))),
            max(0, min(255, int(c[2]*f))))


def bright(c: tuple[int, int, int], a: int) -> tuple[int, int, int]:
    return (min(255, c[0]+a), min(255, c[1]+a), min(255, c[2]+a))


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "r")

    def __init__(self, x: int, y: int, c: tuple[int, int, int]) -> None:
        ang = random.uniform(0, 2 * math.pi)
        spd = random.uniform(1.5, 4.5)
        self.x, self.y = float(x), float(y)
        self.vx = math.cos(ang) * spd
        self.vy = math.sin(ang) * spd
        self.max_life = random.randint(18, 40)
        self.life = self.max_life
        self.color = c
        self.r = random.uniform(2.0, 4.5)

    def update(self) -> bool:
        self.x += self.vx; self.y += self.vy
        self.vy += 0.06; self.life -= 1; self.r *= 0.97
        return self.life > 0

    def draw(self, s: pygame.Surface) -> None:
        ratio = max(0.0, self.life / self.max_life)
        a = int(255 * ratio)
        col = dim(bright(self.color, int(40 * ratio)), a / 255)
        r = max(1, int(self.r))
        pygame.draw.circle(s, col, (int(self.x), int(self.y)), r)
        if r > 2:
            core = bright(self.color, int(100 * ratio))
            pygame.draw.circle(s, core,
                               (int(self.x), int(self.y)), max(1, r // 2))

class Trail:
    """Fading trail dot for drone movement."""
    __slots__ = ("x", "y", "life", "color", "r")

    def __init__(self, x: int, y: int,
                 c: tuple[int, int, int], r: int) -> None:
        self.x, self.y = x, y
        self.life = TRAIL_LEN
        self.color = c
        self.r = r

    def update(self) -> bool:
        self.life -= 1
        return self.life > 0

    def draw(self, s: pygame.Surface) -> None:
        ratio = self.life / TRAIL_LEN
        col = dim(self.color, ratio * 0.45)
        pygame.draw.circle(s, col,
                           (self.x, self.y), max(1, int(self.r * ratio)))


class Visualizer:
    """Render the simulation with smooth animations at full resolution."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        xs = [z.x for z in graph.all_zones.values()]
        ys = [z.y for z in graph.all_zones.values()]
        self.min_x, self.max_x = min(xs), max(xs)
        self.min_y, self.max_y = min(ys), max(ys)

        # native logical size
        self.nat_map_w = max((self.max_x - self.min_x) * B_CELL + B_MARGIN * 2, 480)
        self.nat_map_h = max((self.max_y - self.min_y) * B_CELL + B_MARGIN * 2, 360)
        self.nat_w = self.nat_map_w + B_PANEL_W
        self.nat_h = self.nat_map_h + B_PROG_H

        pygame.init()
        self.win_w, self.win_h = self.nat_w, self.nat_h
        self.screen = pygame.display.set_mode(
            (self.win_w, self.win_h), pygame.RESIZABLE)
        pygame.display.set_caption("Fly-in — Drone Simulation Visualizer")

        self.scale = 1.0
        self._glow_cache: dict[tuple, pygame.Surface] = {}
        self.particles: list[Particle] = []
        self.trails: list[Trail] = []
        self.pulses: list[tuple[tuple[int, int], int, tuple[int, int, int]]] = []
        self.hover_zone: Zone | None = None
        self.mouse_pos: tuple[int, int] = (0, 0)
        self._prev_dpos: dict[str, tuple[int, int]] = {}
        self._rebuild(self.win_w, self.win_h)

    def _rebuild(self, w: int, h: int) -> None:
        """Recompute scaled constants and fonts for new window size."""
        self.win_w, self.win_h = w, h

        # Use separate x/y scales so content fills the full window
        self.sx = w / self.nat_w
        self.sy = h / self.nat_h
        s = min(self.sx, self.sy)  # for things that must stay uniform (circles, fonts)
        self.scale = s

        # Layout: panel and progress bar use their scale, map fills the rest
        self.panel_w = max(140, int(B_PANEL_W * self.sx))
        self.prog_h = max(24, int(B_PROG_H * self.sy))
        self.map_w = self.win_w - self.panel_w
        self.map_h = self.win_h - self.prog_h

        # Cell size adapts to fill the map area
        span_x = max(1, self.max_x - self.min_x)
        span_y = max(1, self.max_y - self.min_y)
        self.margin_x = max(40, int(self.map_w * 0.06))
        self.margin_y = max(40, int(self.map_h * 0.1))
        self.cell_x = (self.map_w - self.margin_x * 2) // max(1, span_x)
        self.cell_y = (self.map_h - self.margin_y * 2) // max(1, span_y)

        self.zr = max(10, int(B_ZONE_R * s))
        self.dr = max(5, int(B_DRONE_R * s))

        fn = "dejavusans"
        self.f_title = pygame.font.SysFont(fn, max(12, int(20*s)), bold=True)
        self.f_zone = pygame.font.SysFont(fn, max(8, int(11*s)), bold=True)
        self.f_cap = pygame.font.SysFont(fn, max(7, int(9*s)))
        self.f_info = pygame.font.SysFont(fn, max(9, int(14*s)), bold=True)
        self.f_small = pygame.font.SysFont(fn, max(8, int(12*s)))
        self.f_key = pygame.font.SysFont(fn, max(7, int(10*s)))
        self.f_sect = pygame.font.SysFont(fn, max(8, int(10*s)), bold=True)
        self.f_fps = pygame.font.SysFont(fn, max(7, int(9*s)))
        self.f_tip = pygame.font.SysFont(fn, max(8, int(11*s)))

        self._glow_cache.clear()

    # ── coordinate helpers ────────────────────────────────────────────

    def _zts(self, zone: Zone) -> tuple[int, int]:
        return ((zone.x - self.min_x) * self.cell_x + self.margin_x,
                (zone.y - self.min_y) * self.cell_y + self.margin_y)

    def _zcol(self, z: Zone) -> tuple[int, int, int]:
        if z.zone_type == ZoneType.BLOCKED:
            return (55, 22, 22)
        if z.color:
            return PYGAME_COLORS.get(z.color.lower(), (180, 180, 190))
        return (180, 180, 190)

    def _dcol(self, did: str) -> tuple[int, int, int]:
        return DRONE_PAL[int(did[1:]) % len(DRONE_PAL)]

    def _glow(self, r: int, c: tuple[int, int, int],
              a: int = 60) -> pygame.Surface:
        key = (r, *c, a)
        if key in self._glow_cache:
            return self._glow_cache[key]
        sz = r * 4
        surf = pygame.Surface((sz, sz), pygame.SRCALPHA)
        cx = sz // 2
        for ri in range(r * 2, 0, -1):
            ai = int(a * (1 - ri / (r * 2)))
            pygame.draw.circle(surf, (*c, max(0, ai)), (cx, cx), ri)
        self._glow_cache[key] = surf
        return surf

    # ── timeline ──────────────────────────────────────────────────────

    def _build_timeline(self, log: list[str]) -> list[dict[str, str]]:
        tl: list[dict[str, str]] = []
        cur: dict[str, str] = {f"D{i}": self.graph.start.name
                                for i in range(self.graph.n_drones)}
        tl.append(dict(cur))
        for line in log:
            for tok in line.split():
                did, _, tgt = tok.partition("-")
                cur[did] = tgt
            tl.append(dict(cur))
        return tl

    def _snap_to_pixels(self, snap: dict[str, str]) -> dict[str, tuple[int, int]]:
        """Compute pixel positions for all drones in a snapshot."""
        groups: dict[str, list[str]] = {}
        for did, zn in sorted(snap.items()):
            groups.setdefault(zn, []).append(did)
        out: dict[str, tuple[int, int]] = {}
        spacing = max(10, int(18 * self.scale))
        for did, zn in snap.items():
            idx = groups[zn].index(did)
            cnt = len(groups[zn])
            off = (idx - cnt // 2) * spacing
            if "-" in zn:
                parts = zn.split("-")
                if len(parts) == 2:
                    za = self.graph.all_zones.get(parts[0])
                    zb = self.graph.all_zones.get(parts[1])
                    if za and zb:
                        pa, pb = self._zts(za), self._zts(zb)
                        out[did] = ((pa[0]+pb[0])//2 + off, (pa[1]+pb[1])//2)
                        continue
                out[did] = (self.margin_x, self.margin_y)
            else:
                zone = self.graph.all_zones.get(zn)
                if zone:
                    b = self._zts(zone)
                    out[did] = (b[0] + off, b[1])
                else:
                    out[did] = (self.margin_x, self.margin_y)
        return out

    # ── hover detection ────────────────────────────────────────────────

    def _find_hover(self) -> Zone | None:
        """Return the zone under the mouse cursor, if any."""
        mx, my = self.mouse_pos
        if mx >= self.map_w:
            return None
        for zone in self.graph.all_zones.values():
            px, py = self._zts(zone)
            if (mx-px)**2 + (my-py)**2 <= (self.zr + 8) ** 2:
                return zone
        return None

    # ── drawing ───────────────────────────────────────────────────────

    def _draw(self, dpos: dict[str, tuple[int, int]],
              snap: dict[str, str], turn: int, total: int,
              playing: bool, speed: float, tick: int,
              clock: pygame.time.Clock) -> None:
        scr = self.screen
        scr.fill(BG)
        s = self.scale
        occ: dict[str, int] = {}
        for zn in snap.values():
            if "-" not in zn:
                occ[zn] = occ.get(zn, 0) + 1

        # dot grid
        gsp = max(20, int(40 * s))
        for gx in range(0, self.map_w, gsp):
            for gy in range(0, self.map_h, gsp):
                scr.set_at((gx, gy), GRID_DOT)

        # connections
        for con in self.graph.connections:
            pa, pb = self._zts(con.zone_a), self._zts(con.zone_b)
            ca = dim(self._zcol(con.zone_a), 0.35)
            cb = dim(self._zcol(con.zone_b), 0.35)
            mid = ((pa[0]+pb[0])//2, (pa[1]+pb[1])//2)
            lw = max(1, int(2 * s))
            pygame.draw.aaline(scr, ca, pa, mid)
            pygame.draw.aaline(scr, cb, mid, pb)
            if lw > 1:
                pygame.draw.line(scr, ca, pa, mid, lw)
                pygame.draw.line(scr, cb, mid, pb, lw)
            dx, dy = pb[0]-pa[0], pb[1]-pa[1]
            ln = math.sqrt(dx*dx+dy*dy)
            if ln > 0:
                nd = max(2, int(ln / (40*s)))
                for i in range(nd):
                    ft = ((i/nd) + tick*0.008) % 1.0
                    fx, fy = int(pa[0]+dx*ft), int(pa[1]+dy*ft)
                    pygame.draw.circle(scr, dim(ca, 0.5), (fx, fy), max(1, int(1.5*s)))
            if con.max_link_capacity > 1:
                b = self.f_cap.render(str(con.max_link_capacity), True, TXT_DIM)
                scr.blit(b, (mid[0]-b.get_width()//2, mid[1]-b.get_height()//2))

        # zones
        for zone in self.graph.all_zones.values():
            pos = self._zts(zone)
            col = self._zcol(zone)
            g = self._glow(self.zr, col, 40)
            scr.blit(g, (pos[0]-g.get_width()//2, pos[1]-g.get_height()//2))

            if zone == self.graph.start:
                pygame.draw.circle(scr, (40, 220, 80), pos, self.zr+max(3, int(5*s)), max(1, int(2*s)))
            elif zone == self.graph.end:
                pygame.draw.circle(scr, (220, 50, 50), pos, self.zr+max(3, int(5*s)), max(1, int(2*s)))
            if zone.zone_type == ZoneType.RESTRICTED:
                p = int(abs(math.sin(tick * 0.05)) * 40)
                pygame.draw.circle(scr, bright((255, 140, 0), p), pos, self.zr+max(3, int(5*s)), max(1, int(2*s)))

            pygame.draw.circle(scr, col, pos, self.zr)
            pygame.draw.circle(scr, bright(col, 35),
                               (pos[0]-max(1, int(3*s)), pos[1]-max(1, int(5*s))),
                               max(3, self.zr//3))
            pygame.draw.circle(scr, bright(col, 60), pos, self.zr, 1)

            lbl = self.f_zone.render(zone.name, True, TXT)
            scr.blit(lbl, (pos[0]-lbl.get_width()//2, pos[1]+self.zr+max(3, int(5*s))))
            # capacity bar
            bw = max(16, int(30*s))
            bh2 = max(3, int(5*s))
            by2 = pos[1]+self.zr+max(14, int(20*s))
            cur_occ = occ.get(zone.name, 0)
            pygame.draw.rect(scr, dim(TXT_DIM, 0.3), (pos[0]-bw//2, by2, bw, bh2), border_radius=2)
            if zone.max_drones > 0:
                fw2 = int(bw * min(1.0, cur_occ / zone.max_drones))
                bar_c = SUCCESS_CLR if cur_occ < zone.max_drones else WARNING_CLR
                if fw2 > 0:
                    pygame.draw.rect(scr, bar_c, (pos[0]-bw//2, by2, fw2, bh2), border_radius=2)

        # pulses
        np2: list[tuple[tuple[int, int], int, tuple[int, int, int]]] = []
        for (px, py), life, pc in self.pulses:
            if life > 0:
                r = self.zr + (20 - life) * max(1, int(2*s))
                pygame.draw.circle(scr, pc, (px, py), r, max(1, life//5))
                np2.append(((px, py), life-1, pc))
        self.pulses = np2

        # trails
        for did, dp in dpos.items():
            prev = self._prev_dpos.get(did)
            if prev and (prev[0] != dp[0] or prev[1] != dp[1]):
                self.trails.append(Trail(prev[0], prev[1], self._dcol(did), self.dr))
        self._prev_dpos = dict(dpos)
        alive_t = [t for t in self.trails if t.update()]
        for t in alive_t:
            t.draw(scr)
        self.trails = alive_t

        # drones
        for did, dp in dpos.items():
            col = self._dcol(did)
            g = self._glow(self.dr+max(2, int(4*s)), col, 50)
            scr.blit(g, (dp[0]-g.get_width()//2, dp[1]-g.get_height()//2))
            pygame.draw.circle(scr, col, dp, self.dr)
            pygame.draw.circle(scr, bright(col, 80),
                               (dp[0]-max(1, int(2*s)), dp[1]-max(1, int(2*s))),
                               max(1, self.dr//3))
            pygame.draw.circle(scr, bright(col, 40), dp, self.dr, 1)
            dt = self.f_cap.render(did, True, col)
            scr.blit(dt, (dp[0]-dt.get_width()//2, dp[1]-self.dr-max(8, int(12*s))))

        # particles
        alive = [p for p in self.particles if p.update()]
        for p in alive:
            p.draw(scr)
        self.particles = alive

        # side panel
        px = self.map_w
        pw = self.win_w - px
        pygame.draw.rect(scr, PANEL_BG, (px, 0, pw, self.map_h))
        pygame.draw.line(scr, LINE_CLR, (px, 0), (px, self.map_h), 1)
        pad = max(8, int(14*s))

        t = self.f_title.render("FLY-IN", True, ACCENT)
        scr.blit(t, (px+pad, pad))
        sb = self.f_small.render("Drone Visualizer", True, TXT_DIM)
        scr.blit(sb, (px+pad, pad+max(16, int(22*s))))

        y = max(50, int(62*s))
        pygame.draw.line(scr, LINE_CLR, (px+pad-4, y), (px+pw-pad, y))
        y += max(5, int(8*s))
        delivered = sum(1 for zn in snap.values() if zn == self.graph.end.name)
        line_h = max(12, int(18*s))
        for st in [f"Zones: {len(self.graph.all_zones)}",
                   f"Links: {len(self.graph.connections)}",
                   f"Drones: {self.graph.n_drones}",
                   f"Turns: {total}", f"Speed: {speed:.1f}x"]:
            r = self.f_small.render(st, True, TXT_DIM)
            scr.blit(r, (px+pad, y)); y += line_h
        # delivered counter
        dc = self.f_small.render(f"Delivered: {delivered}/{self.graph.n_drones}", True, SUCCESS_CLR)
        scr.blit(dc, (px+pad, y)); y += line_h

        # zone type legend
        y += max(2, int(4*s))
        pygame.draw.line(scr, LINE_CLR, (px+pad-4, y), (px+pw-pad, y))
        y += max(5, int(8*s))
        lh2 = self.f_sect.render("ZONE TYPES", True, TXT_MUTED)
        scr.blit(lh2, (px+pad, y)); y += max(12, int(16*s))
        for zt, lbl in ZTYPE_LBL.items():
            zc = ZTYPE_CLR[zt]
            pygame.draw.circle(scr, zc, (px+pad+max(4, int(6*s)), y+max(3, int(5*s))), max(3, int(4*s)))
            lr = self.f_key.render(lbl, True, TXT_DIM)
            scr.blit(lr, (px+pad+max(12, int(16*s)), y)); y += max(10, int(14*s))

        y += max(2, int(4*s))
        pygame.draw.line(scr, LINE_CLR, (px+pad-4, y), (px+pw-pad, y))
        y += max(5, int(8*s))
        lh = self.f_sect.render("DRONES", True, TXT_MUTED)
        scr.blit(lh, (px+pad, y)); y += max(14, int(18*s))
        dline_h = max(12, int(17*s))
        for did, zn in sorted(snap.items()):
            col = self._dcol(did)
            at_goal = zn == self.graph.end.name
            pygame.draw.circle(scr, col, (px+pad+max(4, int(8*s)), y+max(4, int(6*s))), max(3, int(5*s)))
            loc = "✔ GOAL" if at_goal else (zn if len(zn) <= 16 else zn[:14]+"..")
            tc = SUCCESS_CLR if at_goal else TXT_DIM
            r = self.f_small.render(f"{did}: {loc}", True, tc)
            scr.blit(r, (px+pad+max(12, int(20*s)), y)); y += dline_h
            if y > self.map_h - max(70, int(95*s)):
                r2 = self.f_cap.render("...", True, TXT_DIM)
                scr.blit(r2, (px+pad+max(12, int(20*s)), y)); break

        y = self.map_h - max(60, int(78*s))
        pygame.draw.line(scr, LINE_CLR, (px+pad-4, y), (px+pw-pad, y))
        y += max(4, int(6*s))
        kline_h = max(10, int(13*s))
        for k in ["SPACE  play / pause", "❮ ❯    step turns",
                   "UP/DN  speed", "R      restart", "ESC    quit"]:
            r = self.f_key.render(k, True, TXT_DIM)
            scr.blit(r, (px+pad, y)); y += kline_h

        # progress bar
        by = self.map_h
        fw = self.win_w
        pygame.draw.rect(scr, PROG_BG, (0, by, fw, self.prog_h))
        bh = max(6, int(12*s))
        bar_y = by + self.prog_h//2 - bh//4
        fill = int((turn/total)*(fw-20)) if total > 0 else 0
        pygame.draw.rect(scr, dim(PROG_FG, 0.25), (10, bar_y, fw-20, bh), border_radius=max(3, int(6*s)))
        if fill > 0:
            pygame.draw.rect(scr, PROG_FG, (10, bar_y, fill, bh), border_radius=max(3, int(6*s)))
            # glow on fill edge
            gx = 10 + fill
            gs = self._glow(max(6, int(10*s)), PROG_FG, 35)
            scr.blit(gs, (gx - gs.get_width()//2, bar_y + bh//2 - gs.get_height()//2))
        state = "▶" if playing else "⏸"
        pct = int(100 * turn / total) if total > 0 else 0
        it = self.f_info.render(f"{state}  Turn {turn}/{total}  ({pct}%)", True, TXT)
        scr.blit(it, (max(8, int(14*s)), by+max(1, int(2*s))))

        # FPS
        fps_t = self.f_fps.render(f"{int(clock.get_fps())} FPS", True, TXT_MUTED)
        scr.blit(fps_t, (self.map_w - fps_t.get_width() - 6, 4))

        # hover tooltip
        if self.hover_zone and self.mouse_pos[0] < self.map_w:
            hz = self.hover_zone
            lines = [hz.name, f"Type: {ZTYPE_LBL.get(hz.zone_type, '?')}",
                     f"Capacity: {occ.get(hz.name, 0)}/{hz.max_drones}"]
            if hz.color:
                lines.append(f"Color: {hz.color}")
            tw = max(self.f_tip.size(l)[0] for l in lines) + 16
            th = len(lines) * max(10, int(14*s)) + 10
            tx = min(self.mouse_pos[0]+12, self.map_w - tw - 4)
            ty = max(4, self.mouse_pos[1] - th - 4)
            tip_s = pygame.Surface((tw, th), pygame.SRCALPHA)
            tip_s.fill((10, 12, 20, 210))
            scr.blit(tip_s, (tx, ty))
            pygame.draw.rect(scr, LINE_CLR, (tx, ty, tw, th), 1, border_radius=3)
            for i, l in enumerate(lines):
                c = TXT if i == 0 else TXT_DIM
                lr = self.f_tip.render(l, True, c)
                scr.blit(lr, (tx+8, ty+5+i*max(10, int(14*s))))

    # ── main loop ─────────────────────────────────────────────────────

    def run(self, turn_log: list[str]) -> None:
        timeline = self._build_timeline(turn_log)
        total = len(timeline) - 1
        current_turn = 0; playing = False; speed = 1.0
        clock = pygame.time.Clock(); tick = 0

        anim_progress = 1.0; prev_turn = 0
        prev_snap_zone: dict[str, str] = dict(timeline[0])

        while True:
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT:
                    pygame.quit(); return
                if ev.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode(
                        (ev.w, ev.h), pygame.RESIZABLE)
                    self._rebuild(ev.w, ev.h)
                    self.particles.clear()
                    self.pulses.clear()
                    self.trails.clear()
                    self._prev_dpos.clear()
                if ev.type == pygame.KEYDOWN:
                    if ev.key == pygame.K_SPACE:
                        playing = not playing
                    elif ev.key == pygame.K_RIGHT and not playing:
                        if current_turn < total:
                            prev_turn = current_turn; current_turn += 1; anim_progress = 0.0
                    elif ev.key == pygame.K_LEFT and not playing:
                        if current_turn > 0:
                            prev_turn = current_turn; current_turn -= 1; anim_progress = 0.0
                    elif ev.key == pygame.K_UP:
                        speed = min(speed + 0.5, 8.0)
                    elif ev.key == pygame.K_DOWN:
                        speed = max(speed - 0.5, 0.5)
                    elif ev.key == pygame.K_r:
                        current_turn = 0; prev_turn = 0
                        anim_progress = 1.0; playing = False
                        prev_snap_zone = dict(timeline[0])
                    elif ev.key == pygame.K_ESCAPE:
                        pygame.quit(); return
                if ev.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = ev.pos
                    if my >= self.map_h:
                        bar_w = self.win_w - 20
                        ratio = max(0, min(1, (mx - 10) / bar_w))
                        new_t = int(ratio * total)
                        prev_turn = current_turn; current_turn = new_t
                        anim_progress = 0.0

            # mouse hover
            self.mouse_pos = pygame.mouse.get_pos()
            self.hover_zone = self._find_hover()

            if playing and anim_progress >= 1.0:
                if current_turn < total:
                    prev_turn = current_turn; current_turn += 1; anim_progress = 0.0
                else:
                    playing = False

            if anim_progress < 1.0:
                anim_progress += speed / ANIM_FRAMES
                if anim_progress >= 1.0:
                    anim_progress = 1.0
                    cs = timeline[current_turn]
                    for did, zn in cs.items():
                        if zn != prev_snap_zone.get(did):
                            if zn == self.graph.end.name:
                                pix = self._snap_to_pixels(cs)
                                p = pix[did]
                                c = self._dcol(did)
                                for _ in range(25):
                                    self.particles.append(Particle(p[0], p[1], c))
                            zone = self.graph.all_zones.get(zn)
                            if zone:
                                self.pulses.append((self._zts(zone), 20, self._zcol(zone)))
                    prev_snap_zone = dict(cs)

            # compute interpolated positions at current resolution
            src = self._snap_to_pixels(timeline[prev_turn if anim_progress < 1.0 else current_turn])
            dst = self._snap_to_pixels(timeline[current_turn])
            t = min(1.0, max(0.0, anim_progress))
            t = t * t * (3 - 2 * t)  # ease in-out
            drone_pos = {did: lerp_pos(src.get(did, dst[did]), dst[did], t)
                         for did in dst}

            self._draw(drone_pos, timeline[current_turn],
                       current_turn, total, playing, speed, tick, clock)
            pygame.display.flip()
            clock.tick(60); tick += 1
