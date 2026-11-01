import sys
import os
import math
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# EXPERIMENT 9: INTERACTIVE 3D SCENE
# ============================================================
# Demonstrates a fully interactive 3D virtual environment:
# 1. 3D Scene Architecture: Ground grid, obstacles, lighting
# 2. Player Controller: 3D character movement, rotation & gravity jump
# 3. Third-Person Camera: Smoothly follows player in 3D world space
# 4. Interactive Collectibles: 5 rotating animated gems with pickup logic
# 5. On-Screen HUD: Collectible counter, player telemetry & controls
# ============================================================

WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 750

# Player State
player_x = 0.0
player_y = 0.5  # Grounded at y = 0.5 (cube center)
player_z = 2.0
player_angle = 0.0
player_vy = 0.0
is_grounded = True
GRAVITY = 24.0
JUMP_FORCE = 8.5
MOVE_SPEED = 7.0
ROT_SPEED = 120.0

# Collectibles (5 rotating items)
collectibles = [
    {"pos": [-4.0, 0.8, -3.0], "collected": False, "color": (1.0, 0.85, 0.15)}, # Gold
    {"pos": [ 4.0, 0.8, -3.0], "collected": False, "color": (0.2, 0.95, 1.00)}, # Cyan
    {"pos": [-3.5, 0.8,  3.5], "collected": False, "color": (1.0, 0.25, 0.75)}, # Magenta
    {"pos": [ 3.5, 0.8,  3.5], "collected": False, "color": (0.3, 1.00, 0.40)}, # Emerald
    {"pos": [ 0.0, 0.8, -6.5], "collected": False, "color": (1.0, 0.45, 0.10)}, # Orange
]

# Obstacles (x, z, width, depth, height, color)
obstacles = [
    (-2.0, -1.0, 1.5, 1.5, 1.8, (0.55, 0.25, 0.65)),
    ( 2.5, -0.5, 1.2, 2.0, 1.5, (0.20, 0.60, 0.70)),
    (-1.0, -4.5, 3.0, 1.0, 1.4, (0.75, 0.45, 0.20)),
    ( 2.0,  2.0, 1.5, 1.5, 1.6, (0.35, 0.55, 0.35)),
]

score = 0
total_items = len(collectibles)
anim_time = 0.0

keys = {}


def reset_scene():
    global player_x, player_y, player_z, player_angle, player_vy, is_grounded, score
    player_x = 0.0
    player_y = 0.5
    player_z = 2.0
    player_angle = 0.0
    player_vy = 0.0
    is_grounded = True
    score = 0
    for c in collectibles:
        c["collected"] = False


def draw_cube(size=1.0):
    s = size / 2.0
    glBegin(GL_QUADS)
    # Front
    glNormal3f(0, 0, 1)
    glVertex3f(-s, -s,  s); glVertex3f( s, -s,  s); glVertex3f( s,  s,  s); glVertex3f(-s,  s,  s)
    # Back
    glNormal3f(0, 0, -1)
    glVertex3f(-s, -s, -s); glVertex3f(-s,  s, -s); glVertex3f( s,  s, -s); glVertex3f( s, -s, -s)
    # Top
    glNormal3f(0, 1, 0)
    glVertex3f(-s,  s, -s); glVertex3f(-s,  s,  s); glVertex3f( s,  s,  s); glVertex3f( s,  s, -s)
    # Bottom
    glNormal3f(0, -1, 0)
    glVertex3f(-s, -s, -s); glVertex3f( s, -s, -s); glVertex3f( s, -s,  s); glVertex3f(-s, -s,  s)
    # Right
    glNormal3f(1, 0, 0)
    glVertex3f( s, -s, -s); glVertex3f( s,  s, -s); glVertex3f( s,  s,  s); glVertex3f( s, -s,  s)
    # Left
    glNormal3f(-1, 0, 0)
    glVertex3f(-s, -s, -s); glVertex3f(-s, -s,  s); glVertex3f(-s,  s,  s); glVertex3f(-s,  s, -s)
    glEnd()


def draw_gem():
    """Draws a 3D faceted diamond gem."""
    r = 0.4
    h = 0.6
    glBegin(GL_TRIANGLES)
    # Top pyramid (4 faces)
    faces = [
        ((0, h, 0), (-r, 0, -r), ( r, 0, -r)),
        ((0, h, 0), ( r, 0, -r), ( r, 0,  r)),
        ((0, h, 0), ( r, 0,  r), (-r, 0,  r)),
        ((0, h, 0), (-r, 0,  r), (-r, 0, -r)),
        # Bottom pyramid (4 faces)
        ((0, -h, 0), ( r, 0, -r), (-r, 0, -r)),
        ((0, -h, 0), ( r, 0,  r), ( r, 0, -r)),
        ((0, -h, 0), (-r, 0,  r), ( r, 0,  r)),
        ((0, -h, 0), (-r, 0, -r), (-r, 0,  r)),
    ]
    for v1, v2, v3 in faces:
        # Simple face normal
        ax, ay, az = v2[0] - v1[0], v2[1] - v1[1], v2[2] - v1[2]
        bx, by, bz = v3[0] - v1[0], v3[1] - v1[1], v3[2] - v1[2]
        nx = ay * bz - az * by
        ny = az * bx - ax * bz
        nz = ax * by - ay * bx
        nl = math.sqrt(nx*nx + ny*ny + nz*nz) or 1.0
        glNormal3f(nx/nl, ny/nl, nz/nl)
        glVertex3fv(v1)
        glVertex3fv(v2)
        glVertex3fv(v3)
    glEnd()


