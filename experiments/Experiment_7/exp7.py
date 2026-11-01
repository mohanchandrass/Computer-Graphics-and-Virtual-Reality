import sys
import os
from math import sin, cos, pi, sqrt
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# EXPERIMENT 7: PHONG ILLUMINATION MODEL FOR A 3D OBJECT
# ============================================================
# The Phong Illumination Model calculates reflected light intensity:
#   I = I_ambient + I_diffuse + I_specular
#   I = ka * Ia + kd * (N . L) * Id + ks * (R . V)^alpha * Is
# where:
#   N = Surface unit normal
#   L = Normalized light direction vector
#   V = Normalized viewer direction vector
#   R = Reflected light vector: R = 2*(N . L)*N - L
#   alpha = Shininess exponent
# ============================================================

WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 800

# Material & Light properties
KA = 0.15
KD = 0.75
KS = 0.65
SHININESS = 32.0

# Base object color (Emerald / Teal tone or Rich Coral)
BASE_COLOR = (0.90, 0.35, 0.20)
SPECULAR_COLOR = (1.0, 1.0, 1.0)
AMBIENT_LIGHT = (0.3, 0.3, 0.3)

# Light position (spherical coordinates)
light_theta = 0.8
light_phi = 0.6


def get_light_direction():
    lx = cos(light_phi) * sin(light_theta)
    ly = sin(light_phi)
    lz = cos(light_phi) * cos(light_theta)
    norm = sqrt(lx*lx + ly*ly + lz*lz)
    return (lx / norm, ly / norm, lz / norm)


def draw_sphere(mode="full"):
    """
    Renders a 3D sphere using quad/triangle strips with Phong lighting.
    mode can be: 'ambient', 'diffuse', 'specular', 'full'
    """
    lx, ly, lz = get_light_direction()
    vx, vy, vz = 0.0, 0.0, 1.0  # Camera at (0, 0, 1) looking down -Z

    stacks = 50
    sectors = 100

    for i in range(stacks):
        lat0 = -pi / 2.0 + i * pi / stacks
        lat1 = -pi / 2.0 + (i + 1) * pi / stacks

        glBegin(GL_TRIANGLE_STRIP)
        for j in range(sectors + 1):
            lng = j * 2.0 * pi / sectors

            for lat in (lat0, lat1):
                # Unit sphere vertex coordinates = surface normal
                nx = cos(lat) * cos(lng)
                ny = sin(lat)
                nz = cos(lat) * sin(lng)

                # N . L
                n_dot_l = nx * lx + ny * ly + nz * lz

                # 1. Ambient Component
                i_amb = KA
                amb_r = i_amb * BASE_COLOR[0]
                amb_g = i_amb * BASE_COLOR[1]
                amb_b = i_amb * BASE_COLOR[2]

                # 2. Diffuse Component (Lambertian)
                diff_factor = max(0.0, n_dot_l)
                i_diff = KD * diff_factor
                diff_r = i_diff * BASE_COLOR[0]
                diff_g = i_diff * BASE_COLOR[1]
                diff_b = i_diff * BASE_COLOR[2]

                # 3. Specular Component (Phong)
                spec_r = spec_g = spec_b = 0.0
                if n_dot_l > 0.0:
                    # R = 2*(N.L)*N - L
                    rx = 2.0 * n_dot_l * nx - lx
                    ry = 2.0 * n_dot_l * ny - ly
                    rz = 2.0 * n_dot_l * nz - lz

                    # R . V
                    r_dot_v = rx * vx + ry * vy + rz * vz
                    if r_dot_v > 0.0:
                        i_spec = KS * (r_dot_v ** SHININESS)
                        spec_r = i_spec * SPECULAR_COLOR[0]
                        spec_g = i_spec * SPECULAR_COLOR[1]
                        spec_b = i_spec * SPECULAR_COLOR[2]

                # Color assignment based on requested display mode
                if mode == "ambient":
                    r = min(1.0, amb_r + 0.1)
                    g = min(1.0, amb_g + 0.1)
                    b = min(1.0, amb_b + 0.1)
                elif mode == "diffuse":
                    r = min(1.0, diff_r)
                    g = min(1.0, diff_g)
                    b = min(1.0, diff_b)
                elif mode == "specular":
                    r = min(1.0, spec_r)
                    g = min(1.0, spec_g)
                    b = min(1.0, spec_b)
                else:  # 'full' Phong model
                    r = min(1.0, amb_r + diff_r + spec_r)
                    g = min(1.0, amb_g + diff_g + spec_g)
                    b = min(1.0, amb_b + diff_b + spec_b)

                glColor3f(r, g, b)
                glVertex3f(nx, ny, nz)

        glEnd()


