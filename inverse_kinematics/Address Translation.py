# Original code from https://github.com/microspace/Uarm-IK

# Shoulder: alpha
# Elbow: beta
# Base: theta
import math
from math import sqrt, acos, asin, cos
import matplotlib.pyplot as plt

PLOT_TESTS = True

STUD_LENGTH = 7.985

Angled_liftarm_angle = acos(3 / 5)
L1 = 26 * STUD_LENGTH  # Shoulder length
Elbow_down_length = 4 * STUD_LENGTH
Elbow_across_length = 23 * STUD_LENGTH
L2 = sqrt(Elbow_across_length ** 2 + Elbow_down_length ** 2
          - 2 * Elbow_across_length * Elbow_down_length * cos(Angled_liftarm_angle + math.pi / 2))


def translate(x, y, z):
    c_r = sqrt(x * x + y * y)  # Cylindrical coordinates r
    theta = acos(x / c_r)
    s_r = sqrt(x * x + y * y + z * z)  # Spherical coordinates r
    elbow = math.pi - acos(max(-1.0,min(1.0,((L1 * L1 + L2 * L2 - s_r * s_r) / (2 * L1 * L2)))))
    shoulder = (acos(max(-1.0,min(1.0,(L1 * L1 + s_r * s_r - L2 * L2) / (2 * L1 * s_r) + asin(z / s_r)))))
    if (L1 * L1 + s_r * s_r - L2 * L2) / (2 * L1 * s_r) + asin(z / s_r) > 1.1:
        print(x,y,z,(L1 * L1 + s_r * s_r - L2 * L2) / (2 * L1 * s_r) + asin(z / s_r))
    elbow -= shoulder

    # Convert to degrees
    theta = theta * 180 / math.pi
    elbow = elbow * 180 / math.pi
    shoulder = shoulder * 180 / math.pi

    return theta, elbow, shoulder


def test_theta():
    circle = [(10 * cos(a * math.pi / 180), 10 * math.sin(a * math.pi / 180), 0) for a in range(180)]
    for angle,(x,y,z) in enumerate(circle):
        assert(math.isclose(translate(x,y,z)[0],angle))
    if PLOT_TESTS:
        plot_translation(circle)

def plot_x():
    points = [(a,10,0) for a in range(-50,50)]
    plot_translation(points)

def plot_y():
    points = [(0, a, 0) for a in range(10, 50)]
    plot_translation(points)

def plot_z():
    points = [(0, 30, a) for a in range(0, 50)]
    plot_translation(points)


def plot_translation(points):
    (thetas, elbows, shoulders) = zip(*[translate(*p) for p in points])

    plt.plot(thetas, label='theta')
    plt.plot(elbows, label='elbow')
    plt.plot(shoulders, label='shoulder')

    plt.legend()
    plt.show()
if __name__ == "__main__":
    # test_theta()
    plot_z()
    print(translate(10,00,0))