def draw_ground():
    """Draws a stylish checkered arena floor."""
    grid_size = 12
    step = 1.0
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    for x in range(-grid_size, grid_size):
        for z in range(-grid_size, grid_size):
            if (x + z) % 2 == 0:
                glColor3f(0.16, 0.19, 0.25)
            else:
                glColor3f(0.12, 0.14, 0.20)
            glVertex3f(x * step, 0.0, z * step)
            glVertex3f((x + 1) * step, 0.0, z * step)
            glVertex3f((x + 1) * step, 0.0, (z + 1) * step)
            glVertex3f(x * step, 0.0, (z + 1) * step)
    glEnd()

    # Arena boundary rails
    glColor3f(0.35, 0.45, 0.65)
    glLineWidth(3.0)
    b = grid_size * step
    glBegin(GL_LINE_LOOP)
    glVertex3f(-b, 0.1, -b)
    glVertex3f( b, 0.1, -b)
    glVertex3f( b, 0.1,  b)
    glVertex3f(-b, 0.1,  b)
    glEnd()


def draw_scene():
    glClearColor(0.05, 0.06, 0.09, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # Lighting setup
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glLightfv(GL_LIGHT0, GL_POSITION, [8.0, 12.0, 10.0, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.98, 0.90, 1.0])
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.25, 0.28, 0.35, 1.0])

    # Viewport & Projection
    glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(50.0, WINDOW_WIDTH / WINDOW_HEIGHT, 0.1, 100.0)

    # Camera Follows Player (3rd Person Orbit)
    cam_dist = 6.0
    cam_height = 3.2
    rad = math.radians(player_angle)
    cam_x = player_x - cam_dist * math.sin(rad)
    cam_z = player_z + cam_dist * math.cos(rad)
    cam_y = player_y + cam_height

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(cam_x, cam_y, cam_z,
              player_x, player_y + 0.6, player_z,
              0.0, 1.0, 0.0)

    # 1. Ground Plane
    draw_ground()

    # 2. Obstacles
    for ox, oz, w, d, h, col in obstacles:
        glPushMatrix()
        glTranslatef(ox, h / 2.0, oz)
        glScalef(w, h, d)
        glColor3fv(col)
        draw_cube(1.0)
        glPopMatrix()

    # 3. Rotating Collectibles
    for c in collectibles:
        if not c["collected"]:
            glPushMatrix()
            px, py, pz = c["pos"]
            bob = 0.12 * math.sin(anim_time * 3.5 + px)
            glTranslatef(px, py + bob, pz)
            glRotatef(anim_time * 75.0, 0.0, 1.0, 0.0)
            glColor3fv(c["color"])
            draw_gem()
            glPopMatrix()

    # 4. Player Character (Avatar Cube with Directional Marker)
    glPushMatrix()
    glTranslatef(player_x, player_y, player_z)
    glRotatef(player_angle, 0.0, 1.0, 0.0)

    # Body
    glColor3f(0.20, 0.70, 1.00)
    draw_cube(0.9)

    # Direction Eyes / Face Visor
    glColor3f(1.0, 0.9, 0.2)
    glPushMatrix()
    glTranslatef(0.0, 0.15, -0.46)
    glScalef(0.6, 0.25, 0.05)
    draw_cube(1.0)
    glPopMatrix()

    glPopMatrix()

    glDisable(GL_LIGHTING)


def update_physics(dt):
    global player_x, player_y, player_z, player_angle, player_vy, is_grounded, score

    # Rotation
    if keys.get(glfw.KEY_A, False) or keys.get(glfw.KEY_LEFT, False):
        player_angle += ROT_SPEED * dt
    if keys.get(glfw.KEY_D, False) or keys.get(glfw.KEY_RIGHT, False):
        player_angle -= ROT_SPEED * dt

    # Forward / Backward Movement
    move_dir = 0.0
    if keys.get(glfw.KEY_W, False) or keys.get(glfw.KEY_UP, False):
        move_dir -= 1.0
    if keys.get(glfw.KEY_S, False) or keys.get(glfw.KEY_DOWN, False):
        move_dir += 1.0

    if move_dir != 0.0:
        rad = math.radians(player_angle)
        dx = -move_dir * MOVE_SPEED * dt * math.sin(rad)
        dz = move_dir * MOVE_SPEED * dt * math.cos(rad)
        player_x += dx
        player_z += dz

    # Jump & Gravity
    if (keys.get(glfw.KEY_SPACE, False)) and is_grounded:
        player_vy = JUMP_FORCE
        is_grounded = False

    if not is_grounded:
        player_y += player_vy * dt
        player_vy -= GRAVITY * dt
        if player_y <= 0.5:
            player_y = 0.5
            player_vy = 0.0
            is_grounded = True

    # Collectible Collision Check
    for c in collectibles:
        if not c["collected"]:
            cx, cy, cz = c["pos"]
            dist = math.sqrt((player_x - cx)**2 + (player_z - cz)**2)
            if dist < 1.3:
                c["collected"] = True
                score += 1
                print(f"Collected gem! Score: {score}/{total_items}")


