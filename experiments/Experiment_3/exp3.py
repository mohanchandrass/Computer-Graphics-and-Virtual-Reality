from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math


# ============================================================
# 2D TRANSFORMATIONS USING HOMOGENEOUS COORDINATES
# ============================================================

# Original triangle in homogeneous coordinates
# P = [x, y, 1]
triangle = [
    [0, 0, 1],
    [100, 0, 1],
    [50, 100, 1]
]


# ============================================================
# MATRIX MULTIPLICATION
# ============================================================

def matrix_multiply(A, B):
    rows = len(A)
    cols = len(B[0])
    common = len(B)

    result = [[0 for _ in range(cols)] for _ in range(rows)]

    for i in range(rows):
        for j in range(cols):
            for k in range(common):
                result[i][j] += A[i][k] * B[k][j]

    return result


# ============================================================
# APPLY TRANSFORMATION MATRIX TO A POINT
# ============================================================

def transform_point(matrix, point):

    p = [
        [point[0]],
        [point[1]],
        [point[2]]
    ]

    result = matrix_multiply(matrix, p)

    return [
        result[0][0],
        result[1][0],
        result[2][0]
    ]


# ============================================================
# 1. TRANSLATION MATRIX
# ============================================================

def translation(tx, ty):

    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]


# ============================================================
# 2. ROTATION MATRIX
# ============================================================

def rotation(angle):

    theta = math.radians(angle)

    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)

    return [
        [cos_theta, -sin_theta, 0],
        [sin_theta,  cos_theta, 0],
        [0,          0,         1]
    ]


# ============================================================
# 3. SCALING MATRIX
# ============================================================

def scaling(sx, sy):

    return [
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ]


# ============================================================
# 4. REFLECTION MATRIX
# ============================================================

def reflection_x():

    return [
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ]


def reflection_y():

    return [
        [-1, 0, 0],
        [0,  1, 0],
        [0,  0, 1]
    ]


# ============================================================
# 5. SHEARING MATRIX
# ============================================================

def shearing(shx, shy):

    return [
        [1,   shx, 0],
        [shy, 1,   0],
        [0,   0,   1]
    ]


# ============================================================
# TRANSFORM COMPLETE TRIANGLE
# ============================================================

def transform_triangle(matrix):

    transformed = []

    for point in triangle:
        transformed.append(
            transform_point(matrix, point)
        )

    return transformed


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(x, y, text, size=GLUT_BITMAP_9_BY_15):

    glRasterPos2f(x, y)

    for character in text:
        glutBitmapCharacter(size, ord(character))


# ============================================================
# DRAW AXES
# ============================================================

def draw_axes():

    # X-axis
    glColor3f(0.35, 0.35, 0.35)

    glBegin(GL_LINES)

    glVertex2f(-150, 0)
    glVertex2f(250, 0)

    # Y-axis
    glVertex2f(0, -150)
    glVertex2f(0, 200)

    glEnd()


# ============================================================
# DRAW GRID
# ============================================================

def draw_grid():

    glColor3f(0.12, 0.12, 0.12)

    glBegin(GL_LINES)

    # Vertical lines
    for x in range(-150, 251, 50):
        glVertex2f(x, -150)
        glVertex2f(x, 200)

    # Horizontal lines
    for y in range(-150, 201, 50):
        glVertex2f(-150, y)
        glVertex2f(250, y)

    glEnd()


# ============================================================
# DRAW ORIGINAL TRIANGLE
# ============================================================

def draw_original_triangle():

    glColor3f(0.7, 0.7, 0.7)

    glLineWidth(2)

    glBegin(GL_LINE_LOOP)

    for x, y, _ in triangle:
        glVertex2f(x, y)

    glEnd()


# ============================================================
# DRAW TRANSFORMED TRIANGLE
# ============================================================

def draw_transformed_triangle(points):

    glLineWidth(3)

    glBegin(GL_LINE_LOOP)

    for x, y, _ in points:
        glVertex2f(x, y)

    glEnd()

    # Draw vertices
    glPointSize(7)

    glBegin(GL_POINTS)

    for x, y, _ in points:
        glVertex2f(x, y)

    glEnd()


# ============================================================
# DRAW ONE TRANSFORMATION PANEL
# ============================================================

