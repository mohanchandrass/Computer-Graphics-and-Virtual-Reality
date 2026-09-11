from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math


# ============================================================
# EXPERIMENT 4
# COMPOSITE TRANSFORMATIONS USING MATRIX REPRESENTATION
# ============================================================


# ------------------------------------------------------------
# ORIGINAL TRIANGLE
# Homogeneous coordinates: [x, y, 1]
# ------------------------------------------------------------

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

    result = [
        [0 for _ in range(cols)]
        for _ in range(rows)
    ]

    for i in range(rows):
        for j in range(cols):
            for k in range(common):
                result[i][j] += A[i][k] * B[k][j]

    return result


# ============================================================
# TRANSFORM A POINT
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
# TRANSFORM COMPLETE TRIANGLE
# ============================================================

def transform_triangle(matrix):

    result = []

    for point in triangle:
        result.append(
            transform_point(matrix, point)
        )

    return result


# ============================================================
# TRANSLATION MATRIX
# ============================================================

def translation(tx, ty):

    return [
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ]


# ============================================================
# ROTATION MATRIX
# ============================================================

def rotation(angle):

    theta = math.radians(angle)

    c = math.cos(theta)
    s = math.sin(theta)

    return [
        [c, -s, 0],
        [s,  c, 0],
        [0,  0, 1]
    ]


# ============================================================
# SCALING MATRIX
# ============================================================

def scaling(sx, sy):

    return [
        [sx, 0,  0],
        [0,  sy, 0],
        [0,  0,  1]
    ]


# ============================================================
# REFLECTION MATRIX
# ============================================================

def reflection_x():

    return [
        [1,  0, 0],
        [0, -1, 0],
        [0,  0, 1]
    ]


# ============================================================
# SHEARING MATRIX
# ============================================================

def shearing(shx, shy):

    return [
        [1,   shx, 0],
        [shy, 1,   0],
        [0,   0,   1]
    ]


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(x, y, text, font=GLUT_BITMAP_9_BY_15):

    glRasterPos2f(x, y)

    for char in text:
        glutBitmapCharacter(
            font,
            ord(char)
        )


# ============================================================
# DRAW GRID
# ============================================================

def draw_grid():

    glColor3f(
        0.12,
        0.12,
        0.12
    )

    glBegin(GL_LINES)

    for x in range(-200, 301, 50):

        glVertex2f(x, -150)
        glVertex2f(x, 250)

    for y in range(-150, 251, 50):

        glVertex2f(-200, y)
        glVertex2f(300, y)

    glEnd()


# ============================================================
# DRAW AXES
# ============================================================

def draw_axes():

    glColor3f(
        0.4,
        0.4,
        0.4
    )

    glBegin(GL_LINES)

    # X axis
    glVertex2f(-200, 0)
    glVertex2f(300, 0)

    # Y axis
    glVertex2f(0, -150)
    glVertex2f(0, 250)

    glEnd()


# ============================================================
# DRAW ORIGINAL TRIANGLE
# ============================================================

def draw_original():

    glColor3f(
        0.7,
        0.7,
        0.7
    )

    glLineWidth(2)

    glBegin(GL_LINE_LOOP)

    for x, y, _ in triangle:
        glVertex2f(x, y)

    glEnd()


# ============================================================
# DRAW TRANSFORMED TRIANGLE
# ============================================================

def draw_triangle(points, color):

    glColor3f(
        color[0],
        color[1],
        color[2]
    )

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
# DRAW MATRIX
# ============================================================

def draw_matrix(x, y, matrix):

    glColor3f(
        1,
        1,
        1
    )

    # First row
    draw_text(
        x,
        y,
        "[ "
        + f"{matrix[0][0]:6.2f}"
        + "  "
        + f"{matrix[0][1]:6.2f}"
        + "  "
        + f"{matrix[0][2]:6.2f}"
        + " ]"
    )

    # Second row
    draw_text(
        x,
        y - 20,
        "[ "
        + f"{matrix[1][0]:6.2f}"
        + "  "
        + f"{matrix[1][1]:6.2f}"
        + "  "
        + f"{matrix[1][2]:6.2f}"
        + " ]"
    )

    # Third row
    draw_text(
        x,
        y - 40,
        "[ "
        + f"{matrix[2][0]:6.2f}"
        + "  "
        + f"{matrix[2][1]:6.2f}"
        + "  "
        + f"{matrix[2][2]:6.2f}"
        + " ]"
    )


# ============================================================
# DISPLAY
# ============================================================

