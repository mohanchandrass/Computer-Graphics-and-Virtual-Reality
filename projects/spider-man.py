"""
swing_city_demo.py

Requirements:
    pip install PyOpenGL glfw

Single-file OpenGL Spider-Man Endless City Swing Demo.
Uses immediate-mode OpenGL (glBegin/glEnd) via PyOpenGL + GLFW.
"""

import math
import random

import glfw
from OpenGL.GL import *

# ---------------------------------------------------------------------------
# Window / Global Configuration
# ---------------------------------------------------------------------------
WIDTH, HEIGHT = 1280, 720
random.seed(3)

# Traversal & Swing Timing
SWING_PERIOD = 2.0
OMEGA = 2.0 * math.pi / SWING_PERIOD
HALF_PERIOD = SWING_PERIOD / 2.0

# Uniform Parallax City Speeds (World units per second moving right-to-left)
STAR_SPEED = 0.010
CLOUD_SPEED = 0.030
FAR_SPEED = 0.12
MID_SPEED = 0.28
FG_SPEED = 0.55

TRAIL_MAX = 4

MOON_POS = (0.65, 0.72)
MOON_R = 0.080


# ---------------------------------------------------------------------------
# Math Helpers
# ---------------------------------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def lerp(a, b, u):
    return a + (b - a) * u


# ---------------------------------------------------------------------------
# Precomputed Geometry Primitives
# ---------------------------------------------------------------------------
CIRCLE_SEGMENTS = 20
UNIT_CIRCLE = [
    (math.cos(2 * math.pi * i / CIRCLE_SEGMENTS), math.sin(2 * math.pi * i / CIRCLE_SEGMENTS))
    for i in range(CIRCLE_SEGMENTS + 1)
]


def rect(x, y, w, h):
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + w, y)
    glVertex2f(x + w, y + h)
    glVertex2f(x, y + h)
    glEnd()


def triangle(x1, y1, x2, y2, x3, y3):
    glBegin(GL_TRIANGLES)
    glVertex2f(x1, y1)
    glVertex2f(x2, y2)
    glVertex2f(x3, y3)
    glEnd()


def circle(cx, cy, ry, rx=None):
    rx = ry if rx is None else rx
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(cx, cy)
    for ux, uy in UNIT_CIRCLE:
        glVertex2f(cx + ux * rx, cy + uy * ry)
    glEnd()


# ---------------------------------------------------------------------------
# Layer 1: Blue Night Sky & Twinkling Stars
# ---------------------------------------------------------------------------
NUM_STARS = 220
stars = [
    {
        "x": random.uniform(-1.5, 1.5),
        "y": random.uniform(-0.1, 1.1),
        "base": random.uniform(0.5, 1.0),
        "speed": random.uniform(2.0, 5.0),
        "phase": random.uniform(0.0, 2 * math.pi),
        "size": random.uniform(0.002, 0.0045),
    }
    for _ in range(NUM_STARS)
]


def update_stars(dt):
    for s in stars:
        s["x"] -= STAR_SPEED * dt
        if s["x"] < -1.5:
            s["x"] += 3.0


def draw_stars(t):
    for s in stars:
        twinkle = 0.5 + 0.5 * math.sin(t * s["speed"] + s["phase"])
        br = s["base"] * (0.4 + 0.6 * twinkle)
        glColor4f(0.90, 0.95, 1.0, br)
        r = s["size"] * (0.8 + 0.4 * twinkle)
        rect(s["x"] - r, s["y"] - r, r * 2, r * 2)


def draw_sky():
    glBegin(GL_QUADS)
    glColor3f(0.02, 0.04, 0.18)
    glVertex2f(-1.5, 1.2)
    glVertex2f(1.5, 1.2)
    glColor3f(0.08, 0.18, 0.42)
    glVertex2f(1.5, -1.2)
    glVertex2f(-1.5, -1.2)
    glEnd()

    glBegin(GL_QUADS)
    glColor4f(0.15, 0.35, 0.65, 0.0)
    glVertex2f(-1.5, -0.2)
    glVertex2f(1.5, -0.2)
    glColor4f(0.15, 0.35, 0.65, 0.22)
    glVertex2f(1.5, -1.2)
    glVertex2f(-1.5, -1.2)
    glEnd()


