import sys
import os
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# EXPERIMENT 10: 3D VIEWING PIPELINE
#                PROJECTION AND VIEWPORT MAPPING
# ============================================================
# Demonstrates the complete 3D viewing transformation pipeline:
# 1. Model / Object Coordinates: 3D Cube geometry
# 2. World Coordinates: Model rotation & placement
# 3. View / Eye Coordinates: gluLookAt camera transformation
# 4. Projection Coordinates: Orthographic vs Perspective
# 5. Normalized Device Coordinates (NDC): [-1, 1]^3
# 6. Viewport Mapping: Mapping NDC to 2D screen viewports
# ============================================================

WINDOW_WIDTH = 1300
WINDOW_HEIGHT = 700

# 3D Cube Definition
vertices = [
    (-1.0, -1.0, -1.0),
    ( 1.0, -1.0, -1.0),
    ( 1.0,  1.0, -1.0),
    (-1.0,  1.0, -1.0),
    (-1.0, -1.0,  1.0),
    ( 1.0, -1.0,  1.0),
    ( 1.0,  1.0,  1.0),
    (-1.0,  1.0,  1.0),
]

faces = [
    (0, 1, 2, 3),  # Back
    (4, 5, 6, 7),  # Front
    (0, 1, 5, 4),  # Bottom
    (2, 3, 7, 6),  # Top
    (1, 2, 6, 5),  # Right
    (0, 3, 7, 4),  # Left
]

edges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7),
]

colors = [
    (0.95, 0.25, 0.25),  # Red
    (0.25, 0.85, 0.35),  # Green
    (0.25, 0.50, 0.95),  # Blue
    (1.00, 0.85, 0.20),  # Yellow
    (0.85, 0.25, 0.95),  # Magenta
    (0.20, 0.90, 0.90),  # Cyan
]

angle = 45.0


def draw_cube():
    # Colored solid faces
    glBegin(GL_QUADS)
    for i, face in enumerate(faces):
        glColor3fv(colors[i])
        for v_idx in face:
            glVertex3fv(vertices[v_idx])
    glEnd()

    # Black wireframe edges for geometric clarity
    glColor3f(0.08, 0.08, 0.12)
    glLineWidth(2.5)
    glBegin(GL_LINES)
    for edge in edges:
        for v_idx in edge:
            glVertex3fv(vertices[v_idx])
    glEnd()


def setup_viewport(x, y, w, h, is_perspective):
    glViewport(x, y, w, h)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    if is_perspective:
        # Perspective Projection: Converging rays with foreshortening
        gluPerspective(45.0, w / float(h), 0.1, 100.0)
    else:
        # Orthographic Projection: Parallel projection rays
        aspect = w / float(h)
        glOrtho(-3.0 * aspect, 3.0 * aspect, -3.0, 3.0, 1.0, 25.0)

    glMatrixMode(GL_MODELVIEW)


def draw_view(cur_angle):
    glLoadIdentity()
    # Camera View Transformation: Eye=(4, 3, 6), Center=(0, 0, 0), Up=(0, 1, 0)
    gluLookAt(4.0, 3.0, 6.0,
              0.0, 0.0, 0.0,
              0.0, 1.0, 0.0)

    # Modeling Transformation: Rotate cube around diagonal axis
    glRotatef(cur_angle, 1.0, 1.0, 0.0)
    draw_cube()