def display():

    glClear(
        GL_COLOR_BUFFER_BIT
    )

    glLoadIdentity()


    # ========================================================
    # COMPOSITE TRANSFORMATION
    #
    # Original
    #    ↓
    # Scaling
    #    ↓
    # Rotation
    #    ↓
    # Translation
    #    ↓
    # Final
    #
    # P' = T × R × S × P
    # ========================================================

    S = scaling(
        1.5,
        1.5
    )

    R = rotation(
        45
    )

    T = translation(
        250,
        120
    )


    # Composite matrix
    #
    # IMPORTANT:
    # Rightmost transformation is performed first.
    #
    # S → R → T
    #
    composite = matrix_multiply(
        T,
        matrix_multiply(
            R,
            S
        )
    )


    # Final transformed triangle
    final_triangle = transform_triangle(
        composite
    )


    # ========================================================
    # HEADER
    # ========================================================

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        460,
        760,
        "COMPOSITE 2D TRANSFORMATIONS",
        GLUT_BITMAP_HELVETICA_18
    )

    draw_text(
        475,
        735,
        "Using Matrix Representation"
    )


    # ========================================================
    # TRANSFORMATION SEQUENCE
    # ========================================================

    glColor3f(
        0.2,
        0.9,
        1
    )

    draw_text(
        40,
        695,
        "Transformation Sequence:"
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        250,
        695,
        "Original  ->  Scaling  ->  Rotation  ->  Translation  ->  Final"
    )


    # ========================================================
    # PARAMETERS
    # ========================================================

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        40,
        665,
        "Scaling: sx = 1.5, sy = 1.5"
    )

    draw_text(
        300,
        665,
        "Rotation: theta = 45 degrees"
    )

    draw_text(
        600,
        665,
        "Translation: tx = 250, ty = 120"
    )


    # ========================================================
    # LEFT SIDE - TRANSFORMATION VISUALIZATION
    # ========================================================

    # Border
    glColor3f(
        0.5,
        0.5,
        0.5
    )

    glLineWidth(1)

    glBegin(GL_LINE_LOOP)

    glVertex2f(30, 100)
    glVertex2f(650, 100)
    glVertex2f(650, 630)
    glVertex2f(30, 630)

    glEnd()


    # Move drawing area
    glPushMatrix()

    glTranslatef(
        300,
        350,
        0
    )

    draw_grid()
    draw_axes()

    # Original
    draw_original()

    # Final
    draw_triangle(
        final_triangle,
        (1, 0.2, 0.2)
    )

    glPopMatrix()


    # ========================================================
    # LABELS
    # ========================================================

    glColor3f(
        0.7,
        0.7,
        0.7
    )

    draw_text(
        70,
        570,
        "GRAY = ORIGINAL"
    )

    glColor3f(
        1,
        0.2,
        0.2
    )

    draw_text(
        70,
        545,
        "RED = FINAL COMPOSITE RESULT"
    )


    # ========================================================
    # RIGHT SIDE - MATRICES
    # ========================================================

    glColor3f(
        0.2,
        0.9,
        1
    )

    draw_text(
        700,
        620,
        "INDIVIDUAL MATRICES",
        GLUT_BITMAP_HELVETICA_18
    )


    # --------------------------------------------------------
    # SCALING MATRIX
    # --------------------------------------------------------

    glColor3f(
        0.2,
        0.5,
        1
    )

    draw_text(
        700,
        580,
        "Scaling Matrix S:"
    )

    draw_matrix(
        700,
        550,
        S
    )


    # --------------------------------------------------------
    # ROTATION MATRIX
    # --------------------------------------------------------

    glColor3f(
        0.2,
        1,
        0.2
    )

    draw_text(
        700,
        490,
        "Rotation Matrix R:"
    )

    draw_matrix(
        700,
        460,
        R
    )


    # --------------------------------------------------------
    # TRANSLATION MATRIX
    # --------------------------------------------------------

    glColor3f(
        1,
        0.7,
        0.1
    )

    draw_text(
        700,
        400,
        "Translation Matrix T:"
    )

    draw_matrix(
        700,
        370,
        T
    )


    # ========================================================
    # COMPOSITE MATRIX
    # ========================================================

    glColor3f(
        1,
        0.2,
        0.2
    )

    draw_text(
        700,
        300,
        "COMPOSITE MATRIX",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        700,
        270,
        "M = T x R x S"
    )

    draw_matrix(
        700,
        235,
        composite
    )


    # ========================================================
    # FORMULA
    # ========================================================

    glColor3f(
        0.2,
        0.9,
        1
    )

    draw_text(
        700,
        155,
        "Final Transformation:"
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        700,
        125,
        "P' = M x P"
    )

    draw_text(
        700,
        100,
        "P' = T x R x S x P"
    )


    # ========================================================
    # FOOTER
    # ========================================================

    glColor3f(
        0.5,
        0.5,
        0.5
    )

    draw_text(
        40,
        50,
        "Note: Matrix multiplication is NOT commutative. Order of transformations matters."
    )

    glFlush()


# ============================================================
# INITIALIZATION
# ============================================================

def init():

    glClearColor(
        0,
        0,
        0,
        1
    )

    glMatrixMode(
        GL_PROJECTION
    )

    glLoadIdentity()

    gluOrtho2D(
        0,
        1100,
        0,
        800
    )

    glMatrixMode(
        GL_MODELVIEW
    )

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
        1100,
        800
    )

    glutInitWindowPosition(
        50,
        50
    )

    glutCreateWindow(
        b"Composite Transformations using Matrix Representation"
    )

    init()

    glutDisplayFunc(
        display
    )

    glutMainLoop()


if __name__ == "__main__":
    main()