#Implement the Midpoint Circle Drawing Algorithm

from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

WIDTH = 600
HEIGHT = 600


# Plot a point
def plot(x, y):
    glVertex2i(x, y)


# Plot all 8 symmetric points
def draw_circle_points(xc, yc, x, y):
    plot(xc + x, yc + y)
    plot(xc - x, yc + y)
    plot(xc + x, yc - y)
    plot(xc - x, yc - y)
    plot(xc + y, yc + x)
    plot(xc - y, yc + x)
    plot(xc + y, yc - x)
    plot(xc - y, yc - x)


# Midpoint Circle Algorithm
def midpoint_circle(xc, yc, r):
    x = 0
    y = r
    p = 1 - r

    draw_circle_points(xc, yc, x, y)

    while x < y:
        x += 1

        if p < 0:
            p += 2 * x + 1
        else:
            y -= 1
            p += 2 * (x - y) + 1

        draw_circle_points(xc, yc, x, y)


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    glPointSize(3)
    glColor3f(0, 1, 0)

    glBegin(GL_POINTS)
    midpoint_circle(300, 300, 150)
    glEnd()

    glFlush()


def init():
    glClearColor(0, 0, 0, 1)
    gluOrtho2D(0, WIDTH, 0, HEIGHT)


def main():
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
    glutInitWindowSize(WIDTH, HEIGHT)
    glutCreateWindow(b"Midpoint Circle Drawing Algorithm")

    init()
    glutDisplayFunc(display)

    glutMainLoop()


if __name__ == "__main__":
    main()