# ---------------------------------------------------------------------------
# Layer 2: Looping Moon Phase Transition & Clouds
# ---------------------------------------------------------------------------
def draw_moon(t):
    mx, my = MOON_POS
    
    # Outer Glow Ring
    for i in range(4, 0, -1):
        glColor4f(0.7, 0.85, 1.0, 0.03)
        circle(mx, my, MOON_R * (1.0 + 0.4 * i))

    # Full Light Disc
    glColor3f(0.95, 0.98, 1.0)
    circle(mx, my, MOON_R)

    # Dynamic Shadow Mask for Phase Transition (Crescent -> Half -> Full -> Crescent)
    phase_offset = math.sin(t * 0.25)  # Ranges -1.0 to 1.0
    shadow_x = mx + phase_offset * (MOON_R * 1.8)
    
    if abs(phase_offset) > 0.05:
        glColor3f(0.02, 0.04, 0.18)  # Matches zenith sky color
        circle(shadow_x, my, MOON_R * 0.95)


NUM_CLOUDS = 6
clouds = [
    {
        "x": random.uniform(-1.5, 1.5),
        "y": random.uniform(0.50, 0.85),
        "scale": random.uniform(0.10, 0.18),
        "alpha": random.uniform(0.10, 0.20),
    }
    for _ in range(NUM_CLOUDS)
]


def update_clouds(dt):
    for c in clouds:
        c["x"] -= CLOUD_SPEED * dt
        if c["x"] < -1.5:
            c["x"] += 3.0


def draw_clouds():
    for c in clouds:
        x, y, s = c["x"], c["y"], c["scale"]
        glColor4f(0.5, 0.68, 0.88, c["alpha"])
        circle(x, y, s * 0.5, s)
        circle(x + s * 0.6, y + 0.01, s * 0.4, s * 0.75)
        circle(x - s * 0.5, y, s * 0.38, s * 0.70)


# ---------------------------------------------------------------------------
# Layers 3-5: City Skyline (Anchored to Ground + Twinkling Windows)
# ---------------------------------------------------------------------------
ROOFTOP_KINDS = ("flat", "point", "antenna", "step")


def make_building(x, w_range, h_range, water_tower_chance):
    w = random.uniform(*w_range)
    h = random.uniform(*h_range)
    rooftop = random.choice(ROOFTOP_KINDS)

    rows = max(2, int(h / 0.045))
    cols = max(2, int(w / 0.028))
    windows = []
    for r in range(rows):
        for c in range(cols):
            if random.random() < 0.40:
                continue
            wx = 0.12 * w + c * (0.76 * w) / max(1, cols - 1)
            wy = 0.08 * h + r * (0.86 * h) / max(1, rows - 1)
            lit = random.random() < 0.80
            freq = random.uniform(2.0, 6.0)
            phase = random.uniform(0.0, 2 * math.pi)
            windows.append((wx, wy, lit, freq, phase))

    return {
        "x": x, "w": w, "h": h,
        "rooftop": rooftop,
        "windows": windows,
        "tower": random.random() < water_tower_chance,
    }


def fill_layer(x_start, x_end, w_range, h_range, water_tower_chance):
    out = []
    x = x_start
    while x < x_end:
        b = make_building(x, w_range, h_range, water_tower_chance)
        out.append(b)
        x += b["w"]
    return out


def make_layer(w_range, h_range, water_tower_chance=0.0):
    return {
        "buildings": fill_layer(-1.8, 1.8, w_range, h_range, water_tower_chance),
        "w_range": w_range,
        "h_range": h_range,
        "wtc": water_tower_chance,
    }


