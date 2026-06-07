"""
╔══════════════════════════════════════════════════════════════╗
║   GLOSA 3D SIMULÝASIÝA — Kämil Versiýa                      ║
║   Green Light Optimal Speed Advisory                         ║
║   Şanazar Sarjaýew | TDU 2026                               ║
╚══════════════════════════════════════════════════════════════╝

Aýratynlyklar:
  • Gije / Gündüz sikli (real wagt bilen)
  • 3D perspektiw ýol (öňe + yza kamera)
  • Garşy gelen we öňde barýan maşynlar
  • Howa effektleri (ýagyş, gar, duman)
  • GLOSA maslahat ulgamy
  • Kämil dizaýn
"""

import pygame
import numpy as np
import math
import random
import sys

pygame.init()

# ─── EKRAN ────────────────────────────────────────────────
W, H = 1100, 700
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("GLOSA 3D Simulýasiýa — Şanazar Sarjaýew | TDU 2026")
clock = pygame.time.Clock()
FPS = 60

# ─── ŞRIFT ────────────────────────────────────────────────
def load_font(size, bold=False):
    try:
        return pygame.font.SysFont("couriernew", size, bold=bold)
    except:
        return pygame.font.SysFont("monospace", size, bold=bold)

FNT_SM  = load_font(13)
FNT_MD  = load_font(16)
FNT_LG  = load_font(22, bold=True)
FNT_XL  = load_font(32, bold=True)
FNT_TTL = load_font(14)

# ─── REŇKLER ──────────────────────────────────────────────
class C:
    # Esas
    BG_DAY      = (135, 180, 220)
    BG_NIGHT    = (8,   12,  28)
    ROAD_DAY    = (80,  85,  90)
    ROAD_NIGHT  = (28,  32,  42)
    GRASS_DAY   = (72, 140,  60)
    GRASS_NIGHT = (20,  45,  18)
    # Maşynlar
    CAR_GREEN   = (30, 180,  80)
    CAR_RED     = (220,  50,  50)
    CAR_BLUE    = (50,  120, 220)
    CAR_YELLOW  = (240, 190,  30)
    CAR_WHITE   = (220, 220, 220)
    CAR_PURPLE  = (150,  60, 200)
    # Swetafor
    RED         = (220,  40,  40)
    YELLOW      = (240, 190,   0)
    GREEN       = ( 30, 200,  80)
    # UI
    PANEL_BG    = ( 12,  16,  30, 200)
    GLOSA_ON    = ( 30, 200,  80)
    GLOSA_OFF   = (220,  60,  60)
    GOLD        = (240, 180,  30)
    WHITE       = (255, 255, 255)
    MUTED       = (140, 155, 175)
    CYAN        = ( 80, 220, 255)
    ORANGE      = (255, 140,  30)
    TEXT        = (220, 230, 245)

# ─── KONFIGURASIÝA ────────────────────────────────────────
class Config:
    V_MIN_KMH = 30
    V_MAX_KMH = 90
    V_MIN = V_MIN_KMH / 3.6
    V_MAX = V_MAX_KMH / 3.6
    N_LIGHTS = 5
    GAP = 350           # swetafor arasy (m)
    TOTAL = (N_LIGHTS + 1) * GAP
    DAY_CYCLE = 120.0   # sekund (bir doly gün/gije sikli)
    DT = 1.0 / FPS
    WEATHER_DATA = {
        'clear': {'friction': 1.00, 'fuel': 1.00, 'label': 'Açyk',  'color': (255, 220, 80)},
        'rain':  {'friction': 0.82, 'fuel': 1.12, 'label': 'Ýagyş','color': (100, 160, 255)},
        'snow':  {'friction': 0.62, 'fuel': 1.28, 'label': 'Gar',  'color': (200, 210, 255)},
        'fog':   {'friction': 0.74, 'fuel': 1.08, 'label': 'Duman','color': (170, 175, 185)},
    }

# ─── KÖMEKÇI FUNKCIYALAR ──────────────────────────────────
def lerp(a, b, t):
    t = max(0.0, min(1.0, t))
    if isinstance(a, tuple):
        return tuple(int(a[i] + (b[i]-a[i])*t) for i in range(len(a)))
    return a + (b-a)*t

def lerp_color(c1, c2, t):
    return lerp(c1, c2, t)

def draw_text(surf, text, font, color, x, y, align='left'):
    s = font.render(str(text), True, color)
    if align == 'center': x -= s.get_width()//2
    elif align == 'right': x -= s.get_width()
    surf.blit(s, (x, y))
    return s.get_width()

def draw_panel(surf, x, y, w, h, alpha=210, color=(10,14,28)):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill((*color, alpha))
    pygame.draw.rect(s, (60,80,120,150), (0,0,w,h), 1, border_radius=10)
    surf.blit(s, (x, y))

def draw_rounded_rect(surf, color, rect, radius=8, border=0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)

# ─── SWETAFOR SINPY ───────────────────────────────────────
class TrafficLight:
    def __init__(self, pos, green_dur=None, red_dur=None, phase=None):
        self.pos = pos
        self.green_dur = green_dur or random.randint(30, 55)
        self.red_dur   = red_dur   or random.randint(28, 50)
        self.cycle     = self.green_dur + self.red_dur
        self.phase     = phase if phase is not None else random.uniform(0, self.cycle)

    def get_state(self, t):
        cur = (self.phase + t) % self.cycle
        if cur < self.green_dur:
            return 'green', self.green_dur - cur
        return 'red', self.cycle - cur

    def time_to_green(self, t):
        st, rem = self.get_state(t)
        return 0 if st == 'green' else rem

    def time_to_red(self, t):
        st, rem = self.get_state(t)
        return 0 if st == 'red' else rem