def draw_panel_border(w, h):
    """Draw a thin viewport border."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.25, 0.30, 0.40)
    glLineWidth(1.5)
    glBegin(GL_LINE_LOOP)
    glVertex2f(8, 8)
    glVertex2f(w - 8, 8)
    glVertex2f(w - 8, h - 8)
    glVertex2f(8, h - 8)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def render_scene():
    glClearColor(0.04, 0.05, 0.08, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    pw = WINDOW_WIDTH // 4
    ph = WINDOW_HEIGHT

    modes = [
        ("ambient", "1. Ambient Reflection", 0),
        ("diffuse", "2. Diffuse Reflection", pw),
        ("specular", "3. Specular Reflection", pw * 2),
        ("full", "4. Full Phong Model", pw * 3),
    ]

    for mode, label, x in modes:
        glViewport(x, 0, pw, ph)

        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1.45, 1.45, -1.45 * (ph / pw), 1.45 * (ph / pw), -3, 3)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        draw_sphere(mode)
        draw_panel_border(pw, ph)


def add_labels_and_save(output_path):
    """Overlay rich mathematical labels and information."""
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WINDOW_WIDTH, WINDOW_HEIGHT), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    draw = ImageDraw.Draw(image)
    try:
        font_header = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
        font_formula = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 15)
        font_desc = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
    except Exception:
        font_header = font_sub = font_formula = font_desc = ImageFont.load_default()

    pw = WINDOW_WIDTH // 4

    panels = [
        {
            "x": 0,
            "title": "Ambient Component",
            "formula": "I_amb = ka * Ia",
            "desc": "Uniform background lighting\nIndependent of light direction\nProvides baseline illumination",
            "color": (160, 190, 220),
            "accent": (60, 100, 150),
        },
        {
            "x": pw,
            "title": "Diffuse Component",
            "formula": "I_diff = kd * (N . L) * Id",
            "desc": "Lambert's Cosine Law\nScatters equally in all directions\nDepends on angle of incidence",
            "color": (255, 160, 90),
            "accent": (200, 110, 40),
        },
        {
            "x": pw * 2,
            "title": "Specular Component",
            "formula": "I_spec = ks * (R . V)^a * Is",
            "desc": "Mirror-like glossy reflection\nR = 2(N.L)N - L; alpha = 32\nCreates brilliant highlight",
            "color": (230, 230, 255),
            "accent": (140, 140, 210),
        },
        {
            "x": pw * 3,
            "title": "Full Phong Model",
            "formula": "I = I_amb + I_diff + I_spec",
            "desc": "Complete illumination model\nRealistic 3D shading & depth\nCombines all three components",
            "color": (100, 255, 170),
            "accent": (40, 180, 100),
        },
    ]

    for p in panels:
        x0 = p["x"] + 14
        x1 = p["x"] + pw - 14

        # Top Header Box
        draw.rectangle([(x0, 16), (x1, 80)], fill=(20, 24, 34, 235), outline=p["accent"], width=2)
        draw.text((x0 + 12, 22), p["title"], fill=p["color"], font=font_header)
        draw.text((x0 + 12, 50), p["formula"], fill=(255, 230, 140), font=font_formula)

        # Bottom Description Box
        draw.rectangle([(x0, WINDOW_HEIGHT - 95), (x1, WINDOW_HEIGHT - 16)], fill=(20, 24, 34, 235), outline=p["accent"], width=1)
        y_text = WINDOW_HEIGHT - 90
        for line in p["desc"].split("\n"):
            draw.text((x0 + 12, y_text), line, fill=(210, 215, 225), font=font_desc)
            y_text += 22

    # Draw vertical separator lines
    for i in range(1, 4):
        draw.line([(pw * i, 0), (pw * i, WINDOW_HEIGHT)], fill=(60, 70, 90), width=2)

    image.save(output_path)
    print(f"Captured screenshot saved to {output_path}")


def main():
    global light_theta, light_phi
    headless = "--headless" in sys.argv or "--screenshot" in sys.argv

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")

    glfw.window_hint(glfw.DEPTH_BITS, 24)
    if headless:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Experiment 7 - Phong Illumination Model for 3D Object", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(window)

    render_scene()
    glfw.swap_buffers(window)

    output_path = os.path.join(os.path.dirname(__file__), "image.png")
    add_labels_and_save(output_path)

    if headless:
        glfw.destroy_window(window)
        glfw.terminate()
        return

    # Interactive event loop: animate light slowly
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        # Slowly rotate light source around sphere for dynamic 3D lighting
        light_theta += 0.8 * dt

        render_scene()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()

