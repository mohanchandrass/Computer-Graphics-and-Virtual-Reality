from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *


# ============================================================
# EXPERIMENT 5
# COHEN-SUTHERLAND LINE CLIPPING ALGORITHM
# ============================================================


# ------------------------------------------------------------
# CLIPPING WINDOW
# ------------------------------------------------------------

X_MIN = 100
X_MAX = 500
Y_MIN = 100
Y_MAX = 400


# ------------------------------------------------------------
# REGION CODES
# ------------------------------------------------------------

INSIDE = 0
LEFT = 1
RIGHT = 2
BOTTOM = 4
TOP = 8


# ============================================================
# COMPUTE REGION CODE
# ============================================================

def compute_code(x, y):

    code = INSIDE

    if x < X_MIN:
        code |= LEFT

    elif x > X_MAX:
        code |= RIGHT

    if y < Y_MIN:
        code |= BOTTOM

    elif y > Y_MAX:
        code |= TOP

    return code


# ============================================================
# COHEN-SUTHERLAND LINE CLIPPING
# ============================================================

def cohen_sutherland_clip(x1, y1, x2, y2):

    code1 = compute_code(x1, y1)
    code2 = compute_code(x2, y2)

    while True:

        # ----------------------------------------------------
        # Completely inside
        # ----------------------------------------------------

        if code1 == 0 and code2 == 0:

            return True, x1, y1, x2, y2


        # ----------------------------------------------------
        # Completely outside
        # ----------------------------------------------------

        if (code1 & code2) != 0:

            return False, None, None, None, None


        # ----------------------------------------------------
        # Select outside point
        # ----------------------------------------------------

        if code1 != 0:
            code_out = code1
        else:
            code_out = code2


        # ----------------------------------------------------
        # TOP
        # ----------------------------------------------------

        if code_out & TOP:

            if y2 == y1:
                return False, None, None, None, None

            x = x1 + (x2 - x1) * \
                (Y_MAX - y1) / (y2 - y1)

            y = Y_MAX


        # ----------------------------------------------------
        # BOTTOM
        # ----------------------------------------------------

        elif code_out & BOTTOM:

            if y2 == y1:
                return False, None, None, None, None

            x = x1 + (x2 - x1) * \
                (Y_MIN - y1) / (y2 - y1)

            y = Y_MIN


        # ----------------------------------------------------
        # RIGHT
        # ----------------------------------------------------

        elif code_out & RIGHT:

            if x2 == x1:
                return False, None, None, None, None

            y = y1 + (y2 - y1) * \
                (X_MAX - x1) / (x2 - x1)

            x = X_MAX


        # ----------------------------------------------------
        # LEFT
        # ----------------------------------------------------

        else:

            if x2 == x1:
                return False, None, None, None, None

            y = y1 + (y2 - y1) * \
                (X_MIN - x1) / (x2 - x1)

            x = X_MIN


        # ----------------------------------------------------
        # Replace outside endpoint
        # ----------------------------------------------------

        if code_out == code1:

            x1 = x
            y1 = y

            code1 = compute_code(x1, y1)

        else:

            x2 = x
            y2 = y

            code2 = compute_code(x2, y2)


# ============================================================
# DRAW TEXT
# ============================================================

def draw_text(x, y, text, font=GLUT_BITMAP_9_BY_15):

    glRasterPos2f(x, y)

    for character in text:

        glutBitmapCharacter(
            font,
            ord(character)
        )


# ============================================================
# DRAW LINE
# ============================================================

def draw_line(
    x1,
    y1,
    x2,
    y2,
    color,
    width=2
):

    glColor3f(*color)

    glLineWidth(width)

    glBegin(GL_LINES)

    glVertex2f(x1, y1)
    glVertex2f(x2, y2)

    glEnd()


# ============================================================
# DRAW POINT
# ============================================================