# ─── GLOSA ALGORITMI ──────────────────────────────────────
def glosa_advisory(dist, tl, t, v, weather):
    wr = Config.WEATHER_DATA[weather]
    vmax = Config.V_MAX * wr['friction']
    vmin = Config.V_MIN
    st, _ = tl.get_state(t)
    ttg = tl.time_to_green(t)
    ttr = tl.time_to_red(t)
    t_arrive = dist / v if v > 0.1 else 999

    if st == 'green':
        if t_arrive <= ttr - 1.5:
            return v, 'wave', 'ÝAŞYL TOLKUNY'
        t_next = ttr + tl.red_dur
        vopt = np.clip(dist / (t_next + 2), vmin, vmax)
        return vopt, 'slow', 'HAÝALLAŞ'
    else:
        if t_arrive < ttg:
            vopt = np.clip(dist / (ttg + 5), vmin, vmax)
            return vopt, 'slow', 'GARAŞ'
        vopt = np.clip(dist / max(ttg, 0.5), vmin, vmax)
        return vopt, 'wave', 'ÝAKYNLAŞ'

# ─── GARŞY GELEN MAŞYN ────────────────────────────────────
class OtherCar:
    COLORS = [(220,50,50),(50,120,220),(240,190,30),(200,60,200),(30,180,130),(255,120,40)]

    def __init__(self, direction=1):
        self.direction = direction  # 1=öňe, -1=garşy
        if direction == 1:
            self.x = random.uniform(-300, Config.TOTAL*0.5)
            self.lane = random.choice(['right_slow', 'right_fast'])
        else:
            self.x = random.uniform(Config.TOTAL*0.3, Config.TOTAL + 300)
            self.lane = random.choice(['left1', 'left2'])
        self.v_kmh = random.uniform(40, 85)
        self.v = self.v_kmh / 3.6 * direction
        self.color = random.choice(self.COLORS)
        self.stopped = False
        self.length = random.uniform(4.0, 5.5)
        self.width  = 2.0

    def update(self, dt, lights, t, weather):
        wr = Config.WEATHER_DATA[weather]
        vmax = 80/3.6 * wr['friction']
        if self.direction == 1:
            # Öňdäki swetafory tap
            for tl in lights:
                if tl.pos > self.x and tl.pos - self.x < 30:
                    st, _ = tl.get_state(t)
                    if st == 'red':
                        self.stopped = True
                        self.v = 0
                        return
            self.stopped = False
            self.v = min(self.v_kmh/3.6, vmax)
            self.x += self.v * dt
            if self.x > Config.TOTAL + 200:
                self.x = -random.uniform(50, 400)
        else:
            self.v = -abs(self.v_kmh)/3.6 * wr['friction']
            self.x += self.v * dt
            if self.x < -300:
                self.x = Config.TOTAL + random.uniform(50, 400)

# ─── HOWA BÖLEJIKLERI ─────────────────────────────────────
class Particle:
    def __init__(self, w, h, wtype):
        self.reset(w, h, wtype)

    def reset(self, w, h, wtype):
        self.x = random.uniform(0, w)
        self.y = random.uniform(-20, h)
        self.wtype = wtype
        if wtype == 'rain':
            self.vx, self.vy = -1.5, random.uniform(12, 20)
            self.size = random.uniform(1, 2)
            self.color = (120, 170, 255, random.randint(100,200))
        elif wtype == 'snow':
            self.vx = random.uniform(-0.8, 0.8)
            self.vy = random.uniform(1.2, 3)
            self.size = random.uniform(2, 5)
            self.color = (210, 220, 255, random.randint(150,220))

    def update(self, w, h, wtype):
        self.x += self.vx
        self.y += self.vy
        if wtype == 'snow':
            self.vx += math.sin(self.y * 0.05) * 0.04
        if self.y > h + 20 or self.x < -20 or self.x > w + 20:
            self.reset(w, h, wtype)

# ─── KAMERA SINPY ─────────────────────────────────────────
class Camera:
    def __init__(self):
        self.mode = 'front'  # 'front' | 'back'
        self.shake = 0.0

    def toggle(self):
        self.mode = 'back' if self.mode == 'front' else 'front'

