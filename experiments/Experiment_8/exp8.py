import sys
import os
import math
import ctypes
import numpy as np
import glfw
from OpenGL.GL import *
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# EXPERIMENT 8: BASIC OPENGL PROGRAM USING
#               VERTEX AND FRAGMENT SHADERS
# ============================================================
# Demonstrates the modern programmable OpenGL graphics pipeline
# using GLSL 3.3 Core:
# 1. Vertex Shader: Processes vertex attributes & applies rotation
# 2. Fragment Shader: Computes per-fragment color & time pulsation
# 3. Buffer Objects: VAO and VBO for high-performance GPU rendering
# ============================================================

WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700

VERTEX_SHADER_SOURCE = """#version 330 core
layout (location = 0) in vec3 aPos;
layout (location = 1) in vec3 aColor;

out vec3 vertexColor;

uniform float angle;

void main()
{
    float c = cos(angle);
    float s = sin(angle);

    mat2 rotation = mat2(
        c, -s,
        s,  c
    );

    vec2 rotatedPos = rotation * aPos.xy;
    gl_Position = vec4(rotatedPos, aPos.z, 1.0);
    vertexColor = aColor;
}
"""

FRAGMENT_SHADER_SOURCE = """#version 330 core
in vec3 vertexColor;
out vec4 FragColor;

uniform float time;

void main()
{
    float pulse = 0.5 + 0.5 * sin(time * 2.5);
    vec3 animatedColor = vertexColor * (0.75 + 0.25 * pulse);
    FragColor = vec4(animatedColor, 1.0);
}
"""


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        error = glGetShaderInfoLog(shader).decode()
        raise RuntimeError(f"Shader compilation failed: {error}")
    return shader


def create_shader_program():
    vs = compile_shader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER)
    fs = compile_shader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)

    if not glGetProgramiv(program, GL_LINK_STATUS):
        error = glGetProgramInfoLog(program).decode()
        raise RuntimeError(f"Shader program linking failed: {error}")

    glDeleteShader(vs)
    glDeleteShader(fs)
    return program


def add_labels_and_save(output_path):
    """Capture the rendered frame and overlay informative pipeline documentation."""
    glPixelStorei(GL_PACK_ALIGNMENT, 1)
    data = glReadPixels(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, GL_RGB, GL_UNSIGNED_BYTE)
    image = Image.frombytes("RGB", (WINDOW_WIDTH, WINDOW_HEIGHT), data)
    image = image.transpose(Image.FLIP_TOP_BOTTOM)

    draw = ImageDraw.Draw(image)
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
        font_sub = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
        font_code = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 12)
        font_bold = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 14)
    except Exception:
        font_title = font_sub = font_code = font_bold = ImageFont.load_default()

    # Top Header
    draw.rectangle([(20, 16), (WINDOW_WIDTH - 20, 68)], fill=(16, 19, 28, 235), outline=(0, 160, 255), width=2)
    draw.text((36, 22), "EXPERIMENT 8: OPENGL PROGRAMMABLE PIPELINE (GLSL 3.3 CORE)", fill=(0, 200, 255), font=font_title)
    draw.text((36, 46), "Vertex Shader (Transformations)  ->  Rasterization  ->  Fragment Shader (Per-Pixel Color Output)", fill=(200, 210, 225), font=font_sub)

    # Left Side: Vertex Shader Card
    draw.rectangle([(20, 85), (370, 375)], fill=(15, 18, 26, 230), outline=(80, 100, 130), width=1)
    draw.rectangle([(20, 85), (370, 115)], fill=(25, 32, 48))
    draw.text((30, 92), "Vertex Shader (GLSL 330 Core)", fill=(120, 210, 255), font=font_bold)
    vs_text = """layout(location=0) in vec3 aPos;
layout(location=1) in vec3 aColor;
out vec3 vertexColor;
uniform float angle;

void main() {
    mat2 rot = mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
    gl_Position = vec4(rot*aPos.xy,
                       aPos.z, 1.0);
    vertexColor = aColor;
}"""
    draw.text((30, 125), vs_text, fill=(220, 230, 245), font=font_code)

    # Left Side: Fragment Shader Card
    draw.rectangle([(20, 390), (370, WINDOW_HEIGHT - 65)], fill=(15, 18, 26, 230), outline=(80, 100, 130), width=1)
    draw.rectangle([(20, 390), (370, 420)], fill=(35, 25, 45))
    draw.text((30, 397), "Fragment Shader (GLSL 330 Core)", fill=(240, 140, 255), font=font_bold)
    fs_text = """in vec3 vertexColor;
out vec4 FragColor;
uniform float time;

void main() {
    float pulse = 0.5 +
        0.5 * sin(time * 2.5);
    vec3 col = vertexColor *
        (0.75 + 0.25 * pulse);
    FragColor = vec4(col, 1.0);
}"""
    draw.text((30, 430), fs_text, fill=(240, 225, 255), font=font_code)

    # Right Side: Pipeline Attributes Card
    draw.rectangle([(WINDOW_WIDTH - 320, 85), (WINDOW_WIDTH - 20, 310)], fill=(15, 18, 26, 230), outline=(80, 100, 130), width=1)
    draw.rectangle([(WINDOW_WIDTH - 320, 85), (WINDOW_WIDTH - 20, 115)], fill=(24, 38, 30))
    draw.text((WINDOW_WIDTH - 308, 92), "Pipeline Attributes & Buffers", fill=(120, 255, 170), font=font_bold)
    pipeline_info = (
        "- VAO (Vertex Array Object)\n"
        "- VBO (Vertex Buffer Object)\n"
        "- Stride: 6 * sizeof(float)\n"
        "- Attr 0: Position (3 floats)\n"
        "- Attr 1: Color (3 floats)\n"
        "- Uniform 'angle': Dynamic rotation\n"
        "- Uniform 'time': Dynamic pulse\n"
        "- Core Profile: 3.3 Enabled"
    )
    draw.text((WINDOW_WIDTH - 308, 125), pipeline_info, fill=(210, 235, 220), font=font_sub)

    # Bottom status bar
    draw.rectangle([(20, WINDOW_HEIGHT - 50), (WINDOW_WIDTH - 20, WINDOW_HEIGHT - 16)], fill=(16, 20, 30, 235), outline=(60, 75, 100))
    draw.text((35, WINDOW_HEIGHT - 42), "STATUS: Shaders compiled & linked successfully | Smooth per-vertex RGB interpolation | Real-time rotation", fill=(100, 230, 160), font=font_bold)

    image.save(output_path)
    print(f"Captured screenshot saved to {output_path}")