def draw_point(
    x,
    y,
    color=(1, 1, 1)
):

    glColor3f(*color)

    glPointSize(6)

    glBegin(GL_POINTS)

    glVertex2f(x, y)

    glEnd()


# ============================================================
# DRAW CLIPPING WINDOW
# ============================================================

def draw_window(offset_x):

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    glLineWidth(3)

    glBegin(GL_LINE_LOOP)

    glVertex2f(
        offset_x + X_MIN,
        Y_MIN
    )

    glVertex2f(
        offset_x + X_MAX,
        Y_MIN
    )

    glVertex2f(
        offset_x + X_MAX,
        Y_MAX
    )

    glVertex2f(
        offset_x + X_MIN,
        Y_MAX
    )

    glEnd()


# ============================================================
# TEST LINES
# ============================================================

lines = [

    # Completely inside
    (180, 150, 420, 350),

    # Enters from LEFT
    (20, 120, 350, 300),

    # Enters from TOP
    (300, 500, 450, 250),

    # Completely outside TOP-LEFT
    (20, 450, 100, 520),

    # Completely outside RIGHT
    (550, 150, 700, 300)
]


# ============================================================
# BEFORE CLIPPING
# ============================================================

def draw_before():

    # --------------------------------------------------------
    # PANEL POSITION
    # --------------------------------------------------------

    offset_x = 50


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    glColor3f(1, 1, 1)

    draw_text(
        210,
        790,
        "BEFORE CLIPPING",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        0.55,
        0.55,
        0.55
    )

    draw_text(
        215,
        765,
        "Original Lines"
    )


    # --------------------------------------------------------
    # CLIPPING WINDOW
    # --------------------------------------------------------

    draw_window(offset_x)


    # --------------------------------------------------------
    # WINDOW LABEL
    # --------------------------------------------------------

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        offset_x + 100,
        425,
        "CLIPPING WINDOW"
    )


    # --------------------------------------------------------
    # DRAW ORIGINAL LINES
    # --------------------------------------------------------

    for x1, y1, x2, y2 in lines:

        draw_line(
            offset_x + x1,
            y1,
            offset_x + x2,
            y2,
            (0.55, 0.55, 0.55),
            2
        )

        draw_point(
            offset_x + x1,
            y1
        )

        draw_point(
            offset_x + x2,
            y2
        )


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        110,
        70,
        "All original lines are shown"
    )

    draw_text(
        110,
        45,
        "before applying clipping."
    )


# ============================================================
# AFTER CLIPPING
# ============================================================

def draw_after():

    # --------------------------------------------------------
    # PANEL POSITION
    # --------------------------------------------------------

    offset_x = 800


    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        960,
        790,
        "AFTER CLIPPING",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        0.55,
        0.55,
        0.55
    )

    draw_text(
        945,
        765,
        "Cohen-Sutherland Result"
    )


    # --------------------------------------------------------
    # CLIPPING WINDOW
    # --------------------------------------------------------

    draw_window(offset_x)


    # --------------------------------------------------------
    # WINDOW LABEL
    # --------------------------------------------------------

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        offset_x + 100,
        425,
        "CLIPPING WINDOW"
    )


    # --------------------------------------------------------
    # CLIPPED LINES ONLY
    # --------------------------------------------------------

    for x1, y1, x2, y2 in lines:

        accepted, cx1, cy1, cx2, cy2 = \
            cohen_sutherland_clip(
                x1,
                y1,
                x2,
                y2
            )

        if accepted:

            draw_line(
                offset_x + cx1,
                cy1,
                offset_x + cx2,
                cy2,
                (0.1, 1.0, 0.2),
                5
            )

            draw_point(
                offset_x + cx1,
                cy1,
                (0.1, 1.0, 0.2)
            )

            draw_point(
                offset_x + cx2,
                cy2,
                (0.1, 1.0, 0.2)
            )


    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    glColor3f(
        0.1,
        1.0,
        0.2
    )

    draw_text(
        860,
        70,
        "Only accepted / clipped"
    )

    draw_text(
        860,
        45,
        "portions are displayed."
    )


