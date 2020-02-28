import math
import inverse_kinematics.translation as tr
import matplotlib.pyplot as plt
import numpy as np

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

def find_position(shoulder,elbow):
    minv = 1000
    mincoord = (0,0,0)
    xs = [110]
    ys = [y/10 for y in range(120,140,1)]
    zs = [z/10 for z in range(700,720,1)]
    for x in xs:
        for z in zs:
            for y in ys:
                try:
                    t,s_a,e_a = tr.transform(x,y,z)
                    v = abs(s_a-shoulder) + abs(e_a-elbow)
                    if(v<minv):
                        mincoord = (x,y,z)
                        minv = v
                except:
                    print()

    return minv,mincoord

print(find_position(math.pi/2,math.pi/2))
#a,b,c = tr.transform(110, 13, 71.1)


#print(tr.relative_transform(110,200,10))
#print(tr.transform(0,0,10))
#print(tr.transform(220,0,10))
#test_theta()
#plot_x()
#plot_y()
#plot_z()