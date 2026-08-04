#Implement DDA and Bresenham line drawing algorithms.

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


# -----------------------------
# Plot a single pixel
# -----------------------------
def plot(x, y):
    glVertex2i(int(round(x)), int(round(y)))


# -----------------------------
# DDA Line Drawing Algorithm
# -----------------------------
def dda(x1, y1, x2, y2):
    dx = x2 - x1
    dy = y2 - y1

    steps = max(abs(dx), abs(dy))

    if steps == 0:
        plot(x1, y1)
        return

    x_inc = dx / steps
    y_inc = dy / steps

    x = x1
    y = y1

    for _ in range(int(steps) + 1):
        plot(x, y)
        x += x_inc
        y += y_inc


# -----------------------------
# Bresenham Line Drawing Algorithm
# -----------------------------
def bresenham(x1, y1, x2, y2):
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)

    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1

    err = dx - dy

    while True:
        plot(x1, y1)

        if x1 == x2 and y1 == y2:
            break

        e2 = 2 * err

        if e2 > -dy:
            err -= dy
            x1 += sx

        if e2 < dx:
            err += dx
            y1 += sy


# -----------------------------
# Display Function
# -----------------------------
def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glPointSize(3)

    glBegin(GL_POINTS)

    # DDA Line (Red)
    glColor3f(1, 0, 0)
    dda(50, 100, 500, 450)

    # Bresenham Line (Green)
    glColor3f(0, 1, 0)
    bresenham(50, 500, 500, 150)

    glEnd()

    glFlush()


# -----------------------------
# Initialize OpenGL
# -----------------------------
def init():
    glClearColor(0, 0, 0, 1)

    gluOrtho2D(0, WINDOW_WIDTH, 0, WINDOW_HEIGHT)


# -----------------------------
# Main Function
# -----------------------------
def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_WIDTH, WINDOW_HEIGHT)
    glutCreateWindow(b"DDA and Bresenham Line Drawing")

    init()

    glutDisplayFunc(display)

    glutMainLoop()


if __name__ == "__main__":
    main()