def main():
    headless = "--headless" in sys.argv or "--screenshot" in sys.argv

    if not glfw.init():
        raise RuntimeError("GLFW initialization failed")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    if headless:
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "Experiment 8 - OpenGL Vertex and Fragment Shaders", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("OpenGL 3.3 Core Window creation failed")

    glfw.make_context_current(window)

    shader_program = create_shader_program()

    # Vertex Data: [X, Y, Z,   R, G, B]
    # Triangle with 3 distinct per-vertex colors for interpolation
    vertices = np.array([
         0.00,  0.65, 0.0,   1.0, 0.20, 0.25,   # Top: Vibrant Red
        -0.65, -0.55, 0.0,   0.15, 0.85, 0.30,  # Bottom-Left: Emerald Green
         0.65, -0.55, 0.0,   0.20, 0.55, 1.00   # Bottom-Right: Sky Blue
    ], dtype=np.float32)

    # VAO & VBO
    VAO = glGenVertexArrays(1)
    glBindVertexArray(VAO)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 6 * vertices.itemsize

    # Position attribute (location = 0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    # Color attribute (location = 1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * vertices.itemsize))
    glEnableVertexAttribArray(1)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

    angle_loc = glGetUniformLocation(shader_program, "angle")
    time_loc = glGetUniformLocation(shader_program, "time")

    def render(angle, current_time):
        glViewport(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT)
        glClearColor(0.04, 0.05, 0.08, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        glUseProgram(shader_program)
        glUniform1f(angle_loc, angle)
        glUniform1f(time_loc, current_time)

        glBindVertexArray(VAO)
        glDrawArrays(GL_TRIANGLES, 0, 3)
        glBindVertexArray(0)

    # Capture first frame with slight angle for presentation
    initial_angle = 0.35
    render(initial_angle, 1.2)
    glfw.swap_buffers(window)

    output_path = os.path.join(os.path.dirname(__file__), "image.png")
    add_labels_and_save(output_path)

    if headless:
        glDeleteVertexArrays(1, [VAO])
        glDeleteBuffers(1, [VBO])
        glDeleteProgram(shader_program)
        glfw.destroy_window(window)
        glfw.terminate()
        return

    # Interactive animation loop
    start_time = glfw.get_time()
    while not glfw.window_should_close(window):
        t = glfw.get_time() - start_time
        angle = t * 1.0  # 1 rad/s rotation

        render(angle, t)
        glfw.swap_buffers(window)
        glfw.poll_events()

    glDeleteVertexArrays(1, [VAO])
    glDeleteBuffers(1, [VBO])
    glDeleteProgram(shader_program)
    glfw.destroy_window(window)
    glfw.terminate()


if __name__ == "__main__":
    main()