far_layer = make_layer((0.10, 0.20), (0.25, 0.45))
mid_layer = make_layer((0.12, 0.22), (0.40, 0.65))
fg_layer = make_layer((0.15, 0.32), (0.55, 0.95), water_tower_chance=0.30)


def scroll_layer(layer, speed, dt):
    buildings = layer["buildings"]
    for b in buildings:
        b["x"] -= speed * dt
    while buildings and buildings[0]["x"] + buildings[0]["w"] < -2.0:
        buildings.pop(0)
        rightmost = buildings[-1]["x"] + buildings[-1]["w"] if buildings else 2.0
        buildings.append(make_building(rightmost, layer["w_range"], layer["h_range"], layer["wtc"]))


def draw_rooftop(x, y_top, w, kind):
    if kind == "point":
        triangle(x, y_top, x + w, y_top, x + w * 0.5, y_top + w * 0.5)
    elif kind == "antenna":
        rect(x + w * 0.46, y_top, w * 0.08, w * 0.45)
        circle(x + w * 0.50, y_top + w * 0.45, w * 0.04)
    elif kind == "step":
        rect(x + w * 0.18, y_top, w * 0.64, w * 0.12)
        rect(x + w * 0.35, y_top + w * 0.12, w * 0.30, w * 0.10)


def draw_water_tower(x, y_top, w):
    tx = x + w * 0.65
    glColor3f(0.06, 0.07, 0.10)
    rect(tx - w * 0.05, y_top, w * 0.10, w * 0.08)
    circle(tx, y_top + w * 0.14, w * 0.08)
    triangle(tx - w * 0.08, y_top + w * 0.18, tx + w * 0.08, y_top + w * 0.18, tx, y_top + w * 0.28)


def draw_layer(layer, base_color, window_color, t):
    r, g, b = base_color
    wr, wg, wb = window_color
    for bd in layer["buildings"]:
        x, w, h = bd["x"], bd["w"], bd["h"]
        y_bottom = -1.2
        y_top = -1.0 + h
        actual_height = y_top - y_bottom
        
        glColor3f(r, g, b)
        rect(x, y_bottom, w, actual_height)
        draw_rooftop(x, y_top, w, bd["rooftop"])
        if bd["tower"]:
            draw_water_tower(x, y_top, w)
            
        for wx, wy, lit, freq, phase in bd["windows"]:
            if lit:
                twinkle = 0.70 + 0.30 * math.sin(t * freq + phase)
                glColor3f(wr * twinkle, wg * twinkle, wb * twinkle)
                rect(x + wx, -1.0 + wy, 0.009, 0.015)


# ---------------------------------------------------------------------------
# Particles
# ---------------------------------------------------------------------------
NUM_PARTICLES = 18
particles = [
    {
        "x": random.uniform(-1.5, 1.5),
        "y": random.uniform(-0.9, 1.0),
        "vx": random.uniform(0.3, 0.6),
        "size": random.uniform(0.002, 0.004),
        "alpha": random.uniform(0.12, 0.30),
    }
    for _ in range(NUM_PARTICLES)
]


def update_particles(dt):
    for p in particles:
        p["x"] -= p["vx"] * dt
        if p["x"] < -1.5:
            p["x"] = 1.5
            p["y"] = random.uniform(-0.9, 1.0)


def draw_particles():
    for p in particles:
        glColor4f(0.85, 0.92, 1.0, p["alpha"])
        rect(p["x"] - p["size"], p["y"] - p["size"], p["size"] * 2, p["size"] * 2)


# ---------------------------------------------------------------------------
# Web Rope Rendering (Extends Out of Upper Window Boundary)
# ---------------------------------------------------------------------------
def draw_rope(ax, ay, hx, hy, sag_amount):
    mx = (ax + hx) * 0.5
    my = (ay + hy) * 0.5 - sag_amount
    glColor3f(0.95, 0.98, 1.0)
    glLineWidth(2.5)
    glBegin(GL_LINE_STRIP)
    segs = 10
    for i in range(segs + 1):
        u = i / segs
        iu = 1.0 - u
        x = iu * iu * ax + 2 * iu * u * mx + u * u * hx
        y = iu * iu * ay + 2 * iu * u * my + u * u * hy
        glVertex2f(x, y)
    glEnd()