def draw_panel(
    x,
    y,
    width,
    height,
    title,
    parameter,
    matrix,
    color
):

    # --------------------------------------------------------
    # Panel border
    # --------------------------------------------------------

    glColor3f(0.5, 0.5, 0.5)

    glLineWidth(1)

    glBegin(GL_LINE_LOOP)

    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)

    glEnd()


    # --------------------------------------------------------
    # Panel title
    # --------------------------------------------------------

    glColor3f(*color)

    draw_text(
        x + 15,
        y + height - 25,
        title,
        GLUT_BITMAP_HELVETICA_18
    )


    # --------------------------------------------------------
    # Transformation parameter
    # --------------------------------------------------------

    glColor3f(1, 1, 1)

    draw_text(
        x + 15,
        y + height - 48,
        parameter
    )


    # --------------------------------------------------------
    # Set local coordinate system
    # --------------------------------------------------------

    glPushMatrix()

    glTranslatef(
        x + width / 2,
        y + 105,
        0
    )

    # Draw grid and axes
    draw_grid()
    draw_axes()

    # Draw original triangle
    draw_original_triangle()

    # Transform triangle
    transformed = transform_triangle(matrix)

    # Draw transformed triangle
    glColor3f(*color)

    draw_transformed_triangle(transformed)

    glPopMatrix()


# ============================================================
# DISPLAY
# ============================================================

def display():

    glClear(GL_COLOR_BUFFER_BIT)

    glLoadIdentity()


    # ========================================================
    # HEADER
    # ========================================================

    glColor3f(1, 1, 1)

    draw_text(
        390,
        770,
        "2D TRANSFORMATIONS",
        GLUT_BITMAP_HELVETICA_18
    )

    draw_text(
        345,
        745,
        "Using Homogeneous Coordinates"
    )


    # ========================================================
    # ORIGINAL TRIANGLE INFORMATION
    # ========================================================

    glColor3f(0.7, 0.7, 0.7)

    draw_text(
        30,
        715,
        "Original Triangle: (0,0), (100,0), (50,100)"
    )

    draw_text(
        850,
        715,
        "Original = Gray"
    )


    # ========================================================
    # PANEL DIMENSIONS
    # ========================================================

    panel_width = 220
    panel_height = 600

    gap = 20

    start_x = 30
    start_y = 90


    # ========================================================
    # 1. TRANSLATION
    # ========================================================

    T = translation(100, 50)

    draw_panel(
        start_x,
        start_y,
        panel_width,
        panel_height,

        "1. TRANSLATION",

        "tx = 100,  ty = 50",

        T,

        (1, 0.2, 0.2)
    )


    # ========================================================
    # 2. ROTATION
    # ========================================================

    R = rotation(45)

    draw_panel(
        start_x + (panel_width + gap),
        start_y,
        panel_width,
        panel_height,

        "2. ROTATION",

        "theta = 45 degrees",

        R,

        (0.2, 1, 0.2)
    )


    # ========================================================
    # 3. SCALING
    # ========================================================

    S = scaling(0.5, 0.5)

    draw_panel(
        start_x + 2 * (panel_width + gap),
        start_y,
        panel_width,
        panel_height,

        "3. SCALING",

        "sx = 0.5,  sy = 0.5",

        S,

        (0.2, 0.5, 1)
    )


    # ========================================================
    # 4. REFLECTION
    # ========================================================

    Ref = reflection_x()

    draw_panel(
        start_x + 3 * (panel_width + gap),
        start_y,
        panel_width,
        panel_height,

        "4. REFLECTION",

        "About X-axis",

        Ref,

        (1, 1, 0.1)
    )


    # ========================================================
    # 5. SHEARING
    # ========================================================

    Sh = shearing(0.5, 0)

    draw_panel(
        start_x + 4 * (panel_width + gap),
        start_y,
        panel_width,
        panel_height,

        "5. SHEARING",

        "shx = 0.5,  shy = 0",

        Sh,

        (1, 0.1, 1)
    )


    # ========================================================
    # FOOTER
    # ========================================================

    glColor3f(0.2, 0.8, 1)

    draw_text(
        30,
        50,
        "Homogeneous Point: P = [ x  y  1 ]T"
    )

    draw_text(
        400,
        50,
        "Transformed Point: P' = T x P"
    )

    draw_text(
        800,
        50,
        "Gray = Original"
    )

    glFlush()


# ============================================================
# INITIALIZATION
# ============================================================

def init():

    glClearColor(0, 0, 0, 1)

    glMatrixMode(GL_PROJECTION)

    glLoadIdentity()

    gluOrtho2D(
        0,
        1230,
        0,
        800
    )

    glMatrixMode(GL_MODELVIEW)

    glLoadIdentity()


# ============================================================
# MAIN
# ============================================================

def main():

    glutInit()

    glutInitDisplayMode(
        GLUT_SINGLE | GLUT_RGB
    )

    glutInitWindowSize(
        1230,
        800
    )

    glutInitWindowPosition(
        50,
        50
    )

    glutCreateWindow(
        b"2D Transformations using Homogeneous Coordinates"
    )

    init()

    glutDisplayFunc(display)

    glutMainLoop()


if __name__ == "__main__":
    main()