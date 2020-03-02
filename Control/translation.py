import math

from s import *

# Lengths in mm
board_width = 220
board_depth = 220
arm_to_board = 210

STUD_LENGTH = 7.985

angled_beam_angle = math.pi - math.acos(3 / 5)
elbow_down_length = 4 * STUD_LENGTH
elbow_across_length = 23 * STUD_LENGTH
elbow_length = math.sqrt(elbow_across_length ** 2 + elbow_down_length ** 2
                         - 2 * elbow_across_length * elbow_down_length * math.cos(angled_beam_angle + math.pi / 2))
elbow_angle = math.acos(
    (elbow_down_length ** 2 + elbow_length ** 2 - elbow_across_length ** 2) / (2 * elbow_down_length * elbow_length))

shoulder_length = 25 * STUD_LENGTH

horizontal_arm_offset = 0 * STUD_LENGTH
base_height_offset = 6 * STUD_LENGTH
claw_height_offset = 2 * STUD_LENGTH
claw_length_offset = 11 * STUD_LENGTH

# Original coordinate system uses corner of board close right to arm as (0,0,0)
# Define y to be direction from arm to board
# x is to right
# theta=0 points directly at the center of the board
# theta progresses counterclockwise

'''
    Shift origin from corner of board to base of arm
'''


def board_to_arm_centric(x, y, z):
    return board_width / 2 - x, y + arm_to_board, z


'''
    Find the angle and distance from the base
'''


def arm_centric_to_arm_cylindrical(x, y, z):
    theta = math.atan2(y, x)
    r = math.sqrt(x ** 2 + y ** 2)

    return theta - math.pi / 2, r, z


'''
    Abstract away the height of the base and dimensions of claw
'''


def offset_arm_plane(r, z):
    z = z - base_height_offset
    z = z + claw_height_offset
    r = r - claw_length_offset
    return r, z


'''
    Find overall angle and length the arm needs to be at from pivot point
    This views the arm from the side (looking at the arm plane) and determines
    the polar coordinates of the target point
'''


def arm_coordinates_to_angle(r, z):
    r_sphere = math.sqrt(r ** 2 + z ** 2)
    phi = math.atan2(z, r)
    return r_sphere, phi


'''
    Find angles of shoulder and elbow beams in order to satisfy specified distance and angle
'''


# Angle 0 is pointing straight forward at the front of the arm
def arm_angle_to_beam_angles(r, phi):
    # alpha = a_shoulder-phi
    alpha = math.acos((shoulder_length ** 2 + r ** 2 - elbow_length ** 2) /
                      (2 * shoulder_length * r))
    a_shoulder = alpha + phi

    beta = math.acos((shoulder_length ** 2 + elbow_length ** 2 - r ** 2) /
                     (2 * shoulder_length * elbow_length))

    a_elbow = a_shoulder + beta - elbow_angle
    return a_shoulder, a_elbow


'''
    Combine all transformations to convert from board centric coordinates to the angles of the components of the arm
    Motor gearing is handled in communications layer 
'''


def transform(x, y, z):
    # Calculate cylindrical coordinates
    theta, r, z = arm_centric_to_arm_cylindrical(*board_to_arm_centric(x, y, z))

    # Adjustments made to counteract errors in the hardware from the LEGO axles bending
    # calculated by collecting measurements, running a linear regression, then hand tuning
    z_adj = z + ((0.00047 * r ** 2) + (0.00 * r) - 10)

    r_adj = -276 + (2.61 * r) + (-2.26e-3 * r ** 2)

    theta_adj = theta * 1.07

    # Calculate shoulder and elbow angles based on adjusted values
    shoulder, elbow = arm_angle_to_beam_angles(*arm_coordinates_to_angle(*offset_arm_plane(r_adj, z_adj)))

    return theta_adj, shoulder, elbow


'''
    Connects to the arm and moves to coordinates specified on the command line
    Used for testing purposes only
'''


def test_transformation():
    s = Server(HOST, PORT)

    # Takes command line input for x, y, z coordinates
    angles = input("Enter position as x,y,z or q to quit: ")
    while angles != 'q':
        l = angles.split(",")
        x = int(l[0])
        y = int(l[1])
        z = int(l[2])
        theta, shoulder, elbow = transform(x, y, z)
        s.send_pos('A', int(21 * (math.degrees(theta) + 180)))
        s.send_pos('C', int(5 * math.degrees(elbow)))
        s.send_pos('B', int(66.68 * math.degrees(shoulder)))

        angles = input("Enter position as x,y,z or q to quit: ")

    # Returns arm to initial position
    s.send_pos('A', 180 * 21)
    s.send_pos('B', int(66.68 * 83))
    s.send_pos('C', 5 * 83)
    s.send_pos('D', 0)


if __name__ == "__main__":
    test_transformation()