# ─── 3D PERSPEKTIW ÇYZYŞ ──────────────────────────────────
class Renderer3D:
    def __init__(self, cam):
        self.cam = cam

    def world_to_screen(self, world_x, player_x, lane_off=0):
        """Dünýä koordinatasy → ekran koordinatasy (perspektiw)"""
        if self.cam.mode == 'front':
            rel = world_x - player_x
        else:
            rel = player_x - world_x

        VIEW_DIST = 600.0
        HORIZON_Y = int(H * 0.40)
        ROAD_Y    = H - 40
        VP_X      = W // 2

        if rel < 1.0:
            return None

        t = 1.0 - rel / VIEW_DIST
        if t <= 0.0:
            return None

        sy = int(HORIZON_Y + t * (ROAD_Y - HORIZON_Y))
        scale = t
        sx = int(VP_X + lane_off * scale * 200)
        return sx, sy, scale

    def road_segment_x(self, player_x, world_x, lane_off=0):
        """Perspektiw X"""
        r = self.world_to_screen(world_x, player_x, lane_off)
        return r

    def draw_sky(self, surf, day_t, weather):
        """Asman — gündüz/gije gradýent"""
        HORIZON_Y = int(H * 0.40)
        if weather == 'fog':
            sky_top = (170, 175, 185)
            sky_bot = (200, 200, 205)
        elif day_t < 0.5:
            # Gündüz
            d = day_t / 0.5
            sky_top = lerp_color((10,20,60), (30,100,200), d)
            sky_bot = lerp_color((40,80,140),(130,185,240), d)
        else:
            # Gije
            n = (day_t - 0.5) / 0.5
            sky_top = lerp_color((10,20,60),(5,8,25), n)
            sky_bot = lerp_color((30,100,200),(15,30,70), n)

        for y in range(HORIZON_Y):
            t = y / HORIZON_Y
            c = lerp_color(sky_top, sky_bot, t)
            pygame.draw.line(surf, c, (0,y), (W,y))

        # Gün
        if day_t < 0.5 and weather not in ('fog',):
            d = day_t / 0.5
            sun_x = int(W*0.15 + W*0.7*d)
            sun_y = int(HORIZON_Y * 0.35 + HORIZON_Y*0.3*(1-(d-0.5)**2*4 if d>0.5 else d*0.4))
            brightness = int(255 * min(1.0, d*3 if d<0.33 else (1-d)*3+0.01 if d>0.67 else 1.0))
            if brightness > 30:
                pygame.draw.circle(surf, (min(255,brightness+80),min(255,brightness+40),brightness//3), (sun_x,sun_y), 22)
                glow = pygame.Surface((80,80), pygame.SRCALPHA)
                pygame.draw.circle(glow,(255,220,100,40),(40,40),40)
                surf.blit(glow,(sun_x-40,sun_y-40))

        # Aý (gije)
        elif day_t >= 0.5:
            n = (day_t-0.5)/0.5
            moon_a = int(200*n)
            if moon_a > 20:
                pygame.draw.circle(surf,(200,210,230),(int(W*0.75),int(HORIZON_Y*0.3)),14)
                # Ýyldyzlar
                rng = random.Random(42)
                for i in range(60):
                    sx = rng.randint(0,W)
                    sy = rng.randint(0, HORIZON_Y-5)
                    bright = int(n * rng.randint(80,200))
                    twinkle = int(math.sin(pygame.time.get_ticks()*0.001 + i) * 30)
                    br = max(0, min(255, bright + twinkle))
                    if br > 20:
                        pygame.draw.circle(surf,(br,br,min(255,br+20)),(sx,sy),1)

    def draw_road(self, surf, player_x, day_t, weather):
        HORIZON_Y = int(H*0.40)
        ROAD_Y    = H - 40
        VP_X      = W//2

        # Ot (gapdal)
        night = max(0, (day_t-0.5)/0.5) if day_t>=0.5 else 0
        grass_c = lerp_color(C.GRASS_DAY, C.GRASS_NIGHT, night)
        surf.fill(grass_c, (0, HORIZON_Y, W, H-HORIZON_Y))

        # Ýol yüzeýi
        road_c = lerp_color(C.ROAD_DAY, C.ROAD_NIGHT, night)
        road_pts = [
            (VP_X-18, HORIZON_Y+2),
            (VP_X+18, HORIZON_Y+2),
            (W, ROAD_Y),
            (0, ROAD_Y),
        ]
        pygame.draw.polygon(surf, road_c, road_pts)

        # Gapdal çyzgylar (perspektiw)
        for side, mul in [(-1, -1), (1, 1)]:
            pts = []
            for i in range(20):
                t = i / 19
                x = int(VP_X + mul * (18 + 90*t))
                y = int(HORIZON_Y + t * (ROAD_Y - HORIZON_Y))
                pts.append((x, y))
            if len(pts) >= 2:
                pygame.draw.lines(surf, lerp_color((200,200,200),(100,105,110),night), False, pts, 1)

        # Orta çyzyklar (noktalanma)
        steps = 25
        for i in range(steps):
            t1 = i/steps
            t2 = (i+0.45)/steps

            # Perspektiw döwürleme
            world_step = 600/steps
            rel1 = (i+0.5) * world_step
            rel2 = (i+0.95) * world_step

            t_r1 = 1 - rel1/600
            t_r2 = 1 - rel2/600
            if t_r1 <= 0 or t_r2 <= 0:
                continue

            y1 = int(HORIZON_Y + t_r1*(ROAD_Y-HORIZON_Y))
            y2 = int(HORIZON_Y + t_r2*(ROAD_Y-HORIZON_Y))
            thk = max(1, int(2*t_r1))
            dash_c = lerp_color((240,210,30),(120,110,20),night) if weather!='fog' else (150,150,150)
            pygame.draw.line(surf, dash_c, (VP_X, y1), (VP_X, y2), thk)

        # Ýoluň gyrasynda reňk zolak
        edge_c = (255,200,0) if weather!='fog' else (180,180,180)
        for off in [-1, 1]:
            pts2 = []
            for i in range(20):
                t = i/19
                x = int(VP_X + off*(18+90*t))
                y = int(HORIZON_Y + t*(ROAD_Y-HORIZON_Y))
                pts2.append((x,y))
            if len(pts2)>=2:
                pygame.draw.lines(surf, edge_c, False, pts2, 2)

    def draw_traffic_light(self, surf, tl, player_x, t):
        pos3d = self.world_to_screen(tl.pos, player_x, lane_off=0)
        if pos3d is None: return
        sx, sy, scale = pos3d
        if scale < 0.05: return

        st, rem = tl.get_state(t)
        pole_h = int(90 * scale)
        bw = int(22*scale); bh = int(60*scale)
        bx = sx - bw//2; by = sy - pole_h - bh

        # Direk
        pygame.draw.rect(surf, (40,50,60), (sx-int(2*scale), sy-pole_h, int(4*scale), pole_h))

        # Korpus
        draw_rounded_rect(surf, (20,25,35), (bx, by, bw, bh), radius=int(4*scale))
        draw_rounded_rect(surf, (50,60,80), (bx, by, bw, bh), radius=int(4*scale), border=1, border_color=(70,90,120))

        # Çyralar
        r = max(3, int(8*scale))
        cx = sx
        for i, (yoff, col_on, col_off, is_on) in enumerate([
            (0.15, C.RED,    (60,15,15), st=='red'),
            (0.5,  C.YELLOW, (60,50,10), False),
            (0.85, C.GREEN,  (10,55,20), st=='green'),
        ]):
            cy = by + int(bh * yoff)
            c = col_on if is_on else col_off
            pygame.draw.circle(surf, c, (cx, cy), r)
            if is_on and scale > 0.2:
                glow = pygame.Surface((r*6, r*6), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*col_on, 60), (r*3,r*3), r*3)
                surf.blit(glow, (cx-r*3, cy-r*3))

        # Geri saýyş
        if scale > 0.35:
            rem_s = FNT_SM.render(f"{rem:.0f}s", True, C.WHITE if st=='green' else (255,180,180))
            surf.blit(rem_s, (bx - rem_s.get_width()//2 + bw//2, by + bh + 2))

    def draw_car(self, surf, car, player_x, night):
        lane_offsets = {
            'right_fast': 0.3,
            'right_slow': 0.55,
            'left1':     -0.35,
            'left2':     -0.6,
        }
        lo = lane_offsets.get(car.lane, 0.3)
        pos3d = self.world_to_screen(car.x, player_x, lane_off=lo)
        if pos3d is None: return
        sx, sy, scale = pos3d
        if scale < 0.06: return

        cw = int(50*scale); ch = int(24*scale)
        bx = sx - cw//2; by = sy - ch

        # Kölge
        shadow = pygame.Surface((cw, 8), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,80), (0,0,cw,8))
        surf.blit(shadow, (bx, sy-4))

        # Kuzow
        body_c = lerp_color(car.color, (car.color[0]//3, car.color[1]//3, car.color[2]//3), night*0.5)
        draw_rounded_rect(surf, body_c, (bx, by+int(ch*0.35), cw, int(ch*0.65)), radius=int(3*scale))

        # Üst
        roof_c = tuple(max(0,c-30) for c in body_c)
        roof_pts = [
            (bx+int(cw*0.18), by+int(ch*0.35)),
            (bx+int(cw*0.82), by+int(ch*0.35)),
            (bx+int(cw*0.72), by),
            (bx+int(cw*0.28), by),
        ]
        pygame.draw.polygon(surf, roof_c, roof_pts)

        # Aýna
        if scale > 0.2:
            glass_c = (100,170,220,180)
            gs = pygame.Surface((int(cw*0.5), int(ch*0.3)), pygame.SRCALPHA)
            gs.fill(glass_c)
            surf.blit(gs, (bx+int(cw*0.25), by+int(ch*0.05)))

        # Fara
        if scale > 0.15:
            fara_side = bx + cw - int(3*scale) if car.direction==1 else bx + int(3*scale)
            fara_c = (255,250,200) if night > 0.3 else (200,200,160)
            pygame.draw.ellipse(surf, fara_c, (fara_side-int(5*scale), by+int(ch*0.5), int(8*scale), int(6*scale)))
            if night > 0.4 and scale > 0.25:
                beam = pygame.Surface((int(60*scale), int(40*scale)), pygame.SRCALPHA)
                pygame.draw.polygon(beam,(255,250,180,25),[(0,10),(0,30),(int(60*scale),int(40*scale)),(int(60*scale),0)])
                surf.blit(beam,(fara_side if car.direction==1 else fara_side-int(60*scale), by+int(ch*0.3)))

    def draw_player_car(self, surf, player_x, day_t, v_kmh, glosa, adv_msg, strategy):
        ROAD_Y = H - 40
        VP_X   = W // 2
        night  = max(0, (day_t-0.5)/0.5) if day_t>=0.5 else 0.0

        # Esas maşyn (aşakda, uly)
        cw = 120; ch = 55
        cx = VP_X; cy = ROAD_Y - 10
        bx = cx - cw//2; by = cy - ch

        # Kölge
        sh = pygame.Surface((cw, 18), pygame.SRCALPHA)
        pygame.draw.ellipse(sh,(0,0,0,100),(0,0,cw,18))
        surf.blit(sh,(bx, cy-9))

        # Kuzow
        body_c = lerp_color(C.CAR_GREEN, (10,80,35), night*0.4)
        draw_rounded_rect(surf, body_c, (bx, by+int(ch*0.35), cw, int(ch*0.65)), radius=6)

        # Üst
        roof_c = (20,140,55)
        roof_pts = [
            (bx+int(cw*0.15), by+int(ch*0.35)),
            (bx+int(cw*0.85), by+int(ch*0.35)),
            (bx+int(cw*0.75), by),
            (bx+int(cw*0.25), by),
        ]
        pygame.draw.polygon(surf, roof_c, roof_pts)

        # Aýna
        glass = pygame.Surface((int(cw*0.52), int(ch*0.32)), pygame.SRCALPHA)
        glass.fill((120,200,255,150))
        surf.blit(glass,(bx+int(cw*0.24), by+int(ch*0.04)))

        # Faralar
        fara_c = (255,250,200) if night>0.3 else (200,195,160)
        pygame.draw.ellipse(surf, fara_c, (bx+cw-12, by+int(ch*0.5), 14, 10))
        if night>0.4:
            beam = pygame.Surface((200,80),pygame.SRCALPHA)
            pygame.draw.polygon(beam,(255,250,160,18),[(0,20),(0,60),(200,80),(200,0)])
            surf.blit(beam,(bx+cw-12,by+int(ch*0.4)))

        # GLOSA maslahat belligi
        if glosa and adv_msg:
            badge_c = (20,160,60,220) if strategy=='wave' else (180,40,40,220)
            bw2 = 200; bh2 = 34
            bx2 = VP_X - bw2//2; by2 = by - 45
            bs = pygame.Surface((bw2,bh2),pygame.SRCALPHA)
            bs.fill((*badge_c[:3], 200))
            pygame.draw.rect(bs,(255,255,255,60),(0,0,bw2,bh2),1,border_radius=8)
            surf.blit(bs,(bx2,by2))
            draw_text(surf, adv_msg, FNT_MD, C.WHITE, VP_X, by2+8, align='center')

        # Tizlik ölçegi (kapitanka)
        spd = FNT_LG.render(f"{v_kmh:.0f} km/s", True, (50,220,120) if v_kmh>35 else C.ORANGE)
        surf.blit(spd,(VP_X - spd.get_width()//2, by - 80))

# ─── STATISTIKA / LOG ─────────────────────────────────────
class LogBuffer:
    def __init__(self, max_lines=10):
        self.lines = []
        self.max = max_lines

    def add(self, msg, color=C.MUTED):
        t_s = pygame.time.get_ticks()//1000
        self.lines.append((f"[{t_s:>4}s] {msg}", color))
        if len(self.lines) > self.max:
            self.lines.pop(0)

    def draw(self, surf, x, y, w, h):
        draw_panel(surf, x, y, w, h, alpha=180, color=(6,10,22))
        for i, (txt, col) in enumerate(self.lines[-8:]):
            draw_text(surf, txt, FNT_SM, col, x+10, y+8+i*15)

# ─── ESASY OÝUN ───────────────────────────────────────────
def main():
    renderer = Renderer3D(Camera())
    logger   = LogBuffer()

    # Swetaforlar
    lights = [TrafficLight((i+1)*Config.GAP) for i in range(Config.N_LIGHTS)]

    # Garşy gelen maşynlar
    other_cars = [OtherCar(direction=1) for _ in range(5)] + \
                 [OtherCar(direction=-1) for _ in range(4)]

    # Howa bölejikleri
    particles = [Particle(W, H, 'rain') for _ in range(120)] + \
                [Particle(W, H, 'snow') for _ in range(80)]
    rain_p  = particles[:120]
    snow_p  = particles[120:]

    # Simulýasiýa ýagdaýy
    sim = {
        'running': False,
        'glosa'  : True,
        'weather': 'clear',
        'v_init' : 60.0,
        't'      : 0.0,
        'x'      : 0.0,
        'v'      : 60.0/3.6,
        'fuel'   : 0.0,
        'fuel_ng': 0.0,
        'stops'  : 0,
        'adv_msg': '',
        'strategy':'',
        'finished': False,
        'camera_mode': 'front',  # 'front' | 'back'
        'paused' : False,
    }

    # UI ýagdaýy
    ui = {
        'slider_drag': False,
        'show_help'  : True,
        'help_timer' : 240,
    }

    def reset_sim():
        sim['t'] = 0.0
        sim['x'] = 0.0
        sim['v'] = sim['v_init'] / 3.6
        sim['fuel'] = 0.0
        sim['fuel_ng'] = 0.0
        sim['stops'] = 0
        sim['running'] = False
        sim['finished'] = False
        sim['adv_msg'] = ''
        for c in other_cars:
            c.x = random.uniform(-200, Config.TOTAL) if c.direction==1 else random.uniform(Config.TOTAL*0.3, Config.TOTAL+300)
        logger.add("Ulgam täzelendi. SPACE — başla.", C.CYAN)

    reset_sim()
    logger.add("GLOSA Simulýasiýa taýyn!", C.GOLD)
    logger.add("SPACE=Başla  C=Kamera  G=GLOSA  R=Täzele", C.MUTED)

    # Slaýder rect
    SLIDER_X = 20; SLIDER_Y = H - 98; SLIDER_W = 200; SLIDER_H = 8

    # ─── Esasy Loop ───────────────────────────────────────
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        # Gün/gije parametri [0..1]: 0=gündiz ortasy, 0.5=düýe, 1=gündiz
        day_t = (sim['t'] / Config.DAY_CYCLE) % 1.0

        # Gije koef
        night = max(0, (day_t-0.5)/0.5) if day_t >= 0.5 else 0.0

        # ─── Wakalar ──────────────────────────────────────
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            if ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_ESCAPE:
                    running = False
                elif ev.key == pygame.K_SPACE:
                    if sim['finished']:
                        reset_sim()
                    else:
                        sim['running'] = not sim['running']
                        sim['paused'] = not sim['running']
                        logger.add("Başlady!" if sim['running'] else "Saklanyldy.", C.GOLD)
                elif ev.key == pygame.K_r:
                    reset_sim()
                elif ev.key == pygame.K_g:
                    sim['glosa'] = not sim['glosa']
                    logger.add(f"GLOSA: {'AÇYLDY' if sim['glosa'] else 'ÝAPYLDY'}", C.GLOSA_ON if sim['glosa'] else C.GLOSA_OFF)
                elif ev.key == pygame.K_c:
                    sim['camera_mode'] = 'back' if sim['camera_mode']=='front' else 'front'
                    renderer.cam.mode = sim['camera_mode']
                    logger.add(f"Kamera: {'ARKA' if sim['camera_mode']=='back' else 'ÖŇ'}", C.CYAN)
                elif ev.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
                    w = ['clear','rain','snow','fog'][ev.key - pygame.K_1]
                    sim['weather'] = w
                    sim['v'] = min(sim['v'], Config.V_MAX * Config.WEATHER_DATA[w]['friction'])
                    logger.add(f"Howa: {Config.WEATHER_DATA[w]['label']}", C.CYAN)
                elif ev.key == pygame.K_h:
                    ui['show_help'] = not ui['show_help']

            if ev.type == pygame.MOUSEBUTTONDOWN:
                mx, my = ev.pos
                if SLIDER_X <= mx <= SLIDER_X+SLIDER_W and abs(my-SLIDER_Y) < 20:
                    ui['slider_drag'] = True
            if ev.type == pygame.MOUSEBUTTONUP:
                ui['slider_drag'] = False
            if ev.type == pygame.MOUSEMOTION and ui['slider_drag']:
                mx = ev.pos[0]
                pct = (mx - SLIDER_X) / SLIDER_W
                sim['v_init'] = Config.V_MIN_KMH + pct*(Config.V_MAX_KMH - Config.V_MIN_KMH)
                sim['v_init'] = max(Config.V_MIN_KMH, min(Config.V_MAX_KMH, sim['v_init']))

        # ─── Fizika / Simulýasiýa ─────────────────────────
        if sim['running'] and not sim['finished']:
            wr = Config.WEATHER_DATA[sim['weather']]
            vmax = Config.V_MAX * wr['friction']

            # Garşy gelen maşynlar
            for oc in other_cars:
                oc.update(dt, lights, sim['t'], sim['weather'])

            # GLOSA maslahat
            next_tl = None
            dist_tl = 0
            for tl in lights:
                if tl.pos > sim['x']:
                    next_tl = tl
                    dist_tl = tl.pos - sim['x']
                    break

            if next_tl and dist_tl < 320 and sim['glosa']:
                v_rec, strategy, msg = glosa_advisory(dist_tl, next_tl, sim['t'], sim['v'], sim['weather'])
                sim['adv_msg'] = msg
                sim['strategy'] = strategy
            else:
                v_rec = vmax
                sim['adv_msg'] = 'ERKİN HEREKET'
                sim['strategy'] = 'wave'

            # Tizlik çalşygy (ýuwaş)
            accel = np.clip((v_rec - sim['v']) / 2.5, -3.5, 2.5)
            sim['v'] = float(np.clip(sim['v'] + accel*dt, Config.V_MIN, vmax))

            # Swetafor barlagy
            if next_tl and dist_tl <= sim['v']*dt*2:
                st, _ = next_tl.get_state(sim['t'])
                if st == 'red':
                    sim['stops'] += 1
                    wait = next_tl.time_to_green(sim['t'])
                    idle = (0.5/3600) * wr['fuel']
                    sim['fuel']    += idle * wait
                    sim['fuel_ng'] += idle * wait * 1.18
                    sim['t'] += wait
                    sim['v'] = Config.V_MIN
                    logger.add(f"Swetaforda: {wait:.0f}s garaşyldy!", C.RED)
                else:
                    logger.add(f"Ýaşyl tolkuny! Geçildi.", C.GLOSA_ON)
                sim['x'] = next_tl.pos + 0.5

            # Ýangyç
            def f_rate(v, w):
                kmh = v*3.6
                return (0.05*kmh + 0.003*kmh*kmh)/100 * v/1000 * Config.WEATHER_DATA[w]['fuel']

            sim['fuel']    += f_rate(sim['v'], sim['weather']) * dt
            sim['fuel_ng'] += f_rate(min(vmax, sim['v_init']/3.6*1.08), sim['weather']) * dt * 1.05
            sim['x'] += sim['v'] * dt
            sim['t'] += dt

            if sim['x'] >= Config.TOTAL:
                sim['finished'] = True
                sim['running']  = False
                saved_pct = (sim['fuel_ng']-sim['fuel'])/sim['fuel_ng']*100 if sim['fuel_ng']>0 else 0
                logger.add(f"TAMAMLANDY! Tygşytlylyk: {saved_pct:.1f}%", C.GOLD)
                logger.add(f"Säginme: {sim['stops']}, Ýangyç: {sim['fuel']*1000:.2f}ml", C.CYAN)

        # ─── ÇYZMAK ───────────────────────────────────────
        screen.fill(C.BG_NIGHT)

        # Asman + ýol
        renderer.draw_sky(screen, day_t, sim['weather'])
        renderer.draw_road(screen, sim['x'], day_t, sim['weather'])

        # Garşy gelen maşynlar (uzakdakylar öňürti)
        sorted_oc = sorted(other_cars, key=lambda c: -abs(c.x - sim['x']))
        for oc in sorted_oc:
            renderer.draw_car(screen, oc, sim['x'], night)

        # Swetaforlar
        sorted_lights = sorted(lights, key=lambda tl: -abs(tl.pos - sim['x']))
        for tl in sorted_lights:
            renderer.draw_traffic_light(screen, tl, sim['x'], sim['t'])

        # Esasy maşyn
        renderer.draw_player_car(
            screen, sim['x'], day_t,
            sim['v']*3.6, sim['glosa'],
            sim['adv_msg'] if sim['running'] else '',
            sim['strategy']
        )

        # Howa effektleri
        if sim['weather'] == 'rain':
            for p in rain_p:
                p.update(W, H, 'rain')
                pygame.draw.line(screen, (100,150,255,160), (int(p.x),int(p.y)), (int(p.x-2),int(p.y+10)), 1)
        elif sim['weather'] == 'snow':
            for p in snow_p:
                p.update(W, H, 'snow')
                pygame.draw.circle(screen, (210,220,255), (int(p.x),int(p.y)), int(p.size))
        elif sim['weather'] == 'fog':
            fog_s = pygame.Surface((W, H), pygame.SRCALPHA)
            for fy in range(0, H, 40):
                intensity = int(50 + 30*math.sin(sim['t']*0.3+fy*0.02))
                fog_s.fill((160,165,175, intensity), (0, fy, W, 40))
            screen.blit(fog_s, (0,0))

        # ────────────────────────────────────────────────
        #  SOL PANEL — Maglumatlr
        # ────────────────────────────────────────────────
        draw_panel(screen, 12, 12, 240, 220, alpha=210, color=(6,10,22))
        draw_text(screen, "GLOSA ULGAMY", FNT_LG, C.GOLD, 122, 18, align='center')
        pygame.draw.line(screen, (50,70,110), (18,44),(246,44), 1)

        # KPI satyrlar
        v_kmh = sim['v']*3.6
        saved_pct = (sim['fuel_ng']-sim['fuel'])/sim['fuel_ng']*100 if sim['fuel_ng']>0 else 0
        galan_yol = max(0, Config.TOTAL - sim['x'])

        kpis = [
            ("Tizlik",       f"{v_kmh:.1f} km/s",                      (60,220,120) if v_kmh>35 else C.ORANGE),
            ("Ýangyç",       f"{sim['fuel']*1000:.2f} ml",              C.GOLD),
            ("Säginme",      f"{sim['stops']}",                         C.RED),
            ("Tygşytlylyk",  f"{saved_pct:.1f}%",                       C.CYAN),
            ("Galan ýol",    f"{galan_yol:.0f} m",                      C.TEXT),
            ("Geçilen ýol",  f"{sim['x']:.0f} m",                       C.MUTED),
            ("Wagt",         f"{sim['t']:.0f} s",                        C.MUTED),
        ]
        for i,(lbl, val, col) in enumerate(kpis):
            y = 52 + i*22
            draw_text(screen, lbl+":", FNT_TTL, C.MUTED, 20, y)
            draw_text(screen, val,     FNT_TTL, col,     248, y, align='right')

        # GLOSA & Howa ýagdaýy
        g_c = C.GLOSA_ON if sim['glosa'] else C.GLOSA_OFF
        g_lbl = "GLOSA: AÇYK [G]" if sim['glosa'] else "GLOSA: ÝAPYK [G]"
        draw_rounded_rect(screen, (*g_c[:3],40) if False else (10,30,15) if sim['glosa'] else (30,10,10),
                          (16, 214, 228, 22), radius=5)
        pygame.draw.rect(screen, g_c, (16,214,228,22), 1, border_radius=5)
        draw_text(screen, g_lbl, FNT_TTL, g_c, 130, 218, align='center')

        wr = Config.WEATHER_DATA[sim['weather']]
        draw_text(screen, wr['label'], FNT_TTL, wr['color'], 130, 238, align='center')

        # ────────────────────────────────────────────────
        #  SAĞ PANEL — Swetaforlar
        # ────────────────────────────────────────────────
        draw_panel(screen, W-210, 12, 198, 30+Config.N_LIGHTS*28, alpha=200, color=(6,10,22))
        draw_text(screen, "SWETAFORLAR", FNT_TTL, C.GOLD, W-111, 18, align='center')
        for i, tl in enumerate(lights):
            st, rem = tl.get_state(sim['t'])
            col = C.GREEN if st=='green' else C.RED
            dist = max(0, tl.pos - sim['x'])
            pygame.draw.circle(screen, col, (W-198, 40+i*28), 7)
            if st=='green':
                glow2 = pygame.Surface((24,24),pygame.SRCALPHA)
                pygame.draw.circle(glow2,(30,200,80,50),(12,12),12)
                screen.blit(glow2,(W-210,28+i*28))
            draw_text(screen, f"#{i+1}  {rem:>4.0f}s   {dist:>5.0f}m", FNT_SM, C.TEXT, W-188, 34+i*28)

        # ────────────────────────────────────────────────
        #  AŞAK PANEL — Slaýder + Kamera + Düwmeler
        # ────────────────────────────────────────────────
        draw_panel(screen, 0, H-115, 560, 115, alpha=200, color=(6,10,22))

        # Tizlik slaýderi
        draw_text(screen, "Başlangyç tizlik:", FNT_TTL, C.MUTED, 20, H-108)
        draw_text(screen, f"{sim['v_init']:.0f} km/s", FNT_MD, C.GLOSA_ON, 210, H-112)
        pygame.draw.rect(screen,(40,50,65),(SLIDER_X, SLIDER_Y, SLIDER_W, SLIDER_H), border_radius=4)
        pct = (sim['v_init']-Config.V_MIN_KMH)/(Config.V_MAX_KMH-Config.V_MIN_KMH)
        pygame.draw.rect(screen, C.GLOSA_ON, (SLIDER_X, SLIDER_Y, int(SLIDER_W*pct), SLIDER_H), border_radius=4)
        sx_knob = SLIDER_X + int(SLIDER_W*pct)
        pygame.draw.circle(screen, C.WHITE, (sx_knob, SLIDER_Y+SLIDER_H//2), 9)
        pygame.draw.circle(screen, C.GLOSA_ON, (sx_knob, SLIDER_Y+SLIDER_H//2), 7)

        # Howa düwmeleri
        WBTNS = [('1:Açyk','clear',(255,220,80)),('2:Ýagyş','rain',(100,160,255)),('3:Gar','snow',(200,210,255)),('4:Duman','fog',(170,175,185))]
        for i,(lbl,key,col) in enumerate(WBTNS):
            bx3 = 20 + i*115; by3 = H-72
            active = sim['weather']==key
            bg = (15,20,35) if not active else (col[0]//5, col[1]//5, col[2]//5)
            draw_rounded_rect(screen, bg, (bx3,by3,108,22), radius=5)
            bc = col if active else C.MUTED
            pygame.draw.rect(screen, bc, (bx3,by3,108,22), 1, border_radius=5)
            draw_text(screen, lbl, FNT_SM, bc, bx3+54, by3+5, align='center')

        # Gündüz/Gije belgisi
        is_night_now = day_t >= 0.4 and day_t <= 0.9
        gece_c = (80,100,200) if is_night_now else (240,200,60)
        gece_txt = "GIJE" if is_night_now else "GÜNDÜZ"
        draw_text(screen, gece_txt, FNT_MD, gece_c, 490, H-108, align='center')

        # Kamera
        cam_lbl = "Kamera: ARKA [C]" if sim['camera_mode']=='back' else "Kamera: ÖŇ  [C]"
        draw_text(screen, cam_lbl, FNT_TTL, C.CYAN, 490, H-82, align='center')

        # SPACE / R düwmesi
        if not sim['running']:
            if sim['finished']:
                btn_txt = "SPACE — Täzele"
                btn_c = C.GOLD
            else:
                btn_txt = "SPACE — Başla"
                btn_c = C.GLOSA_ON
        else:
            btn_txt = "SPACE — Sakla"
            btn_c = C.ORANGE
        draw_text(screen, btn_txt, FNT_MD, btn_c, 490, H-55, align='center')
        draw_text(screen, "R=Täzele  H=Kömek", FNT_SM, C.MUTED, 490, H-32, align='center')

        # ─── Ýol progress ─────────────────────────────────
        PB_X=260; PB_Y=H-50; PB_W=W-520; PB_H=14
        draw_panel(screen, PB_X-5, PB_Y-22, PB_W+10, 44, alpha=180)
        draw_text(screen,"Ýoluň progressi", FNT_SM, C.MUTED, PB_X, PB_Y-20)
        pygame.draw.rect(screen,(30,40,55),(PB_X,PB_Y,PB_W,PB_H),border_radius=7)
        prog = min(1.0, sim['x']/Config.TOTAL)
        if prog > 0:
            pg = pygame.Surface((int(PB_W*prog), PB_H), pygame.SRCALPHA)
            pg.fill((30,200,80,230))
            screen.blit(pg,(PB_X,PB_Y))
        pygame.draw.rect(screen,(60,80,100),(PB_X,PB_Y,PB_W,PB_H),1,border_radius=7)
        # Swetafor nokatlar
        for tl in lights:
            tp = tl.pos/Config.TOTAL
            tx = PB_X + int(PB_W*tp)
            st2,_ = tl.get_state(sim['t'])
            pygame.draw.circle(screen, C.GREEN if st2=='green' else C.RED, (tx,PB_Y+PB_H//2), 5)
        # % gorkeziji
        draw_text(screen, f"{prog*100:.0f}%", FNT_TTL, C.WHITE, PB_X+PB_W+8, PB_Y)

        # Galan ýol (uly)
        draw_text(screen, f"Galan ýol: {galan_yol:.0f} m", FNT_MD, C.CYAN, PB_X, PB_Y-40)

        # ─── LOG ──────────────────────────────────────────
        logger.draw(screen, W-210, H-130, 198, 118)

        # ─── Başlyk (ýokarda) ─────────────────────────────
        draw_panel(screen, W//2-280, 0, 560, 30, alpha=200, color=(4,8,20))
        draw_text(screen,
            "GLOSA 3D SIMULÝASIÝA   |   Şanazar Sarjaýew   |   TDU 2026",
            FNT_TTL, C.GOLD, W//2, 7, align='center')

        # Tamamlanma ekrany
        if sim['finished']:
            overlay = pygame.Surface((W,H), pygame.SRCALPHA)
            overlay.fill((4,8,20,180))
            screen.blit(overlay,(0,0))
            draw_panel(screen,W//2-280,H//2-130,560,260,alpha=240)
            draw_text(screen,"SIMULÝASIÝA TAMAMLANDY!",FNT_XL,C.GOLD,W//2,H//2-115,align='center')
            pygame.draw.line(screen,C.GOLD,(W//2-220,H//2-80),(W//2+220,H//2-80),1)
            res_data = [
                ("Säginme sany",   f"{sim['stops']}",                                   C.RED),
                ("Ýangyç",         f"{sim['fuel']*1000:.2f} ml",                         C.GOLD),
                ("Tygşytlylyk",    f"{saved_pct:.1f}%",                                  C.GLOSA_ON),
                ("Geçilen ýol",    f"{Config.TOTAL:.0f} m",                              C.CYAN),
                ("Jemi wagt",      f"{sim['t']:.0f} s",                                  C.MUTED),
            ]
            for i,(lbl,val,col) in enumerate(res_data):
                y = H//2 - 62 + i*36
                draw_text(screen, lbl+":", FNT_LG, C.MUTED, W//2-20, y, align='right')
                draw_text(screen, val,     FNT_LG, col,      W//2+20, y)
            draw_text(screen,"[SPACE] — Täzele  |  [ESC] — Çyk",FNT_MD,C.MUTED,W//2,H//2+110,align='center')

        # Help
        if ui['show_help'] and ui['help_timer'] > 0:
            ui['help_timer'] -= 1
            if ui['help_timer'] > 0:
                alpha = min(255, ui['help_timer'] * 4)
                draw_panel(screen,W//2-200,H-160,400,48,alpha=min(200,alpha))
                draw_text(screen,"ÝOLBELET: SPACE=Başla  G=GLOSA  C=Kamera  1-4=Howa  R=Täzele",
                          FNT_SM, (*C.MUTED[:3], alpha) if False else C.MUTED, W//2,H-148,align='center')

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