def draw_panel_border(w, h):
    """Draw a clean 2D border around each viewport."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, w, 0, h, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.28, 0.35, 0.48)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(10, 10)
    glVertex2f(w - 10, 10)
    glVertex2f(w - 10, h - 10)
    glVertex2f(10, h - 10)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def render_scene(cur_angle):
    glClearColor(0.04, 0.05, 0.08, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    half_w = WINDOW_WIDTH // 2

    # ------------------------------------------------------------
    # LEFT VIEWPORT: ORTHOGRAPHIC PROJECTION
    # ------------------------------------------------------------
    setup_viewport(0, 0, half_w, WINDOW_HEIGHT, False)
    draw_view(cur_angle)
    draw_panel_border(half_w, WINDOW_HEIGHT)

    # ------------------------------------------------------------
    # RIGHT VIEWPORT: PERSPECTIVE PROJECTION
    # ------------------------------------------------------------
    setup_viewport(half_w, 0, half_w, WINDOW_HEIGHT, True)
    draw_view(cur_angle)
    draw_panel_border(half_w, WINDOW_HEIGHT)


def add_labels_and_save(output_path):
    """Capture screen and overlay detailed viewing pipeline documentation."""
    glReadBuffer(GL_BACK)
    glFinish()
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WINDOW_WIDTH, WINDOW_HEIGHT), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
        font_head = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 17)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
        font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 13)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    except Exception:
        font_title = font_head = font_sub = font_code = font_bold = ImageFont.load_default()

    half_w = WINDOW_WIDTH // 2

    # Top Header Banner
    draw.rectangle([(20, 16), (WINDOW_WIDTH - 20, 72)], fill=(16, 20, 30, 240), outline=(0, 180, 255), width=2)
    draw.text((36, 22), "EXPERIMENT 10: 3D VIEWING PIPELINE & PROJECTION MAPPING", fill=(0, 210, 255), font=font_title)
    draw.text((36, 48), "Object Space  ->  World Space  ->  Eye/Camera Space  ->  Projection & Clipping  ->  NDC  ->  Viewport Screen", fill=(200, 215, 230), font=font_sub)

    # Left Viewport Card (Orthographic)
    draw.rectangle([(25, 88), (half_w - 25, 175)], fill=(16, 22, 34, 235), outline=(100, 180, 255), width=2)
    draw.text((38, 95), "1. Orthographic Projection (Parallel)", fill=(100, 200, 255), font=font_head)
    draw.text((38, 122), "glOrtho(left, right, bottom, top, near, far)", fill=(255, 225, 120), font=font_code)
    draw.text((38, 146), "Projectors are parallel | Object scale is constant regardless of distance | Preserves true geometry", fill=(210, 220, 235), font=font_sub)

    # Left Bottom Info
    draw.rectangle([(25, WINDOW_HEIGHT - 85), (half_w - 25, WINDOW_HEIGHT - 20)], fill=(18, 22, 32, 235), outline=(70, 90, 120))
    draw.text((38, WINDOW_HEIGHT - 77), "Characteristics: No vanishing points; ideal for engineering, CAD, and technical schematics.", fill=(180, 205, 230), font=font_sub)
    draw.text((38, WINDOW_HEIGHT - 55), "Matrix: Affine transformation preserving parallelism between 3D vectors.", fill=(150, 230, 180), font=font_sub)

    # Right Viewport Card (Perspective)
    draw.rectangle([(half_w + 25, 88), (WINDOW_WIDTH - 25, 175)], fill=(16, 22, 34, 235), outline=(255, 170, 60), width=2)
    draw.text((half_w + 38, 95), "2. Perspective Projection (Foreshortening)", fill=(255, 190, 80), font=font_head)
    draw.text((half_w + 38, 122), "gluPerspective(fovy=45°, aspect, near=0.1, far=100.0)", fill=(255, 225, 120), font=font_code)
    draw.text((half_w + 38, 146), "Projectors converge at eye center | Distance creates realistic foreshortening | Natural human vision", fill=(210, 220, 235), font=font_sub)

    # Right Bottom Info
    draw.rectangle([(half_w + 25, WINDOW_HEIGHT - 85), (WINDOW_WIDTH - 25, WINDOW_HEIGHT - 20)], fill=(18, 22, 32, 235), outline=(70, 90, 120))
    draw.text((half_w + 38, WINDOW_HEIGHT - 77), "Characteristics: Parallel lines converge toward vanishing points; mimics real-world human vision.", fill=(180, 205, 230), font=font_sub)
    draw.text((half_w + 38, WINDOW_HEIGHT - 55), "Matrix: Non-linear perspective division by W produces depth perception.", fill=(255, 210, 140), font=font_sub)

    # Center Divider
    draw.line([(half_w, 0), (half_w, WINDOW_HEIGHT)], fill=(80, 100, 130), width=2)

    image.save(output_path)
    print(f"Captured screenshot saved to {output_path}")


def main():
    global angle
    headless = "--headless" in sys.argv or "--screenshot" in sys.argv

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")

    glfw.window_hint(glfw.DEPTH_BITS, 24)
    if headless:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Experiment 10 - 3D Viewing Pipeline, Projection and Viewport Mapping", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Window creation failed")

    glfw.make_context_current(window)

    angle = 35.0
    render_scene(angle)
    output_path = os.path.join(os.path.dirname(__file__), "image.png")
    add_labels_and_save(output_path)
    glfw.swap_buffers(window)

    if headless:
        glfw.destroy_window(window)
        glfw.terminate()
        return

    # Interactive loop: rotate 3D cube
    last_time = glfw.get_time()
    while not glfw.window_should_close(window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time

        angle += 30.0 * dt
        render_scene(angle)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()

