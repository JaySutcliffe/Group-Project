import math
import inverse_kinematics.translation as tr
import matplotlib.pyplot as plt

def test_theta():
    circle = [(100 * math.cos(a * math.pi / 180), 100 * math.sin(a * math.pi / 180), 0) for a in range(360)]
    #for angle,(x,y,z) in enumerate(circle):
    #    assert(math.isclose(tr.transform_from_arm_centric(x,y,z)[0],angle))
    plot_translation(circle,relative=True)

def plot_x():
    points = [(a,0,0) for a in range(0,220)]
    plot_translation(points)

def plot_y():
    points = [(0, a, 0) for a in range(0, 220)]
    plot_translation(points)

def plot_z():
    points = [(0, 50, a) for a in range(0, 50)]
    plot_translation(points)


def plot_translation(points,relative=False):
    if relative:
        (thetas, elbows, shoulders) = zip(*[tr.relative_transform(*p) for p in points])
    else:
        (thetas, elbows, shoulders) = zip(*[tr.transform(*p) for p in points])

    plt.plot(thetas, label='theta')
    plt.plot(elbows, label='elbow')
    plt.plot(shoulders, label='shoulder')

    plt.legend()
    plt.show()

test_theta()
plot_x()
plot_y()
plot_z()