def add_hud_and_save(output_path):
    """Capture 3D scene and render a rich game HUD overlay."""
    glReadBuffer(GL_BACK)
    glFinish()
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WINDOW_WIDTH, WINDOW_HEIGHT), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
        font_score = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 26)
        font_info = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    except Exception:
        font_title = font_score = font_info = font_bold = ImageFont.load_default()

    # Top Header Banner
    draw.rectangle([(20, 16), (WINDOW_WIDTH - 20, 68)], fill=(16, 20, 30, 235), outline=(0, 180, 255), width=2)
    draw.text((36, 22), "EXPERIMENT 9: INTERACTIVE 3D SCENE", fill=(0, 210, 255), font=font_title)
    draw.text((36, 46), "Player Controller | 3rd-Person Camera Follow | 3D Obstacles | Animated Collectibles | Real-Time Physics", fill=(200, 215, 230), font=font_info)

    # Top Right: Score & Collectibles Counter Box
    draw.rectangle([(WINDOW_WIDTH - 270, 16), (WINDOW_WIDTH - 20, 105)], fill=(18, 26, 38, 240), outline=(255, 200, 50), width=2)
    draw.text((WINDOW_WIDTH - 255, 24), "COLLECTIBLES", fill=(255, 215, 60), font=font_bold)
    draw.text((WINDOW_WIDTH - 255, 48), f"{score} / {total_items} GEMS", fill=(255, 255, 255), font=font_score)
    status_text = "COLLECT ALL TO WIN" if score < total_items else "SCENE COMPLETED!"
    draw.text((WINDOW_WIDTH - 255, 82), status_text, fill=(80, 255, 140) if score == total_items else (255, 170, 80), font=font_info)

    # Bottom Left: Controls Guide
    draw.rectangle([(20, WINDOW_HEIGHT - 95), (450, WINDOW_HEIGHT - 18)], fill=(16, 20, 30, 235), outline=(70, 90, 120), width=1)
    draw.rectangle([(20, WINDOW_HEIGHT - 95), (450, WINDOW_HEIGHT - 70)], fill=(28, 36, 50))
    draw.text((32, WINDOW_HEIGHT - 90), "INTERACTIVE CONTROLS", fill=(120, 210, 255), font=font_bold)
    draw.text((32, WINDOW_HEIGHT - 65), "W / S or Up / Down  : Move Forward / Backward\nA / D or Left / Right : Rotate Player\nSpace : Jump  |  R : Reset Scene  |  Esc : Quit", fill=(220, 225, 235), font=font_info)

    # Bottom Right: Telemetry Box
    draw.rectangle([(WINDOW_WIDTH - 360, WINDOW_HEIGHT - 95), (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 18)], fill=(16, 20, 30, 235), outline=(70, 90, 120), width=1)
    draw.rectangle([(WINDOW_WIDTH - 360, WINDOW_HEIGHT - 95), (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 70)], fill=(28, 36, 50))
    draw.text((WINDOW_WIDTH - 348, WINDOW_HEIGHT - 90), "PLAYER TELEMETRY & CAMERA", fill=(120, 255, 180), font=font_bold)
    telemetry = (
        f"Position: ({player_x:.1f}, {player_y:.1f}, {player_z:.1f}) | Yaw: {player_angle:.0f}°\n"
        f"Grounded: {is_grounded} | Camera: 3rd-Person Dynamic Follow\n"
        f"Physics Engine: Euler Kinematics with Gravity"
    )
    draw.text((WINDOW_WIDTH - 348, WINDOW_HEIGHT - 65), telemetry, fill=(215, 230, 220), font=font_info)

    image.save(output_path)
    print(f"Captured screenshot saved to {output_path}")


def key_callback(window, key, scancode, action, mods):
    global keys
    if action == glfw.PRESS:
        keys[key] = True
        if key == glfw.KEY_R:
            reset_scene()
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)
    elif action == glfw.RELEASE:
        keys[key] = False


def main():
    global anim_time
    headless = "--headless" in sys.argv or "--screenshot" in sys.argv

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")

    glfw.window_hint(glfw.DEPTH_BITS, 24)
    if headless:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Experiment 9 - Simple Interactive 3D Scene", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    # Set up initial display
    anim_time = 1.5
    draw_scene()
    output_path = os.path.join(os.path.dirname(__file__), "image.png")
    add_hud_and_save(output_path)
    glfw.swap_buffers(window)

    if headless:
        glfw.destroy_window(window)
        glfw.terminate()
        return

    # Interactive Game Loop
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time
        anim_time = current_time

        update_physics(dt)
        draw_scene()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()