# ============================================================
# INFORMATION PANEL
# ============================================================

def draw_information():

    # ========================================================
    # VERTICAL SEPARATOR
    # ========================================================

    glColor3f(
        0.25,
        0.25,
        0.25
    )

    glLineWidth(2)

    glBegin(GL_LINES)

    glVertex2f(
        1370,
        40
    )

    glVertex2f(
        1370,
        800
    )

    glEnd()


    # ========================================================
    # REGION CODES
    # ========================================================

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        1400,
        700,
        "REGION CODES",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        1400,
        660,
        "TOP       = 1000"
    )

    draw_text(
        1400,
        630,
        "BOTTOM    = 0100"
    )

    draw_text(
        1400,
        600,
        "RIGHT     = 0010"
    )

    draw_text(
        1400,
        570,
        "LEFT      = 0001"
    )

    draw_text(
        1400,
        530,
        "INSIDE    = 0000"
    )


    # ========================================================
    # ALGORITHM
    # ========================================================

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        1400,
        450,
        "ALGORITHM",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        1400,
        410,
        "1. Compute region codes"
    )

    draw_text(
        1400,
        380,
        "2. Check both endpoints"
    )

    draw_text(
        1400,
        350,
        "3. Accept if both = 0000"
    )

    draw_text(
        1400,
        320,
        "4. Reject if AND != 0"
    )

    draw_text(
        1400,
        290,
        "5. Find intersection"
    )

    draw_text(
        1400,
        260,
        "6. Repeat until accepted"
    )


    # ========================================================
    # RESULT
    # ========================================================

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        1400,
        180,
        "RESULT",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        1400,
        145,
        "Inside  -> Accepted"
    )

    draw_text(
        1400,
        115,
        "Crossing -> Clipped"
    )

    draw_text(
        1400,
        85,
        "Outside -> Rejected"
    )


# ============================================================
# LEGEND
# ============================================================

def draw_legend():

    glColor3f(
        0.1,
        0.8,
        1.0
    )

    draw_text(
        50,
        850,
        "LEGEND",
        GLUT_BITMAP_HELVETICA_18
    )


    # --------------------------------------------------------
    # ORIGINAL
    # --------------------------------------------------------

    draw_line(
        145,
        855,
        205,
        855,
        (0.55, 0.55, 0.55),
        3
    )

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        220,
        850,
        "Original Line"
    )


    # --------------------------------------------------------
    # CLIPPED
    # --------------------------------------------------------

    draw_line(
        380,
        855,
        440,
        855,
        (0.1, 1.0, 0.2),
        5
    )

    glColor3f(
        0.1,
        1.0,
        0.2
    )

    draw_text(
        455,
        850,
        "Accepted / Clipped"
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
    # MAIN TITLE
    # ========================================================

    glColor3f(
        1,
        1,
        1
    )

    draw_text(
        600,
        875,
        "COHEN-SUTHERLAND LINE CLIPPING",
        GLUT_BITMAP_HELVETICA_18
    )

    glColor3f(
        0.65,
        0.65,
        0.65
    )

    draw_text(
        675,
        845,
        "Line Clipping Algorithm"
    )


    # ========================================================
    # PANELS
    # ========================================================

    draw_before()

    draw_after()

    draw_information()


    # ========================================================
    # LEGEND
    # ========================================================

    draw_legend()


    # ========================================================
    # FLUSH
    # ========================================================

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
        1600,
        0,
        900
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
        1600,
        900
    )

    glutInitWindowPosition(
        20,
        20
    )

    glutCreateWindow(
        b"Cohen-Sutherland Line Clipping"
    )

    init()

    glutDisplayFunc(
        display
    )

    glutMainLoop()


if __name__ == "__main__":
    main()