# ---------------------------------------------------------------------------
# Proportional Side-Profile Spider-Man (Alternating Dual Arm System)
# ---------------------------------------------------------------------------
def draw_silhouette(x, y, alpha):
    glPushMatrix()
    glTranslatef(x, y, 0)
    glColor4f(0.9, 0.1, 0.15, alpha)
    circle(0, 0.0, 0.045, 0.028)
    glPopMatrix()


def draw_spider_man(x, y, pose_angle, vy, t, active_hand):
    """
    Renders Spider-Man in SIDE PROFILE facing right with realistic, non-boxy 
    retro proportions. Arms visibly swap between foreground and background.
    Returns the exact world coordinates of the currently active web-shooting hand.
    """
    torso_deg = math.degrees(pose_angle)
    leg_tuck = clamp(vy * 0.35, -1.0, 1.0)

    glPushMatrix()
    glTranslatef(x, y, 0)
    glRotatef(torso_deg, 0, 0, 1)

    # --- 1. MASK HEAD (Side Profile) ---
    glColor3f(0.92, 0.08, 0.12)  # Classic Spidey Red
    circle(0.004, 0.095, 0.021, 0.017)

    # Distinct Triangular White Mask Eye Lens with Black Rim
    glColor3f(0.05, 0.05, 0.08)  # Black border
    triangle(0.002, 0.103, 0.020, 0.096, 0.006, 0.087)
    glColor3f(0.98, 0.98, 0.98)  # White lens
    triangle(0.004, 0.101, 0.017, 0.096, 0.007, 0.089)

    # --- 2. TAPERED ATHLETIC TORSO ---
    # Slim blue waist/back section
    glColor3f(0.08, 0.18, 0.72)
    triangle(-0.012, 0.075, -0.012, -0.025, 0.008, 0.020)
    rect(-0.012, -0.025, 0.018, 0.050)

    # Red chest section (angled/contoured)
    glColor3f(0.92, 0.08, 0.12)
    triangle(0.006, 0.075, 0.006, -0.020, 0.022, 0.035)

    # Chest Spider Emblem
    glColor3f(0.05, 0.05, 0.08)
    circle(0.008, 0.030, 0.005, 0.003)

    # --- 3. ALTERNATING DUAL ARMS ---
    glLineWidth(3.0)

    # Define Left and Right Arm Positions
    # Reaching arm (Up/Forward holding web):
    reach_start = (0.008, 0.060)
    reach_elbow = (0.032, 0.105)
    reach_hand  = (0.055, 0.155)

    # Cocked arm (Back in web shooter pose):
    cock_start = (-0.004, 0.050)
    cock_elbow = (-0.028, 0.020)
    cock_hand  = (-0.020, -0.025)

    if active_hand == -1:
        # Left Arm is Active (Foreground - Reaching)
        l_color, l_start, l_elbow, l_hand = (0.92, 0.08, 0.12), reach_start, reach_elbow, reach_hand
        r_color, r_start, r_elbow, r_hand = (0.65, 0.05, 0.08), cock_start, cock_elbow, cock_hand
    else:
        # Right Arm is Active (Foreground - Reaching)
        r_color, r_start, r_elbow, r_hand = (0.92, 0.08, 0.12), reach_start, reach_elbow, reach_hand
        l_color, l_start, l_elbow, l_hand = (0.65, 0.05, 0.08), cock_start, cock_elbow, cock_hand

    # Render Background Arm First
    back_color = r_color if active_hand == -1 else l_color
    back_start = r_start if active_hand == -1 else l_start
    back_elbow = r_elbow if active_hand == -1 else l_elbow
    back_hand  = r_hand  if active_hand == -1 else l_hand

    glColor3f(*back_color)
    glBegin(GL_LINES)
    glVertex2f(*back_start); glVertex2f(*back_elbow)
    glVertex2f(*back_elbow); glVertex2f(*back_hand)
    glEnd()

    # --- 4. ATHLETIC LEGS ---
    knee_y = -0.090 + 0.025 * leg_tuck
    foot_y = -0.155 - 0.025 * max(0.0, -leg_tuck)

    glBegin(GL_LINES)
    # Background Leg
    glColor3f(0.06, 0.14, 0.58)
    glVertex2f(-0.008, -0.025); glVertex2f(-0.028 - 0.01 * leg_tuck, knee_y - 0.01)
    glColor3f(0.65, 0.05, 0.08)
    glVertex2f(-0.028 - 0.01 * leg_tuck, knee_y - 0.01); glVertex2f(-0.038, foot_y + 0.02)

    # Foreground Leg
    glColor3f(0.08, 0.18, 0.72)
    glVertex2f(0.004, -0.025); glVertex2f(0.024 + 0.018 * leg_tuck, knee_y)
    glColor3f(0.92, 0.08, 0.12)
    glVertex2f(0.024 + 0.018 * leg_tuck, knee_y); glVertex2f(0.018, foot_y)
    glEnd()

    # Render Foreground Arm
    fore_color = l_color if active_hand == -1 else r_color
    fore_start = l_start if active_hand == -1 else r_start
    fore_elbow = l_elbow if active_hand == -1 else r_elbow
    fore_hand  = l_hand  if active_hand == -1 else r_hand

    glColor3f(*fore_color)
    glBegin(GL_LINES)
    glVertex2f(*fore_start); glVertex2f(*fore_elbow)
    glVertex2f(*fore_elbow); glVertex2f(*fore_hand)
    glEnd()

    # Hands
    glColor3f(0.92, 0.08, 0.12)
    circle(fore_hand[0], fore_hand[1], 0.006)
    glColor3f(0.65, 0.05, 0.08)
    circle(back_hand[0], back_hand[1], 0.005)

    glPopMatrix()

    # Calculate and return active hand position transformed into world space
    rad = math.radians(torso_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    active_local_x, active_local_y = reach_hand
    
    world_hand_x = x + (active_local_x * cos_a - active_local_y * sin_a)
    world_hand_y = y + (active_local_x * sin_a + active_local_y * cos_a)
    
    return world_hand_x, world_hand_y


# ---------------------------------------------------------------------------
# State Management & Forward Physics Engine
# ---------------------------------------------------------------------------
def init_state():
    return {
        "t": 0.0,
        "prev_hy": -0.1,
        "anchor_x": 0.65,
        "anchor_y": 1.15,         # Anchored OUT OF WINDOW top boundary (> 1.0)
        "swing_idx": -1,
        "active_hand": -1,        # -1 = Left Hand, 1 = Right Hand
        "cam_y": 0.0,
        "trail": [(0.0, 0.0)] * TRAIL_MAX,
        "trail_head": 0,
        "trail_count": 0,
        "trail_timer": 0.0,
        "hx": 0.0,                # Spider-Man fixed horizontally at screen center X = 0.0
        "hy": -0.1,
        "pose_angle": 0.0,
        "vy": 0.0,
        "sag": 0.03,
    }


def update_world(state, dt):
    t = state["t"]

    phase = (t % HALF_PERIOD) / HALF_PERIOD
    
    # Character stays horizontally centered
    hx = 0.0
    
    # Vertical pendulum motion
    hy = -0.22 + 0.32 * math.cos(phase * math.pi - math.pi / 2)
    
    # Forward torso lean
    pose_angle = -0.20 * math.sin(phase * math.pi)

    # Active web anchor glides right-to-left
    state["anchor_x"] -= FG_SPEED * dt
    
    # Switch active hand and spawn next anchor off-screen above window
    idx = int(t // HALF_PERIOD)
    if idx != state["swing_idx"]:
        state["swing_idx"] = idx
        state["active_hand"] = -1 if (idx % 2 == 0) else 1
        state["anchor_x"] = random.uniform(0.55, 0.80)
        state["anchor_y"] = random.uniform(1.10, 1.25)  # Strictly above upper window frame

    vy = (hy - state["prev_hy"]) / max(dt, 1e-4)
    state["prev_hy"] = hy

    state["hx"], state["hy"] = hx, hy
    state["pose_angle"] = pose_angle
    state["vy"] = vy
    state["sag"] = 0.025 + 0.018 * math.sin(phase * math.pi)
    state["t"] = t + dt

    # Camera tracking
    smooth = 1.0 - math.exp(-6.0 * dt)
    state["cam_y"] += ((hy * 0.05) - state["cam_y"]) * smooth

    # Ring buffer trail silhouette
    state["trail_timer"] += dt
    if state["trail_timer"] >= 0.05:
        state["trail_timer"] = 0.0
        head = state["trail_head"]
        state["trail"][head] = (hx, hy)
        state["trail_head"] = (head + 1) % TRAIL_MAX
        if state["trail_count"] < TRAIL_MAX:
            state["trail_count"] += 1

    # Scroll city background
    scroll_layer(far_layer, FAR_SPEED, dt)
    scroll_layer(mid_layer, MID_SPEED, dt)
    scroll_layer(fg_layer, FG_SPEED, dt)
    update_stars(dt)
    update_clouds(dt)
    update_particles(dt)


# ---------------------------------------------------------------------------
# Main Application Loop
# ---------------------------------------------------------------------------
def main():
    if not glfw.init():
        return
    win = glfw.create_window(WIDTH, HEIGHT, "Classic Spider-Man Endless Swing", None, None)
    if not win:
        glfw.terminate()
        return
    glfw.make_context_current(win)
    glfw.swap_interval(1)

    fbw, fbh = glfw.get_framebuffer_size(win)
    glViewport(0, 0, fbw, fbh)
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glClearColor(0.02, 0.04, 0.18, 1.0)

    state = init_state()
    last_time = glfw.get_time()

    while not glfw.window_should_close(win):
        glfw.poll_events()
        now = glfw.get_time()
        dt = min(0.033, now - last_time)
        last_time = now

        update_world(state, dt)
        glClear(GL_COLOR_BUFFER_BIT)

        glLoadIdentity()
        glTranslatef(0.0, state["cam_y"], 0.0)

        # 1. Celestial & Sky (Star Twinkle & Moon Loop Cycle)
        draw_sky()
        draw_stars(state["t"])
        draw_moon(state["t"])
        draw_clouds()
        
        # 2. City Layers with Twinkling Windows
        draw_layer(far_layer, (0.05, 0.09, 0.22), (0.42, 0.52, 0.70), state["t"])
        draw_layer(mid_layer, (0.04, 0.07, 0.18), (0.78, 0.70, 0.45), state["t"])
        draw_layer(fg_layer, (0.02, 0.04, 0.12), (0.98, 0.85, 0.42), state["t"])

        # 3. Particles
        draw_particles()

        # 4. Motion Trail
        count = state["trail_count"]
        head = state["trail_head"]
        for i in range(count):
            idx = (head - count + i) % TRAIL_MAX
            tx, ty = state["trail"][idx]
            draw_silhouette(tx, ty, (i + 1) / (count + 1) * 0.15)

        # 5. Render Hero Character & Compute Active Web Hand Attachment Point
        hand_x, hand_y = draw_spider_man(
            state["hx"], state["hy"], 
            state["pose_angle"], state["vy"], 
            state["t"], state["active_hand"]
        )

        # 6. Web Line (Connects active hand directly out of top window border)
        draw_rope(
            state["anchor_x"], state["anchor_y"], 
            hand_x, hand_y, 
            state["sag"]
        )

        glfw.swap_buffers(win)

    glfw.terminate()


if __name__ == "__main__":
    main()