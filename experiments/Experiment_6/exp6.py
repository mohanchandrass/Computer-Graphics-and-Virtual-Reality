import sys
import os
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# EXPERIMENT 6: Z-BUFFER ALGORITHM FOR HIDDEN SURFACE REMOVAL
# ============================================================
# The Z-buffer (depth-buffer) algorithm is an image-space approach
# for hidden surface removal. Each pixel on the screen maintains:
# 1. Color Buffer: The RGB color of the visible primitive.
# 2. Depth (Z) Buffer: The smallest Z distance (closest to viewer).
#
# When rasterizing a polygon:
# If polygon_Z(x, y) < depth_buffer(x, y):
#     depth_buffer(x, y) = polygon_Z(x, y)
#     color_buffer(x, y) = polygon_color
# ============================================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

def draw_primitives():
    """Draw multiple overlapping primitives at different depths."""
    glBegin(GL_TRIANGLES)

    # Primitive 1: Red Triangle - Closer to viewer (Z = 0.5)
    # Drawn FIRST in the sequence.
    # Without Z-buffer, it gets overwritten by primitives drawn later.
    # With Z-buffer, it stays on top because Z=0.5 is closer than Z=-0.2 and Z=-0.6.
    glColor3f(0.92, 0.22, 0.22)
    glVertex3f(-0.7, -0.6, 0.5)
    glVertex3f(0.5, -0.6, 0.5)
    glVertex3f(-0.1, 0.7, 0.5)

    # Primitive 2: Green Triangle - Mid depth (Z = -0.2)
    # Drawn SECOND. Overlaps with red.
    glColor3f(0.20, 0.85, 0.35)
    glVertex3f(-0.4, -0.4, -0.2)
    glVertex3f(0.8, -0.4, -0.2)
    glVertex3f(0.3, 0.8, -0.2)

    # Primitive 3: Blue Triangle - Far depth (Z = -0.6)
    # Drawn THIRD. Overlaps bottom region.
    glColor3f(0.25, 0.50, 0.95)
    glVertex3f(-0.8, 0.2, -0.6)
    glVertex3f(0.2, 0.2, -0.6)
    glVertex3f(-0.3, -0.8, -0.6)

    glEnd()


def draw_viewport_border(width, height):
    """Draw a clean border around the viewport."""
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    glOrtho(0, width, 0, height, -1, 1)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    glColor3f(0.3, 0.35, 0.45)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    glVertex2f(12, 12)
    glVertex2f(width - 12, 12)
    glVertex2f(width - 12, height - 12)
    glVertex2f(12, height - 12)
    glEnd()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def render_scene():
    glClearColor(0.06, 0.07, 0.10, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    half_width = WINDOW_WIDTH // 2

    # ------------------------------------------------------------
    # LEFT VIEWPORT: WITHOUT Z-BUFFER (DEPTH TESTING DISABLED)
    # Painter's Algorithm failure: order of drawing determines visibility
    # ------------------------------------------------------------
    glViewport(0, 0, half_width, WINDOW_HEIGHT)
    glDisable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.3, 1.3, -1.3, 1.3, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_primitives()
    draw_viewport_border(half_width, WINDOW_HEIGHT)

    # ------------------------------------------------------------
    # RIGHT VIEWPORT: WITH Z-BUFFER (DEPTH TESTING ENABLED)
    # Depth buffer resolves visibility correctly regardless of draw order
    # ------------------------------------------------------------
    glViewport(half_width, 0, half_width, WINDOW_HEIGHT)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(-1.3, 1.3, -1.3, 1.3, -2, 2)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    draw_primitives()
    draw_viewport_border(half_width, WINDOW_HEIGHT)


def add_labels_and_save(output_path):
    """Capture framebuffer and add crisp informative annotations."""
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WINDOW_WIDTH, WINDOW_HEIGHT), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 16)
        font_tag = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    except Exception:
        font_title = font_sub = font_tag = ImageFont.load_default()

    half_width = WINDOW_WIDTH // 2

    # Left header banner (Without Z-Buffer)
    draw.rectangle([(20, 20), (half_width - 20, 75)], fill=(25, 28, 38, 230), outline=(220, 60, 60), width=2)
    draw.text((35, 27), "Without Z-Buffer (Depth Test DISABLED)", fill=(255, 90, 90), font=font_title)
    draw.text((35, 52), "Farther primitives overwrite closer ones (Draw order dependent)", fill=(200, 200, 200), font=font_sub)

    # Left note tag
    draw.rectangle([(30, WINDOW_HEIGHT - 65), (half_width - 30, WINDOW_HEIGHT - 25)], fill=(35, 20, 20), outline=(180, 50, 50))
    draw.text((45, WINDOW_HEIGHT - 57), "INCORRECT VISIBILITY: Green & Blue wrongly occlude Red", fill=(255, 120, 120), font=font_tag)

    # Right header banner (With Z-Buffer)
    draw.rectangle([(half_width + 20, 20), (WINDOW_WIDTH - 20, 75)], fill=(25, 28, 38, 230), outline=(50, 200, 100), width=2)
    draw.text((half_width + 35, 27), "With Z-Buffer (Depth Test ENABLED)", fill=(70, 230, 120), font=font_title)
    draw.text((half_width + 35, 52), "Per-pixel depth test: if Z < Z_buffer then update pixel", fill=(200, 200, 200), font=font_sub)

    # Right note tag
    draw.rectangle([(half_width + 30, WINDOW_HEIGHT - 65), (WINDOW_WIDTH - 30, WINDOW_HEIGHT - 25)], fill=(20, 35, 25), outline=(50, 160, 80))
    draw.text((half_width + 45, WINDOW_HEIGHT - 57), "CORRECT VISIBILITY: Closer Red (Z=0.5) stays in front of Green & Blue", fill=(120, 255, 160), font=font_tag)

    # Middle divider line
    draw.line([(half_width, 0), (half_width, WINDOW_HEIGHT)], fill=(80, 90, 110), width=2)

    image.save(output_path)
    print(f"Captured screenshot saved to {output_path}")


def main():
    headless = "--headless" in sys.argv or "--screenshot" in sys.argv

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")

    glfw.window_hint(glfw.DEPTH_BITS, 24)
    if headless:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Experiment 6 - Z-Buffer Algorithm for Hidden Surface Removal", None, None)
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

    # Interactive event loop
    while not glfw.window_should_close(window):
        render_scene()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()
